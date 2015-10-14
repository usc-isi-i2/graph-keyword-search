#!/bin/sh

INDEXNAME=twitter

curl -XDELETE "http://localhost:9200/${INDEXNAME}/"

curl -s -XPUT "http://localhost:9200/${INDEXNAME}/" -d '{
  "mappings": {
    "tweet": {
      "properties": {
        "text": {
          "type": "string",
          "term_vector": "yes",
          "store" : true,
          "index_analyzer" : "fulltext_analyzer"
         },
         "fullname": {
          "type": "string",
          "term_vector": "no",
          "index_analyzer" : "fulltext_analyzer"
        },
        "eyecolor": {
          "type": "string",
          "term_vector": "no",
          "index": "not_analyzed"
        }
      }
    }
  },
  "settings" : {
    "index" : {
      "number_of_shards" : 1,
      "number_of_replicas" : 0
    },
    "analysis": {
      "analyzer": {
        "fulltext_analyzer": {
          "type": "custom",
          "tokenizer": "whitespace",
          "filter": [
            "lowercase",
            "type_as_payload"
          ]
        }
      }
    }
  }
}'

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