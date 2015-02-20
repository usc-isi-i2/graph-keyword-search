import urllib.request
import sys


word1 = input(" Enter the word1 : ")
word2 = input(" Enter the word2 : ")

url = "http://vmdeb20.deri.ie:8890/esaservice?task=esa&term1="+word1+'&term2='+word2
request = urllib.request.Request(url)
response = urllib.request.urlopen(request)

print (response.read().decode('utf-8'))