#!/usr/bin/env python
# Filename: util.py

'''
util
@author: Andrew Philpot
@version 0.79

collection of misc utils
Usage: python util.py
Options:
\t-h, --help:\tprint help to STDOUT and quit
\t-v, --verbose:\tverbose output
'''

import sys
import inspect
import types
import getopt
import fileinput
import tempfile
import datetime
import time
import io
import re
import html.entities
import os
import socket
from itertools import zip_longest
import math
import hashlib
import codecs
from subprocess import check_output, CalledProcessError
import argparse
import cgi
from contextlib import contextmanager
import multiprocessing as mp
import subprocess
import traceback
import requests
import collections

VERSION = '0.79'
__version__ = VERSION
REVISION = '$Revision: 25780 $'.replace('$','')

# defaults
VERBOSE = True

# util section echo (= trace)
# adapted from http://wordaligned.org/articles/echo

def format_arg_value(arg_val):
    """ Return a string representing a (name, value) pair.
    
    >>> format_arg_value(('x', (1, 2, 3)))
    'x=(1, 2, 3)'
    """
    arg, val = arg_val
    return "%s=%r" % (arg, val)
    
def echo(fn, write=sys.stdout.write):
    """ Echo calls to a function.
    
    Returns a decorated version of the input function which "echoes" calls
    made to it by writing out the function's name and the arguments it was
    called with.
    """
    import functools
    # Unpack function's arg count, arg names, arg defaults
    code = fn.__code__
    argcount = code.co_argcount
    argnames = code.co_varnames[:argcount]
    fn_defaults = fn.__defaults__ or list()
    argdefs = dict(list(zip(argnames[-len(fn_defaults):], fn_defaults)))
    name = fn.__name__
    
    @functools.wraps(fn)
    def wrapped(*v, **k):
        # Collect function arguments by chaining together positional,
        # defaulted, extra positional and keyword arguments.
        positional = list(map(format_arg_value, list(zip(argnames, v))))
        defaulted = [format_arg_value((a, argdefs[a]))
                     for a in argnames[len(v):] if a not in k]
        nameless = list(map(repr, v[argcount:]))
        keyword = list(map(format_arg_value, list(k.items())))
        args = positional + defaulted + nameless + keyword
        write(emittable("=> %s(%s)\n" % (name, ", ".join(args))))
        try:
            result = fn(*v, **k)
            write(emittable("<= %s : %s\n" % (name, result)))
        except Exception as e:
            write(emittable("<# %s exited exceptionally (%s.%s) via %r\n" % (name, os.path.basename(traceback.extract_stack()[-2][0]), traceback.extract_stack()[-2][1], e)))
            raise e
        return result
    return wrapped

def eecho(fn, write=sys.stderr.write):
    return echo(fn, write=sys.stderr.write)

# 18 April 2014
# adapted from https://wiki.python.org/moin/PythonDecoratorLibrary
# import warnings
import functools

def deprecated(func):
    '''This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.'''

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        # warnings.warn_explicit(
        #     "Call to deprecated function {}.".format(func.__name__),
        #     category=DeprecationWarning,
        #     filename=func.func_code.co_filename,
        #     lineno=func.func_code.co_firstlineno + 1
        # )

        print(("Call to deprecated function %s from %s.%s." %
                              (func.__name__,
                               func.__code__.co_filename,
                               func.__code__.co_firstlineno + 1)), file=sys.stderr)
        return func(*args, **kwargs)
    return new_func

# ## Usage examples ##
# @deprecated
# def my_func():
#     pass

# @other_decorators_must_be_upper
# @deprecated
# def my_func():
#     pass

# #!/usr/bin/env python

# """
# Deprecated decorator.

# Author: Giampaolo Rodola' <g.rodola [AT] gmail [DOT] com>
# License: MIT
# """

# import warnings
# import functools

# def deprecated(replacement=None):
#     """A decorator which can be used to mark functions as deprecated.
#     replacement is a callable that will be called with the same args
#     as the decorated function.

#     >>> @deprecated()
#     ... def foo(x):
#     ...     return x
#     ...
#     >>> ret = foo(1)
#     DeprecationWarning: foo is deprecated
#     >>> ret
#     1
#     >>>
#     >>>
#     >>> def newfun(x):
#     ...     return 0
#     ...
#     >>> @deprecated(newfun)
#     ... def foo(x):
#     ...     return x
#     ...
#     >>> ret = foo(1)
#     DeprecationWarning: foo is deprecated; use newfun instead
#     >>> ret
#     0
#     >>>
#     """
#     def outer(fun):
#         msg = "psutil.%s is deprecated" % fun.__name__
#         if replacement is not None:
#             msg += "; use %s instead" % replacement
#         if fun.__doc__ is None:
#             fun.__doc__ = msg

#         @functools.wraps(fun)
#         def inner(*args, **kwargs):
#             warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
#             return fun(*args, **kwargs)

#         return inner
#     return outer

def stub(func):
    '''This is a decorator which can be used to mark functions
    as stubbed out.'''

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        # warnings.warn_explicit(
        #     "Call to deprecated function {}.".format(func.__name__),
        #     category=DeprecationWarning,
        #     filename=func.func_code.co_filename,
        #     lineno=func.func_code.co_firstlineno + 1
        # )

        print(("Call to stubbed-out function %s from %s.%s." %
                              (func.__name__,
                               func.__code__.co_filename,
                               func.__code__.co_firstlineno + 1)), file=sys.stderr)
        return func(*args, **kwargs)
    return new_func

def gripe(msg, *args):
    i = inspect.getouterframes(inspect.currentframe(),1)[1]
    blurb = msg % tuple(args)
    print("---- %s:%s in %s -- %s" % (os.path.basename(i[1]), i[2], i[3], blurb), file=sys.stderr)
    del i

def blab(msg, *args):
    i = inspect.getouterframes(inspect.currentframe(),1)[1]
    blurb = msg % tuple(args)
    print("-- %s:%s in %s -- %s" % (os.path.basename(i[1]), i[2], i[3], blurb), file=sys.stderr)
    del i

def gossip(msg, *args):
    i = inspect.getouterframes(inspect.currentframe(),1)[1]
    blurb = msg % tuple(args)
    print("-- %s:%s in %s -- %s" % (os.path.basename(i[1]), i[2], i[3], blurb), file=sys.stdout)
    del i

class Talkative(object):
    def vgripe(self, msg, *args):
        try:
            if self.verbose:
                # gripe(msg, *args)
                i = inspect.getouterframes(inspect.currentframe(),1)[1]
                blurb = msg % tuple(args)
                print(":::: %s:%s in %s :: %s" % (os.path.basename(i[1]), i[2], i[3], blurb), file=sys.stderr)
                del i
        except:
            pass

    def vblab(self, msg, *args):
        try:
            if self.verbose:
                # blab(msg, *args)
                i = inspect.getouterframes(inspect.currentframe(),1)[1]
                blurb = msg % tuple(args)
                print(":: %s:%s in %s :: %s" % (os.path.basename(i[1]), i[2], i[3], blurb), file=sys.stderr)
                del i
        except:
            pass

# from http://wiki.python.org/moin/PythonDecoratorLibrary#Cached_Properties
#
# (c) 2011 Christopher Arndt, MIT License
#

class cached_property(object):
    '''Decorator for read-only properties evaluated only once within TTL period.

    It can be used to created a cached property like this::

        import random

        # the class containing the property must be a new-style class
        class MyClass(object):
            # create property whose value is cached for ten minutes
            @cached_property(ttl=600)
            def randint(self):
                # will only be evaluated every 10 min. at maximum.
                return random.randint(0, 100)

    The value is cached  in the '_cache' attribute of the object instance that
    has the property getter method wrapped by this decorator. The '_cache'
    attribute value is a dictionary which has a key for every property of the
    object which is wrapped by this decorator. Each entry in the cache is
    created only when the property is accessed for the first time and is a
    two-element tuple with the last computed property value and the last time
    it was updated in seconds since the epoch.

    The default time-to-live (TTL) is 300 seconds (5 minutes). Set the TTL to
    zero for the cached value to never expire.

    To expire a cached property value manually just do::

        del instance._cache[<property name>]

    '''
    def __init__(self, ttl=300):
        self.ttl = ttl

    def __call__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__
        return self

    def __get__(self, inst, owner):
        now = time.time()
        try:
            value, last_update = inst._cache[self.__name__]
            if self.ttl > 0 and now - last_update > self.ttl:
                raise AttributeError
        except (KeyError, AttributeError):
            value = self.fget(inst)
            try:
                cache = inst._cache
            except AttributeError:
                cache = inst._cache = {}
            cache[self.__name__] = (value, now)
        return value


# util section splitpath
# from http://nicks-liquid-soapbox.blogspot.com/2011/03/splitting-path-to-list-in-python.html
  
def splitpath(path, maxdepth=20):
    ( head, tail ) = os.path.split(path)
    return splitpath(head, maxdepth - 1) + [ tail ] \
        if maxdepth and head and head != path \
        else [ head or tail ]

def ancestry(path, depth=3):
    return os.path.join(*splitpath(path)[-depth:])

#philpot
def pathnameName(pth):
    return os.path.splitext(os.path.split(pth)[1])[0]

#philpot
def pathnameType(pth):
    return os.path.splitext(pth)[1].lstrip('.')

# 19 March 2013
def lowestMatchingPath(path, leafDir):
    #info(path)
    #print """/usr/bin/python""" in path
    #print """/usr/bin/python -m cProfile -s cumulative""" in path
    # path = path[0:17] + path[42:]
    #print path
    # if -m cProfile -s cumulative
    # /usr/lib64/python2.7/cProfile.py
    comps = splitpath(os.path.realpath(path))
    pos = position(leafDir, comps, fromEnd=True)
    if not pos:
        raise ValueError("No such directory %s in path %s" % (leafDir, path))
    return os.path.join(*comps[0:pos+1])

# 19 March 2013
def parentDir(start,count=1):
    for i in range(count):
        start = os.path.join(start, os.pardir)
    return os.path.abspath(start)

def slurp(streamDesignator):
    '''streamDesignator could be string=filename, sys.stdin, - (= sys.stdin), or an opened file'''
    stream = streamDesignator
    if isinstance(streamDesignator,str):
        stream = open(streamDesignator)
    contents = []
    for line in stream:
        contents.append(line)
    return "".join(contents)

import os, errno

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: 
            raise

## essentially the same

def ensureDirectoriesExist(path):
    d = os.path.dirname(path)
    try:
        os.makedirs(d)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

# adapted from http://stackoverflow.com/questions/431684/how-do-i-cd-in-python

class CurrentDirectoryContext:
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

# # Now you can enter the directory like this:
# with CurrentDirectoryContext("~/Library"):
#    # we are in ~/Library
#    subprocess.call("ls")

def diskUsage(path, duCmd='du'):
    """Untested on bad input"""
    try:
        result = check_output([duCmd, "-s", "-b", os.path.realpath(path)])
        bytes = result.split('\t')[0]
        return int(bytes)
    except CalledProcessError as e:
        return None

def getFolderSize(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += getFolderSize(itempath)
    return total_size

def getFolderCount(folder):
    total_count = 0
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            # one for file
            total_count += 1
        elif os.path.isdir(itempath):
            # one for the dir
            total_count += 1
            # plus those in subdirs
            total_count += getFolderCount(itempath)
    return total_count

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

# util section ID
# adapted from http://effbot.org/zone/python-hash.htm

def c_mul(a, b):
    return eval(hex((int(a) * b) & 0xFFFFFFFF)[:-1])

def pseudohash(sequence):
    value = 0x345678
    for item in sequence:
        value = c_mul(1000003, value) ^ hash(item)
    value = value ^ len(sequence)
    if value == -1:
        value = -2
    return value

def iterChunks(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

# lisplike getf for list/tuple

def getf(seq, item):
    missing = object()
    for (key,val) in iterChunks(seq, 2, fillvalue=missing):
        if item == key:
            if val == missing:
                raise ValueError("malformed property list %s" % (seq,))
            return val
    return None

# adapted from http://effbot.org/zone/re-sub.html#unescape-html

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def decodeEntities(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return chr(int(text[3:-1], 16))
                else:
                    return chr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = chr(html.entities.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

# 1 September 2013

def escapeEntities(uc):
    return cgi.escape(uc).encode('ascii', 'xmlcharrefreplace')

# ported from Ute.pm

def safeDecodeEntities(text):
    """Simply delete any control chars in 0x00-0x1F, 0x7F-0xFF"""
    text = decodeEntities(text)
    # simply delete any control characters
    return re.sub(r"""[\x00-\x1F\x7F-\xFF]""", "", text)

# def safeAsciiString(text):
#     # try mightily to represent the contents of string
#     # using &#nnnn; if necessary

#     # 'unicodeescape' codec can't decode bytes in position 311-313: truncated \UXXXXXXXX escape
#     # e.g., in /nfs/studio-data/wat/data/escort/20130101/sandiego.backpage.com/FemaleEscorts/60-forget-the-rest-beautiful-from-top-to-bottom-im-the-best-60-23/8229874
#     # But this didn't fix it(!)
#     # # http://stackoverflow.com/questions/7602171/unicode-error-unicodeescape-codec-cant-decode-bytes-string-with-u
#     # # escape \U
#     # print "before, len is %s" % len(text)
#     # text = re.sub(r'\U',r'\\U',text)
#     # print "after, len is %s" % len(text)

#     # UnicodeDecodeError: 'unicodeescape' codec can't decode byte 0x5c in position 1035: \ at end of string
#     text = text.strip("""\\""")
#     if isinstance(text,str):
#         u = str(text,'unicode_escape')
#     elif isinstance(text,str):
#         u = text
#     else:
#         raise ValueError
#     # print ">> unicode %s" % u
#     a = u.encode('ascii','xmlcharrefreplace')
#     # print ">> xcrp %s" % a
    
#     # 1251 stuff 29 June 2012
#     t = dumb1251decode(a)
    
#     # finally, delete any remaining control characters
#     # should not be necessary(?)
#     raw = "[\x00-\x1F\x7F-\xFF]"
#     # print raw,len(raw)
#     return re.sub(raw, "", t)

def dumbDecodeEntities(text):
    """Encode as numeric entities any control chars in 0x00-0x1F, 0x7F-0xFF"""
    def fixup(m):
        text = m.group(0)
        # print "fixup %s" % text
        return "&#%s;" % ord(text[0:1])
    return re.sub("""[\x00-\x1F\x7F-\xFF]""", fixup, text)

def dumbEncodeControlChars(text):
    """Encode as numeric entities any control chars in 0x00-0x1F, 0x7F-0xFF"""
    def fixup(m):
        text = m.group(0)
        # print "fixup %s" % text
        return "&#%s;" % ord(text[0:1])
    return re.sub("""[\x00-\x1F\x7F-\xFF]""", fixup, text)

# 30 January 2013
# gets data as unicode, turns it into a string where all bad characters
# including control characters: x00 - x1F
# including non Ascii latin-1: x7F - XFF
# including unicode #x100 - infinity ;-)
# are represented as decimal HTML entities

import gzip

def slurpAsciiEntitified(file):
    try:
        with codecs.open(file, encoding='utf-8', mode='r') as stream:
            # lines: a list of unicode objects
            lines = [line for line in stream]
            # blob: a unicode object
            blob = "".join(lines)
            # print type(blob)
            # text: a unicode object
            text = " ".join(blob.splitlines())
            # print type(text)
            # escaped: a string
            escaped = safeAsciiString(dumbDecodeEntities(text))
            return escaped
    except UnicodeDecodeError as e:
        # 14 February 2013
        # Assume failure due to file being gzipped(!)
        # e.g., /nfs/studio-data/wat/data/escort/20130101/longbeach.backpage.com/FemaleEscorts/luscious-latina-bombshell-22/26059623
        print("retry reading %s as gzipped" % (file), file=sys.stderr)
        try:
            with gzip.open(file) as gunzipfile:
                # lines: a list of objects, convert on the fly to unicode utf-8
                lines = [line.decode('utf-8') for line in gunzipfile]
                # blob: a unicode object
                blob = "".join(lines)
                # print type(blob)
                # text: a unicode object
                text = " ".join(blob.splitlines())
                # print type(text)
                # escaped: a string
                escaped = safeAsciiString(dumbDecodeEntities(text))
                return escaped
        except IOError as e:
            return None

win1251replacements = {
    # win 1251 appears with hex encoded entity in 0x80-0x9F range
    "&#x80;": "&#x20AC;", # EURO SIGN                                          
    "&#x81;": "&#xFFFD;", # REPLACEMENT CHAR (philpot)                         
    "&#x82;": "&#x201A;", # SINGLE LOW-9 QUOTATION MARK                        
    "&#x83;": "&#x0192;", # LATIN SMALL LETTER F WITH HOOK                     
    "&#x84;": "&#x201E;", # DOUBLE LOW-9 QUOTATION MARK                        
    "&#x85;": "&#x2026;", # HORIZONTAL ELLIPSIS                                
    "&#x86;": "&#x2020;", # DAGGER                                             
    "&#x87;": "&#x2021;", # DOUBLE DAGGER                                      
    "&#x88;": "&#x02C6;", # MODIFIER LETTER CIRCUMFLEX ACCENT                  
    "&#x89;": "&#x2030;", # PER MILLE SIGN                                     
    "&#x8A;": "&#x0160;", # LATIN CAPITAL LETTER S WITH CARON                  
    "&#x8B;": "&#x2039;", # SINGLE LEFT-POINTING ANGLE QUOTATION MARK          
    "&#x8C;": "&#x0152;", # LATIN CAPITAL LIGATURE OE                          
    "&#x8D;": "&#xFFFD;", # REPLACEMENT CHAR (philpot)                         
    "&#x8E;": "&#x017D;", # LATIN CAPITAL LETTER Z WITH CARON                  
    "&#x8F;": "&#xFFFD;", # REPLACEMENT CHAR (philpot)                         
    "&#x90;": "&#xFFFD;", # REPLACEMENT CHAR (philpot)                         
    "&#x91;": "&#x2018;", # LEFT SINGLE QUOTATION MARK                         
    "&#x92;": "&#x2019;", # RIGHT SINGLE QUOTATION MARK                        
    "&#x93;": "&#x201C;", # LEFT DOUBLE QUOTATION MARK                         
    "&#x94;": "&#x201D;", # RIGHT DOUBLE QUOTATION MARK                        
    "&#x95;": "&#x2022;", # BULLET                                             
    "&#x96;": "&#x2013;", # EN DASH                                            
    "&#x97;": "&#x2014;", # EM DASH                                            
    "&#x98;": "&#x02DC;", # SMALL TILDE                                        
    "&#x99;": "&#x2122;", # TRADE MARK SIGN                                    
    "&#x9A;": "&#x0161;", # LATIN SMALL LETTER S WITH CARON                    
    "&#x9B;": "&#x203A;", # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK         
    "&#x9C;": "&#x0153;", # LATIN SMALL LIGATURE OE                            
    "&#x9D;": "&#xFFFD;", # REPLACEMENT CHAR (philpot)                         
    "&#x9E;": "&#x017E;", # LATIN SMALL LETTER Z WITH CARON                    
    "&#x9F;": "&#x0178;", # LATIN CAPITAL LETTER Y WITH DIAERESIS              
    
    # win 1251 appears with decimal-encoded entity in range
    "&#128;": "&#x20AC;", # EURO SIGN                                          
    "&#129;": "&#xFFFD;", # REPLACEMENT CHAR (philpot)                         
    "&#130;": "&#x201A;", # SINGLE LOW-9 QUOTATION MARK                        
    "&#131;": "&#x0192;", # LATIN SMALL LETTER F WITH HOOK                     
    "&#132;": "&#x201E;", # DOUBLE LOW-9 QUOTATION MARK                        
    "&#133;": "&#x2026;", # HORIZONTAL ELLIPSIS                                
    "&#134;": "&#x2020;", # DAGGER                                             
    "&#135;": "&#x2021;", # DOUBLE DAGGER                                      
    "&#136;": "&#x02C6;", # MODIFIER LETTER CIRCUMFLEX ACCENT                  
    "&#137;": "&#x2030;", # PER MILLE SIGN                                     
    "&#138;": "&#x0160;", # LATIN CAPITAL LETTER S WITH CARON                  
    "&#139;": "&#x2039;", # SINGLE LEFT-POINTING ANGLE QUOTATION MARK          
    "&#140;": "&#x0152;", # LATIN CAPITAL LIGATURE OE                          
    "&#141;": "&#xFFFD;", # REPLACEMENT CHAR (philpot)                         
    "&#142;": "&#x017D;", # LATIN CAPITAL LETTER Z WITH CARON                  
    "&#143;": "&#xFFFD;", # REPLACEMENT CHAR (philpot)                         
    "&#144;": "&#xFFFD;", # REPLACEMENT CHAR (philpot)                         
    "&#145;": "&#x2018;", # LEFT SINGLE QUOTATION MARK                         
    "&#146;": "&#x2019;", # RIGHT SINGLE QUOTATION MARK                        
    "&#147;": "&#x201C;", # LEFT DOUBLE QUOTATION MARK                         
    "&#148;": "&#x201D;", # RIGHT DOUBLE QUOTATION MARK                        
    "&#149;": "&#x2022;", # BULLET                                             
    "&#150;": "&#x2013;", # EN DASH                                            
    "&#151;": "&#x2014;", # EM DASH                                            
    "&#152;": "&#x02DC;", # SMALL TILDE                                        
    "&#153;": "&#x2122;", # TRADE MARK SIGN                                    
    "&#154;": "&#x0161;", # LATIN SMALL LETTER S WITH CARON                    
    "&#155;": "&#x203A;", # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK         
    "&#156;": "&#x0153;", # LATIN SMALL LIGATURE OE                            
    "&#157;": "&#xFFFD;", # REPLACEMENT CHAR (philpot)                         
    "&#158;": "&#x017E;", # LATIN SMALL LETTER Z WITH CARON                    
    "&#159;": "&#x0178;"  # LATIN CAPITAL LETTER Y WITH DIAERESIS              
    }

win1251regex = re.compile('''(&#(?:x8|x9|12|13|14|15)[0-9a-f];)''', re.IGNORECASE)

# Also see mapping table to emulate silly windows emulation

def win1251repl(matchobj):
    """I'm not sure I like this, I think we canonically want decimal entities, at least"""
    oldent = matchobj.group(0)
    # print "considering replacing %s" % oldent
    newent = win1251replacements.get(oldent,oldent)
    return newent

def dumb1251decode(text):
    return re.sub(win1251regex,win1251repl,text)

# 17 December 2013
def isGzipFile(path):
    # SANITY CHECK that a file is actually gzip, not just named .gz/.tgz
    fileType = None
    try:
        # if this succeeds, it is a gzip file
        s = gzip.GzipFile(path, 'r')
        s.read(2)
        fileType = "gzip"
    except IOError as e:
        # not a gzip file
        pass
    finally:
        # be sure and try to close it
        try:
            s.close()
        except:
            pass
    return (fileType == "gzip")

# 1 September 2013

def asutf8(x):
    if isinstance(x, (int, float)):
        x = str(x)
    return x.encode('utf-8')

#adapted from https://secure.wikimedia.org/wikipedia/en/wiki/Base_36

def base36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """Convert positive integer to a base36 string."""
    if not isinstance(number, int):
        raise TypeError('number must be an integer')
 
    # Special case for zero
    if number == 0:
        return alphabet[0]
 
    base36 = ''
 
    sign = ''
    if number < 0:
        sign = '-'
        number = - number
 
    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36
 
    return sign + base36
 
def base36decode(number):
    return int(number, 36)

#print base36encode(1412823931503067241)
#print base36decode('AQF8AA0006EH')

def vanillaRepr(o):
    cr = hasattr(o, "signature") and isinstance(getattr(o, "signature"), collections.Callable) and o.signature()
    cr = "'%s' " % (cr) if cr else ''
    return "{|%s %s@ %s|}" % (fullyQualifiedName(o), cr, base36encode(id(o)))
        
def vanillaStr(o):
    cr = hasattr(o, "signature") and isinstance(getattr(o, "signature"), collections.Callable) and o.signature()
    cr = "%s " % (cr) if cr else ''
    return emittable("<%s %s@ %s>" % (fullyQualifiedName(o), cr, base36encode(id(o))))

def abbrevString(s, max=10):
    if len(s) > max:
        return s[:max-3] + "..."
    else:
        return s

# util section control

def forever(x):
    while 1:
        yield x
        
# util section output
        
class NotEmittable(Exception):
    pass

onError=True

def emittable(atom, onError=True):
    e = atom
    if hasattr(e, "encode"):
        try:
            e = atom.encode('utf-8')
        except (AttributeError, TypeError):
            gripe("Failed to UTF-8 encode [%s], passing thru unchanged", atom)
        except UnicodeEncodeError:
            e = "###unencodable###"
        except UnicodeDecodeError:
            e = "###undecodable###"
            if onError:
                raise NotEmittable(atom)
        except:
            e = "###GeneralError###"
    else:
        e = str(e)
    return e

def utf8print(content):
    try:
        import sys
        reload(sys)
        sys.setdefaultencoding("utf-8")
        print(content)
    except:
        pass

# util section general introspection

def fullyQualifiedName(o):
    m =  o.__module__
    c = o.__class__.__name__
    l = []
    if m != '__main__':
        l.append(m)
    l.append(c)
    return ".".join(l)

# adapted from
# """Visit http://diveintopython.org/"""

# __author__ = "Mark Pilgrim (mark@diveintopython.org)"

def safeGetAttr(o,e):
    try:
        return getattr(o,e)
    except AttributeError:
        return None

def attrChain(obj, *attrs):
    """if attrs is ["a1", "a2", ..., "an"], then this returns obj.a1.a2.a3...an.
If any .ak for k<n returns a scalar, stop and return None"""
    r = obj
    complete = False
    started = False
    for attr in attrs:
        try:
            r = getattr(r, attr)
            started = True
        except (ValueError, AttributeError) as e:
            return None
    complete = True
    if started and complete:
        return r
    else:
        raise SyntaxError("Must have some attrs")

def info(object, spacing=12, collapse=1, hidden=False, dest=sys.stdout):
    """Print methods and doc strings.
Takes module, class, list, dictionary, or string."""
    print("INFO for %r" % (object), file=dest)
    methodList = [e for e in dir(object) if isinstance(safeGetAttr(object, e), collections.Callable)]
    processFunc = collapse and (lambda s: " ".join(s.split())) or (lambda s: s)
    print("\n".join(["  %s %s" % (method.ljust(spacing),
                                processFunc(str(safeGetAttr(object, method).__doc__)))
                    for method in methodList
                    if hidden or not method.startswith("__")]), file=dest)
    attrList = [e for e in dir(object) if not isinstance(safeGetAttr(object, e), collections.Callable)]
    print("\n".join(["  %s %s" % (attr.ljust(spacing),
                                processFunc(str(safeGetAttr(object, attr))))
                    for attr in attrList
                    if hidden or not attr.startswith("__")]), file=dest)
    print("END INFO for %r" % (object), file=dest)

# if name == "main": print help.doc 

# util section data-directed programming

def lookupClass(name):
    try:
        g = globals().get(name)
    except TypeError:
        # For example if name is something unhashable
        return None
    return g if inspect.isclass(g) else None

def findClass(thing):
    # it's a class
    if inspect.isclass(thing):
        return thing
    # treat as class name (works if it is a string...)
    cl = lookupClass(thing)
    if cl:
        return cl
    # return object's stored class
    cl = thing.__class__
    return cl

def lookupFunction(name):
    "Don't try this at home, globals() aren't"
    try:
        print(globals())
        g = globals().get(name)
    except TypeError:
        # For example if name is something unhashable
        return None
    return g if inspect.isfunction(g) else None

prototypes = {}

def prototype(classOrName, *args, **kwdargs):
    cl = findClass(classOrName)
    if cl:
        proto = prototypes.get(cl)
        if not proto:
            proto = cl(*args, **kwdargs)
            prototypes[cl] = proto
        return proto
    return None
    
def objectify(designator, *args, **kwdargs):
    return prototype(designator, *args, **kwdargs) or designator.__class__ or designator

def master(dispatch_arg, arg1, arg2, **kwdargs):
    return objectify(dispatch_arg).slave(arg1,arg2,**kwdargs)

# example
# Each of these classes exists only to allow data directed programming

#class Banana(object):
#    def slave(self, arg1, arg2, **kwdargs):
#        print "I am a banana slave"
#
#class Orange(object):
#    def slave(self, arg1, arg2, **kwdargs):
#        print "I am an orange slave"

# util section : lists

def canonList(thing):
    if isinstance(thing, list):
        return thing
    elif isinstance(thing, (tuple, set, dict)):
        return list(thing)
    else:
        return [thing]
    
# util section: string

def unprefix(prefix, s, strict=False):
    if s.startswith(prefix):
        return s[len(prefix):]
    else:
        if strict:
            raise ValueError("string '%s' has no prefix '%s'" % (s, prefix))
        else:
            return s
        
def unsuffix(suffix, s, strict=False):
    if s.endswith(suffix):
        return s[:-len(suffix)]
    else:
        if strict:
            raise ValueError("String '%s' has no suffix '%s'" % (s, suffix))
        else:
            return s
        
# util section : format

def fmt(fmtString, *args):
    return fmtString.format(*args)

# util section temp i/o

outputFiles = {}

def getOutputFile(prefix=None, delete=False, dir=".", mode='w+b'):
    scriptName = sys.argv and sys.argv[0]
    # assumes that processing has used fileinput.input to open files of interest, either stdin or file(s) passed in on command line
    prefix = prefix if prefix else fileinput.filename()
    prefix = prefix if (prefix and prefix != '<stdin>') else (scriptName or "out")
    outputFile = outputFiles.get(prefix) or outputFiles.setdefault(prefix, tempfile.NamedTemporaryFile(mode=mode, prefix=prefix+"-", delete=delete, dir=dir))
    return outputFile
        
# end utils

def backupFile(pathname):
    """Quick and dirty rename file to timestamped version"""
    t=time.localtime()
    timestamp = time.strftime("%Y%m%d%H%M%S", t)
    os.rename(pathname, pathname + "_" + str(timestamp))

# util section fns

def guess_boolean(thing):
    if thing in ("1", 1, "Y", "y", "YES", "Yes", "yes", "T", "t", "TRUE", "True", "true"):
        return True
    elif thing in ("0", 0, "N", "n", "NO", "No", "no", "F", "f", "FALSE", "False", "false", 
                   "NONE", "None", "none", ""):
        return False
    else:
        raise TypeError('thing must denote a boolean')

# end fns

def rebase(num, base=16):
    rem = 1
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    result = []
    while num != 0:
        rem = num % base
        num = num/base
        result.append(digits[rem])
    result.reverse()
    return "".join(result)

def asStream(streamDesignator, mode=None):
    '''streamDesignator could be string=filename, sys.stdin, - (= sys.stdin), or an opened file'''
    stream = streamDesignator
    if isinstance(streamDesignator, str):
        try: 
            stream = open(streamDesignator, mode)
        except IOError as e:
            stream = io.StringIO(streamDesignator)
    return stream

# 29 January 2013

# import codecs
# import io

# def asUnicodeStream(streamDesignator, mode='r'):
#     '''streamDesignator could be string=filename, sys.stdin, - (= sys.stdin), or an opened file'''

#     stream = streamDesignator
#     # print emittable(streamDesignator)
#     if isinstance(streamDesignator,str) or isinstance(streamDesignator, unicode):
#         try: 
#             # print emittable("%s, encoding=%s, mode=%s" % (streamDesignator, 'utf-8', mode))
#             stream = codecs.open(streamDesignator, encoding='utf-8', mode=mode)
#         except IOError as e:
#             stream = StringIO.StringIO(streamDesignator)
#         except UnicodeError as e:
#             stream = io.StringIO(streamDesignator)
#     return stream


# '''perl s/[^\x9\xA\xD\x20-\x{D7FF}\x{E000}-\x{FFFD}\x{10000}-\x{10FFFF}]//g'''
def xmlclean(s):
    '''I don't think this really does what I want it to do'''
    # s = re.sub(ur'[^\u0009\u000A\u000D\u0020-\uD7FF\uE000-\uFFFD\U00010000-\U0010FFFF]+','',s,0)
    return s

def isSequence(obj):
    '''Ignores the fact that str is a sequence.  That's not the kind of sequence I care about in this context'''
    return type(obj) in [str, list, tuple, buffer, xrange]

def isIterable(obj):
    '''Ignores the fact that str, unicode are iterable.  That's not what I want'''
    if isinstance(obj,str):
        return False
    else:
        try:
            i = iter(obj)
            return True
        except TypeError as te:
            return False

# adapted from http://stackoverflow.com/a/6710895

def canonIterable(iterable):
    if not isIterable(iterable):
       return [iterable]
    else:
        try:
            iter(iterable)
        except TypeError:
            iterable = [iterable]
        return iterable

def isString(obj):
    return isinstance(obj, str)

def identity(x):
    return x

def ignore(*_):
    pass

def printToDest(thing, dest=sys.stdout):
    """Useful when we need to use 'print' (statement) as a function"""
    print(thing, file=dest)

import functools
printToStdout = functools.partial(printToDest, dest=sys.stdout)
printToStderr = functools.partial(printToDest, dest=sys.stderr)

# generator-based
# def find(item,seq,key=identity):
#     next((elt for elt in seq if key(elt) == item),None)

def find(item, seq, key=identity, fromEnd=False, default=None):
    for elt in reversed(seq) if fromEnd else seq:
        if key(elt) == item:
            return elt
    return default

def findIf(fn, seq, key=identity, fromEnd=False, default=None):
    for elt in reversed(seq) if fromEnd else seq:
        if fn(key(elt)):
            return elt
    return default

# generator-based
# def position(item,seq,key=identity):
#     next((pos for pos in range(len(seq)) if key(seq[pos]) == item),None)

def position(item, seq, key=identity, fromEnd=False, default=None):
    i = 0
    for elt in reversed(seq) if fromEnd else seq:
        if key(elt) == item:
            return len(seq)-i-1 if fromEnd else i
        i += 1
    return default

def positionIf(fn, seq, key=identity, fromEnd=False, start=0, default=None):
    i = start
    seq = seq[start:] if start else seq
    for elt in reversed(seq) if fromEnd else seq:
        if fn(key(elt)):
            return len(seq)-i-1 if fromEnd else i
        i += 1
    return default

def enumerate1(iterable):
    """Like built-in enumerate, but 1-based"""
    for (index,object) in enumerate(iterable):
        yield (1+index, object)

# print find('a',['x','a','5'])
# print find('a',[['x','y'],['a','b'],['5',6]],key=lambda l:l[0])
# print position('a',['x','a','5'])
# print position('a',[['x','y'],['a','b'],['5',6]],key=lambda l:l[0])

def timestamp(now=None):
    now = now if now else datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def parseTimestamp(s):
    return datetime.datetime.fromtimestamp(time.mktime(time.strptime(s,'%Y-%m-%d %H:%M:%S')))

def datestamp(now=None):
    now = now if now else datetime.datetime.now()
    return now.strftime("%Y%m%d")

def genDatestamps(start=20120101, end=20131231):
    def toDate(ds):
        ds = int(ds)
        return datetime.date(ds/10000, (ds%10000)/100, ds%100)

    startDate = toDate(start)
    endDate = toDate(end)
    for n in range(int ((endDate - startDate).days+1)):
        yield int(datetime.datetime.strftime(startDate + datetime.timedelta(n), "%Y%m%d"))

def elapsed(delta, round=True):
    if round:
        try:
            delta = datetime.timedelta(seconds=math.trunc(delta.total_seconds()))
        except AttributeError as e:
            # prior to 2.7
            total = delta.seconds + delta.days * 24 * 3600
            delta = datetime.timedelta(seconds=total)
    return str(delta)

# from http://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python

def daterange(start, stop, step=1, inclusive=False):
    """start, stop, and step must all be the same type, either datetime.datetime, int or string.  Output will match input type"""
    if isinstance(start, int):
        fmt = lambda d: int(d.strftime("%Y%m%d"))
        start = datetime.datetime.strptime(str(start), "%Y%m%d")
        stop = datetime.datetime.strptime(str(stop), "%Y%m%d")
        step = datetime.timedelta(days=step)
    elif isinstance(start, str):
        fmt = lambda d: d.strftime("%Y%m%d")
        start = datetime.datetime.strptime(start, "%Y%m%d")
        stop = datetime.datetime.strptime(stop, "%Y%m%d")
        step = datetime.timedelta(days=int(step))
    else:
        fmt = lambda d: d
    # inclusive=False to behave like range by default
    if step.days > 0:
        while start < stop:
            yield fmt(start)
            start = start + step
            # not +=! don't modify object passed in if it's mutable
            # since this function is not restricted to
            # only types from datetime module
    elif step.days < 0:
        while start > stop:
            yield fmt(start)
            start = start + step
    if inclusive and start == stop:
        yield fmt(start)

# ...
# 
# for date in daterange(start_date, end_date, inclusive=True):
#     print strftime("%Y-%m-%d", date.timetuple())

def interpretDatestamps(datestamps):
    """datestamps is a set of argparse arguments,
so it can be
-- empty sequence => interpreted as today only
-- non-empty sequence
in which each integer element => interpreted as that datestamp
         each daterange element YYYYMMDD:YYYYMMDD => interpreted as the range of dates
the result is deduped and reeturned as sorted list
will raise ValueError for bad args"""
    datestamps = sorted(list(set(datestamps)))
    # We can either have 
    if len(datestamps) == 0:
        # neither datestamp nor range => just today
        datestamps = [datetime.datetime.now().strftime("%Y%m%d")]
    else:
        unabbreviated = []
        for datestamp in datestamps:
            # tuple: indicates a date range
            if isinstance(datestamp, tuple):
                unabbreviated.extend(daterange(datestamp[0], datestamp[1], inclusive=True))
            # integer: indicates a single date
            elif isinstance(datestamp, int):
                unabbreviated.append(datestamp)
            else:
                raise ValueError("Bad datestamp arg: %s" % datestamp)
        datestamps = unabbreviated
    datestamps = sorted(datestamps)
    return datestamps

def canonHostname(hostname):
    if re.match(r'''\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}''', hostname):
        return hostname
    else:
        m = re.match(r'''([^.]+)''', hostname)
        return m.group(1)

def snippet(s,n=8):
    '''first N (clipped) chars of string'''
    s = str(s)
    start = 0
    end = min(len(s),n)
    return s[start:end]

def rsnippet(s,n=8):
    ''' last N (clipped) chars of string'''
    s = str(s)
    start = max(0,len(s)-n)
    return s[start:]

def stdout_encode(u, default='UTF8'):
    if sys.stdout.encoding:
        return u.encode(sys.stdout.encoding)
    return u.encode(default)

def redirectTo(url,method="javascript",pause=1000):
    if method=="javascript":
        print('Content-Type: text/html\n')
        print("""<script>
setTimeout("window.location.replace('%s')" ,%s)
</script>""" % (url, pause))
    elif method=="refresh":
        print('Content-Type: text/html\n')
        print("""<html>
<head>
<meta http-equiv="Refresh" content="%s; url=%s" />
</head>
<body>
<p>Please follow <a href="%s">this link</a>.</p>
</body>
</html>""" % ((int(math.ceil(pause/1000))),url,url))
    elif method=="header":
        print('HTTP/1.1 303 See other')
        print('Location: %s' % url)
    else:
        raise ValueError("Unknown redirect method %s" % method)

def mergeUris(baseUri, fragmentUri):
    baseUri = str(baseUri)
    fragmentUri = str(fragmentUri)
    p = baseUri.rindex('/')
    return baseUri[0:p] + '/' + fragmentUri.lstrip('/')

def chunkedFetchUrl(url, local_filename=None, **kwargs):
    """Adapted from http://stackoverflow.com/q/16694907"""
    if not local_filename:
        local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True, **kwargs)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return local_filename

def chunkedFetchUrlText(url, **kwargs):
    f = io.StringIO()
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True, **kwargs)
    for chunk in r.iter_content(chunk_size=1024): 
        if chunk: # filter out keep-alive new chunks
            f.write(chunk)
            f.flush()
    text = f.getvalue()
    f.close()
    return text

# https://karmadigstorage.blob.core.windows.net/arch/churl/20140101/bellingham.backpage.com/FemaleEscorts/120-morning-special-dont-miss-this-25/14910841

import http.client
from urllib.parse import urlparse

def checkUrl(url):
    """From http://stackoverflow.com/a/6471552/2077242.  Not perfect but will work for s3"""
    p = urlparse(url)
    conn = http.client.HTTPConnection(p.netloc)
    conn.request('HEAD', p.path)
    resp = conn.getresponse()
    return resp.status < 400

def bytesToHex( byteStr ):
    """
    from http://code.activestate.com/recipes/510399-byte-to-hex-and-hex-to-byte-string-conversion/
    Convert a byte string to its hex string representation e.g. for output.
    """
    
    # Uses list comprehension which is a fractionally faster implementation than
    # the alternative, more readable, implementation below
    #   
    #    hex = []
    #    for aChar in byteStr:
    #        hex.append( "%02X " % ord( aChar ) )
    #
    #    return ''.join( hex ).strip()        

    # return ''.join( [ "%02X " % ord( x ) for x in byteStr ] ).strip()
    return ''.join( [ "%02x" % ord( x ) for x in byteStr ] ).strip()

ZEROS = "0" * 40

### it's not 100% clear that this corresponds exactly to 
### MySQL's sha1 built-in function

def safeHex(contents, default=ZEROS):
    return hashlib.sha1(contents).hexdigest() if contents else default

# from http://stackoverflow.com/questions/651794/whats-the-best-way-to-initialize-a-dict-of-dicts-in-python
from collections import defaultdict
def autovivdict():
    return defaultdict(autovivdict)

# from collections import Counter
def printHistogram(histogram):
    for key in sorted(list(histogram.keys()), reverse=True):
        print("%s: %s" % (key, histogram[key]))

# stolen from managed
def settableAttrs(obj):
    """Truly I would like something like issettable(self,key) but didn't find such"""
    return [key for (key,val) in inspect.getmembers(obj) 
            if key[0] != '_' and not inspect.ismethod(val)]

### ;;; 13 August 2013 by Philpot
### test data for coalesce
### pairs = [("a", "e"), ("z", "f"), ("m", "b"), ("p", "k"), ("e", "i"), ("f", "s"), ("b", "d"), ("t", "p"), ("i", "o"), ("s", "v"), ("d", "g"), ("k", "p"), ("o", "u"), ("v", "z"), ("g", "m"), ("p", "t")]


#####
###
### Coalesce(list of pairs)
###
### Take a list of pairs and create a set of equivalence classes.  For
### example, 
###
### (coalesce '((a . e) (z . f) (m . b) (p . k) (e . i) (f . s) 
###             (b . d) (t . p) (i . o) (s . v) (d . g) (k . p)
###             (o . u) (v . z) (g . m) (p . t)))
###
### should return something like
### 
### ((U O I A E) (V S Z F) (G D M B) (T P K)) 
###
### Note that one minor change was made from Winston & Horn's
### implementation: the input list of equivalence pairs is implemented
### as a list of CONS pairs, not a list of 2-ary lists.
###
### 24 April 1991 by Philpot
###
### 29 September 1995 by Philpot
### Further abstract by allowing user to supply "car" and "cdr"
### functions to extract data from the pairs.
###
#####

from pprint import pprint

def coalesce(pairs):
    classes = defaultdict(set)
    def update(a, b):
        if a in classes and b in classes:
            case = 1
            # merge them
            merged = classes[a].union(classes[b])
            for member in merged:
                classes[member] = merged
            #print >> sys.stderr, "Case 1: a [%s] -> %s, b [%s] -> %s" % (a, classes[a], b, classes[b])
            #pprint(classes, stream=sys.stderr)
        elif a in classes:
            case = 2
            # add b to a's class
            classes[a].add(b)
            classes[b] = classes[a]
        elif b in classes:
            case = 3
            # add a to b's class
            classes[b].add(a)
            classes[a] = classes[b]
        else:
            case = 4
            # both 4 and 5 from above
            new = set([a,b])
            classes[a] = new
            classes[b] = new
        # print >> sys.stderr, ("After adding in (%s,%s) using %s, all classes are: %s" %
        #                       (a, b, case, set([tuple(s) for s in classes.values()])))
    for pair in pairs:
        update(pair[0], pair[1])
    return set(tuple(s) for s in list(classes.values()))
            
# for argparse

def interpretCmdLine(args=sys.argv):
    """Why is this necessary?? Reverse engineer and document"""
    prog = os.path.basename(args[0])
    if prog in ['invoke', 'iinvoke']:
        return((prog + " " + args[1], args[2:]))
    else:
        return(prog, args[1:])

def validDatestamp(string):
    if re.search(r"""^201[2-9][01][0-9][0-3][0-9]$""", string):
        value=int(string)
    else:
        msg = "%r is not a valid datestamp" % string
        raise argparse.ArgumentTypeError(msg)
    return value

def validDatestampRange(string):
    m = re.search(r"""^(201[2-9][01][0-9][0-3][0-9]):(201[2-9][01][0-9][0-3][0-9])$""", string)
    if m:
        d1 = int(m.group(1))
        d2 = int(m.group(2))
        if d1 < d2:
            value = (d1, d2)
    else:
        msg = "%r is not a valid datestamp range" % string
        raise argparse.ArgumentTypeError(msg)
    return value

def validDatestampOrRange(string):
    try:
        return validDatestampRange(string)
    except argparse.ArgumentTypeError as e:
        try:
            return validDatestamp(string)
        except argparse.ArgumentTypeError as e:
            msg = "%r is neither a valid datestamp nor a datestamp range" % string
            raise argparse.ArgumentTypeError(msg)

# haversine great circle distance

from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2, unit='mi'):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = list(map(radians, [lon1, lat1, lon2, lat2]))
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    # print "dlat=%r,dlon=%r" % (dlat, dlon)
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    
    distance = {'km': 6367,
                'mi': 3956,
                'ft': 20889110}[unit] * c
    return distance


# brought in from context.py r23462

@contextmanager
def attrAs (obj, attrName, value):
    existed = True
    try:
        try:
            old_value = getattr(obj, attrName)
        except AttributeError:
            existed = False
        setattr(obj, attrName, value)
        yield None
    except:
        # print "catch/rethrow"
        if existed:
            setattr(obj, attrName, old_value)
        else:
            delattr(obj, attrName)
        raise
    # print "unexceptional"
    if existed:
        setattr(obj, attrName, old_value)
    else:
        delattr(obj, attrName)

PYMODDIR = os.path.dirname(__file__)

def makeDeathWish(clockTime, allInGroup=True, verbose=False, silent=True):
    """Launch an 'at' job that will kill the current process at the stated time"""
    trash = open(os.devnull, 'w')
    parent = mp.current_process()
    parentPid = parent.pid
    # process group: if negative it means kill process and all its children (??)
    # groupPid = -abs(parentPid) if allInGroup else abs(parentPid)
    groupPid = abs(parentPid)
    if verbose:
        print("parent %s %s" % (groupPid, parent))
    # windows
    # child = subprocess.Popen(['at', '22:25'], creationflags=DETACHED_PROCESS)
    # child = subprocess.Popen(['at', '-t', '201310082251'], shell=False, stdin=subprocess.PIPE, stdout=None, stderr=None, close_fds=True)
    child = subprocess.Popen(['at', str(clockTime)], 
                             shell=False, 
                             stdin=subprocess.PIPE, stdout=trash, stderr=trash, 
                             close_fds=True)
    childPid = child.pid
    if verbose:
        print("child %s %s" % (childPid, child))
    if silent:
        # adds /dev/null redirect within the kill
        proc = os.path.join(PYMODDIR, "killsilent.sh")
    else:
        proc = "kill"
    child.communicate(input='%s %s' % (proc, groupPid))
    return child

# from http://stackoverflow.com/a/14707227/2077242

import sys
from contextlib import contextmanager
@contextmanager
def stdoutRedirected(new_stdout):
    save_stdout = sys.stdout
    sys.stdout = new_stdout
    try:
        yield None
    finally:
        sys.stdout = save_stdout

def camelCase(y):
    y=y.translate(None,r"`~!@#$%^&*()-_+=,<.>?/{}[]|\\'")
    z=''.join(x for x in y.title() if not x.isspace())
    w=z[0].lower()+z[1:]
    return w

import smtplib
# try
def textViaGmail(number, msg, provider='virgin'):

    # Next, establish a secure session with gmail's outgoing SMTP
    # server using your gmail account. A TLS or SSL connection must be
    # used; the example below uses STARTTLS which is port 587.  

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    appSpecificPw = 'lvonhierukjirwkz'
    server.login('andrew.philpot@gmail.com', appSpecificPw)

    # Now you're set up to send email. You will send a text message by
    # taking advantage of each mobile carrier's email to SMS gateway! 

    # For example, to send a text message to a t-mobile number, you
    # would use <number>@tmomail.net. To send a text message to an
    # AT&T number, you would use <number>@mms.att.net. 

    gateways = {'at&t': 'mss.att.net',
                'tmobile': 'tmomail.net',
                'virgin': 'vmobl.com'}

    # Once you have your phone destination, all that's left is to add
    # your message and send the mail.

    server.sendmail('8182573354', 
                    '%s@%s' % (number, gateways[provider]),
                    msg)

class Util(object):
    def __init__(self, args, verbose=VERBOSE):
        '''create Util'''
        self.verbose = verbose
        
def main(argv=None):
    '''this is called if run from command line'''
    # process command line arguments
    if argv is None:
        argv = sys.argv
    try:
        opts, args = getopt.getopt(argv[1:], "hv", ["echo=", "help"])
    except getopt.error as msg:
        print(msg)
        print("for help use --help")
        sys.exit(2)
    # default options
    my_verbose = VERBOSE
    # process options
    for o,a in opts:
        if o in ("-h","--help"):
            print(__doc__)
            sys.exit(0)
        if o in ("--echo", ):
            print(a)
        if o in ("-v", "--verbose", ):
            my_verbose = True
    u = Util(args, verbose=my_verbose)
    modname = globals()['__name__']
    print(repr(modname), u, ":")
    module = sys.modules[modname]
    print(dir(module)) 
    s = args[0] if args else 'abc\x00\x1F\x7E\x7F\xFFdef'
    print("input: %s" % s)
    # print len(s)
    # print("safe ascii: %s" % safeAsciiString(s))
    #d = dumbDecodeEntities(s)
    # print len(d)
    #print "dumbDecode: %s" % d
    #t = dumb1251decode(s)
    #print "dumb1251: %s" % t

# call main() if this is run as standalone
if __name__ == "__main__":
    sys.exit(main())

# End of util.py
