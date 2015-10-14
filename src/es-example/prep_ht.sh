#!/bin/sh

INDEXNAME=ht

pushd $PROJ/dig-elasticsearch
git pull
mapping=$PROJ/dig-elasticsearch/types/webpage/esMapping-dig-ht-DT.json
popd

curl -k -XPUT "https://darpamemex:darpamemex@esc.memexproxy.com/${indexName}" -d @$mapping


curl -XDELETE "http://localhost:9200/${INDEXNAME}/"

curl -s -XPUT "http://localhost:9200/${INDEXNAME}/" -d @$mapping

curl -XPUT "http://localhost:9200/${INDEXNAME}/tweet/1?pretty=true" -d '{
  "fullname" : "John Doe",
  "text" : "twitter test test test ",
  "eyecolor": "blue"
}'

curl -XPUT "http://localhost:9200/${INDEXNAME}/tweet/2?pretty=true" -d '{
  "fullname" : "Jane Doe",
  "text" : "Another twitter test ...",
  "eyecolor": "blue"
}'

curl -XPUT "http://localhost:9200/${INDEXNAME}/tweet/3?pretty=true" -d '{
  "fullname" : "Robot",
  "text" : "one two two three three three four four four four four four four five four five six seven eight nine",
  "eyecolor": "red"
}'