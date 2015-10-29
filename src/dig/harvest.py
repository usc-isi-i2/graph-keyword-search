#!/usr/bin/env python3

import sys
if sys.version_info < (3, 0):
    raise "must use python 3.0 or greater"

import sys
from elasticsearch import Elasticsearch
from pprint import pprint
import json
from collections import OrderedDict
import os

CA_CERTS_PATH='/Users/philpot/aws/credentials/certs.pem'

es = Elasticsearch(
    [
        'https://darpamemex:darpamemex@esc.memexproxy.com/' # dig-ht-latest/offer
        # 'http://user:secret@localhost:9200/', 
        ],
    # make sure we verify SSL certificates (off by default)
    verify_certs=True,
    # provide a path to CA certs on disk
    ca_certs=CA_CERTS_PATH
    )

def makeBodyNested(fieldName="name", innerPath="itemOffered", size=10):
    return {
        "query": {
            "match_all": {}
            },
        "aggs": {
            "toplevelAgg": {
                "nested": {
                    "path": innerPath
                    },
                "aggs": {
                    "termAgg": {
                        "terms": {
                            "field": "{}.{}".format(innerPath, fieldName),
                            "size" : size
                            }
                        }
                    }
                }
            }
        }

def makeBodyDirect(fieldName="name", size=10):
    return {
        "query": {
            "match_all": {}
            },
        "aggs": {
            "termAgg": {
                "terms": {
                    "field": fieldName,
                    "size": size
                    }
                }
            }
        }

def makeBody(fieldName="name", innerPath="", size=10):
    if innerPath:
        return makeBodyNested(fieldName=fieldName,
                              innerPath=innerPath,
                              size=size)
    else:
        return makeBodyDirect(fieldName=fieldName,
                              size=size)

"""
{'_shards': {'failed': 0, 'successful': 20, 'total': 20},
 'aggregations': {'toplevelAgg': {'doc_count': 19134836,
                                     'termAgg': {'buckets': [{'doc_count': 18104,
                                                                  'key': 'jessica'},
                                                                 {'doc_count': 15956,
                                                                  'key': 'ashley'},
                                                                 {'doc_count': 12748,
                                                                  'key': 'amber'},
                                                                 {'doc_count': 12037,
                                                                  'key': 'tiffany'},
                                                                 {'doc_count': 11808,
                                                                  'key': 'bella'},
                                                                 {'doc_count': 11628,
                                                                  'key': 'mya'},
                                                                 {'doc_count': 11514,
                                                                  'key': 'candy'},
                                                                 {'doc_count': 10963,
                                                                  'key': 'nikki'},
                                                                 {'doc_count': 10932,
                                                                  'key': 'diamond'},
                                                                 {'doc_count': 10808,
                                                                  'key': 'lexi'}],
                                                     'doc_count_error_upper_bound': 2728,
                                                     'sum_other_doc_count': 1322532}}},
 'hits': {'hits': [], 'max_score': 0.0, 'total': 19134836},
 'timed_out': False,
 'took': 1422}
"""

def harvest(index="dig-ht-latest", docType="webpage",fieldName="addressCountry", innerPath="", size=10):
    nested = True if innerPath else False
    body=makeBody(fieldName=fieldName, innerPath=innerPath, size=size)
    result = es.search(index=index,
                       doc_type=docType,
                       body=body,
                       search_type="count")
    agg = result['aggregations']['toplevelAgg']['termAgg'] if nested else result['aggregations']['termAgg']
    report = {"docType": docType,
              "fieldName": fieldName,
              "innerPath": innerPath,
              "size": size,
              # use 'result' later to get hitsTotal, sum_other_doc_count if needed
              "result": result,
              # collections.OrderedDict is serialized to JSON in the order keys were added
              # so preserves decreasing value order
              "histo": OrderedDict()
              }
    for bucket in agg['buckets']:
        report["histo"][bucket["key"]] = bucket["doc_count"]
    return report

# def outputPathname(docType="webpage", innerPath="mainEntity.availableAtOrFrom.address", fieldName="addressCountry", root="/tmp", **kwargs):
#     return os.path.join(root, "{}_{}_{}.json".format(docType, innerPath.replace('.', '_').replace('__','_'), fieldName))

OUTPUT_ROOT = "/Users/philpot/Documents/project/graph-keyword-search/src/dig/data/cache"

def outputPathname(docType="webpage", innerPath="", fieldName="addressCountry", root=OUTPUT_ROOT, **kwargs):
    return os.path.join(root, "{}_{}_{}.json".format(docType, innerPath.replace('.', '_').replace('__','_'), fieldName))

WORKING=[    # works
    {"docType": "offer", "innerPath": "itemOffered", "fieldName": "name", "size": 200},
    # works
    {"docType": "webpage", "innerPath": "publisher", "fieldName": "name", "size": 200},
    {"docType": "offer", "innerPath": "seller", "fieldName": "name", "size": 200},
    {"docType": "offer", "innerPath": "itemOffered", "fieldName": "personAge", "size": 20},
    
    {"docType": "offer", "innerPath": "mainEntityOfPage.publisher", "fieldName": "name", "size": 20},
    {"docType": "seller", "innerPath": "makesOffer.mainEntityOfPage.publisher", "fieldName": "name", "size": 20},
    {"docType": "phone", "innerPath": "owner.makesOffer.mainEntityOfPage.publisher", "fieldName": "name", "size": 20},
    {"docType": "offer", "innerPath": "priceSpecification", "fieldName": "billingIncrement", "size": 10},
    {"docType": "offer", "innerPath": "priceSpecification", "fieldName": "price", "size": 10},
    {"docType": "offer", "innerPath": "priceSpecification", "fieldName": "name", "size": 10},
    {"docType": "offer", "innerPath": "priceSpecification", "fieldName": "unitCode", "size": 10},
    {"docType": "offer", "innerPath": "priceSpecification", "fieldName": "billingIncrement", "size": 10},
    
    {"docType": "offer", "innerPath": "availableAtOrFrom", "fieldName": "name", "size": 10},
    {"docType": "offer", "innerPath": "availableAtOrFrom.geo", "fieldName": "lat", "size": 10},
    {"docType": "offer", "innerPath": "itemOffered", "fieldName": "hairColor", "size": 20},
    {"docType": "offer", "innerPath": "itemOffered", "fieldName": "eyeColor", "size": 20},
    {"docType": "offer", "innerPath": "itemOffered", "fieldName": "name", "size": 20},
    {"docType": "offer", "innerPath": "availableAtOrFrom.geo", "fieldName": "lat", "size": 10},
    {"docType": "seller", "innerPath": "telephone", "fieldName": "name", "size": 10},
    {"docType": "seller", "innerPath": "telephone", "fieldName": "a", "size": 10}
    ]


SPECS=[ # {"docType": "webpage", "innerPath": "mainEntity.availableAtOrFrom.address", "fieldName": "addressCountry", "size": 200},
    # {"docType": "webpage", "innerPath": "mainEntity.availableAtOrFrom.address", "fieldName": "addressRegion", "size": 200},
    # {"docType": "webpage", "innerPath": "mainEntity.availableAtOrFrom.address", "fieldName": "addressLocality", "size": 200},

    ###{"docType": "seller", "innerPath": "email", "fieldName": "name", "size": 10},
    ###{"docType": "seller", "innerPath": "email", "fieldName": "a", "size": 10},
    ###{"docType": "offer", "innerPath": "seller.telephone", "fieldName": "a", "size": 10},
    # WORKS
    ###{"docType": "seller", "innerPath": "telephone", "fieldName": "name", "size": 10},
    # DOES NOT WORK in pyelasticsearch, only in sense/curl
    {"docType": "offer", "innerPath": "seller.telephone", "fieldName": "name", "size": 10},
    # WORKS
    {"docType": "webpage", "innerPath": "mainEntity.seller.telephone", "fieldName": "name", "size": 10}
    
    # Doesn't work
    #       {"docType": "offer", "innerPath": "seller.telephone", "fieldName": "name", "size": 200},
    # ???
    #       {"docType": "offer", "innerPath": "seller", "fieldName": "a", "size": 200},
    # {"docType": "offer", "innerPath": "itemOffered", "fieldName": "a", "size": 200},

    #       {"docType": "seller", "innerPath": "telephone", "fieldName": "name", "size": 200}
    # bad syntax
    #        {"docType": "address", "innerPath": "", "fieldName": "addressCountry", "size": 200}
    # doesn't work
    # probably the issue w.r.t. nested Pedro suggested
    # but sibling fields do work
    ]

# SPECS=[ {"docType": "offer", "innerPath": "itemOffered", "fieldName": "name", "size": 10} ]

SPECS=[ {"docType": "adultservice", "fieldName": "eyeColor", "size": 10} ]

SPECS=[ {"docType": "adultservice", "fieldName": "eyeColor", "size": 10},
        {"docType": "adultservice", "fieldName": "hairColor", "size": 10},
        {"docType": "adultservice", "fieldName": "name", "size": 200},
        {"docType": "adultservice", "fieldName": "personAge", "size": 20},

        # These are valid, but has flat distribution, so not useful for suggestion
        # {"docType": "phone", "fieldName": "name", "size": 200},
        # {"docType": "email", "fieldName": "name", "size": 200},
        # Instead seller-centric distribution
        {"docType": "seller", "innerPath": "telephone", "fieldName": "name", "size": 200},
        {"docType": "seller", "innerPath": "email", "fieldName": "name", "size": 200},

        {"docType": "webpage", "innerPath": "publisher", "fieldName": "name", "size": 200},
        # Ignore webpage.description, webpage.dateCreated

        # Ignore offer.identifier
        {"docType": "offer", "innerPath": "priceSpecification", "fieldName": "billingIncrement", "size": 10},
        {"docType": "offer", "innerPath": "priceSpecification", "fieldName": "price", "size": 200},
        {"docType": "offer", "innerPath": "priceSpecification", "fieldName": "name", "size": 200},
        {"docType": "offer", "innerPath": "priceSpecification", "fieldName": "unitCode", "size": 10},
        {"docType": "offer", "innerPath": "availableAtOrFrom.address", "fieldName": "addressLocality", "size": 200},
        {"docType": "offer", "innerPath": "availableAtOrFrom.address", "fieldName": "addressRegion", "size": 200},
        {"docType": "offer", "innerPath": "availableAtOrFrom.address", "fieldName": "addressCountry", "size": 200},
        # Ignore offer.availableAtOrFrom.name
        # Ignore offer.availableAtOrFrom.geo.lat, offer.availableAtOrFrom.geo.lon

    ]

def harvestToFile(spec):
    outPath = None
    try:
        outPath = outputPathname(**spec)
    except:
        pass
    try:
        h = harvest(**spec)
        print("Harvest to {}".format(outPath), file=sys.stderr)
        with open(outPath, 'w') as f:
            # Don't use sort_keys here
            # We are counting on the behavior where collections.OrderedDict is
            # serialized in the order keys were added.  If we add things in
            # order of decreasing counts, the order will stick, unless we use sort_keys.
            json.dump(h, f, indent=4)
    except Exception as e:
        print("Error [{}] during processing of {}".format(e, outPath))

def generateAll ():
    for spec in SPECS:
        print()
        print(spec)
        # harvestToFile(spec)
        try:
            h = harvest(**spec)
            # pprint(h)
            l = -1
            try:
                try:
                    # nested
                    b = h["result"]["aggregations"]["toplevelAgg"]["termAgg"]["buckets"]
                except:
                    # direct
                    b = h["result"]["aggregations"]["termAgg"]["buckets"]
                l = len(b)
                if l>0:
                    print("Success %d for %s" % (l, spec), file=sys.stderr)
                    q = 5
                    for i,v in zip(range(q+1), b[0:q]):
                        print("value %d is %s" % (i, v))
                elif l==0:
                    print("No data for %s" % (spec), file=sys.stderr)
                else:
                    pass
            except Exception as e:
                print("Nothing happened for %s" % (spec), file=sys.stderr)
                print(e, file=sys.stderr)
        except Exception as e:
            print("Failed during %s" % (spec), file=sys.stderr)
            print(e, file=sys.stderr)

"""

POST https://darpamemex:darpamemex@esc.memexproxy.com/dig-ht-latest/offer/_search?search_type=count
{
   "query": {
      "filtered": {
         "query": {
            "match_all": {}
         },
         "filter": {
            "nested": {
                           "path": "itemOffered",
                                  "filter": {
                  "exists": {
                     "field": "eyeColor"
                  }
               }
            }
         }
      }
   },

   "aggs": {
      "toplevelAgg": {
         "nested": {
            "path": "itemOffered"
         },
         "aggs": {
            "termAgg": {
               "terms": {
                  "field": "itemOffered.eyeColor",
                  "size" : 100
               }
            }
         }
      }
   }
}
"""
