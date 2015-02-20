import urllib.request
import sys

argLen = 1
sentence = ''

sentence = input(" Enter the keyword query : ")
sentence = sentence.replace(' ','%20')

url = "http://spotlight.dbpedia.org/rest/annotate?text="+sentence+"&confidence=0.2&support=20"
#url = "http://spotlight.dbpedia.org/rest/annotate?types=DBPedia:Person&text="+sentence+"&confidence=0.2&support=20"
#print(url)
request = urllib.request.Request(url)
request.add_header('Accept', 'application/json')
response = urllib.request.urlopen(request)
print (response.read().decode('utf-8'))
