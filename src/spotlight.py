import urllib.request
import sys

argLen = 1
sentence = ''

for arg in range(1,len(sys.argv)):
	sentence = sentence + "%20" + str(sys.argv[arg])

sentence = sentence.strip()

url = "http://spotlight.dbpedia.org/rest/annotate?text="+sentence+"&confidence=0.2&support=20"
request = urllib.request.Request(url)
request.add_header('Accept', 'application/json')
response = urllib.request.urlopen(request)
print (response.read().decode('utf-8'))
