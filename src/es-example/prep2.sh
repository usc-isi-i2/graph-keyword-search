#!/bin/sh

INDEXNAME=twitter2

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
         },
         "children": {
           "type": "nested",
           "properties": {
             "name": {
               "type": "string",
               "index": "not_analyzed"
            },
             "school": {
               "type": "string",
               "index": "not_analyzed"
            }
          }
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
  "eyecolor": "blue",
  "children": [ {"name": "Alice", "school": "Aardvark"} ]
}'

curl -XPUT "http://localhost:9200/${INDEXNAME}/tweet/2?pretty=true" -d '{
  "fullname" : "Jane Doe",
  "text" : "Another twitter test ...",
  "eyecolor": "blue",
  "children": [ {"name": "Bob", "school": "Aardvark"},
                {"name": "Carole", "school": "Aardvark"},
                {"name": "Dan", "school": "Aardvark"},
                {"name": "Eve", "school": "Badger"} ]
}'

curl -XPUT "http://localhost:9200/${INDEXNAME}/tweet/3?pretty=true" -d '{
  "fullname" : "Robot3",
  "text" : "one two two three three three four four four four four four four five four five six seven eight nine",
  "eyecolor": "red",
  "children": [ {"name": "Ronald3", "school": "Factory"},
                {"name": "Rhonda3", "school": "Junkyard"}]
}'

curl -XPUT "http://localhost:9200/${INDEXNAME}/tweet/4?pretty=true" -d '{
  "fullname" : "Robot4",
  "text" : "one two two three three three four four four four four four four five four five six seven eight nine",
  "eyecolor": "red",
  "children": [ {"name": "Ronald4", "school": "Factory"},
                {"name": "Rhonda4", "school": "Junkyard"}]
}'

curl -XPUT "http://localhost:9200/${INDEXNAME}/tweet/5?pretty=true" -d '{
  "fullname" : "Robot5",
  "text" : "one two two three three three four four four four four four four five four five six seven eight nine",
  "eyecolor": "red",
  "children": [ {"name": "Ronald5", "school": "Factory"},
                {"name": "Rhonda5", "school": "Junkyard"}]
}'

curl -XPUT "http://localhost:9200/${INDEXNAME}/tweet/6?pretty=true" -d '{
  "fullname" : "Robot6",
  "text" : "one two two three three three four four four four four four four five four five six seven eight nine",
  "eyecolor": "red",
  "children": [ {"name": "Ronald6", "school": "Factory"},
                {"name": "Rhonda6", "school": "Junkyard"}]
}'

curl -XPUT "http://localhost:9200/${INDEXNAME}/tweet/7?pretty=true" -d '{
  "fullname" : "Robot7",
  "text" : "one two two three three three four four four four four four four five four five six seven eight nine",
  "eyecolor": "red",
  "children": [ {"name": "Ronald7", "school": "Factory"},
                {"name": "Rhonda7", "school": "Junkyard"}]
}'

curl -XPUT "http://localhost:9200/${INDEXNAME}/tweet/8?pretty=true" -d '{
  "fullname" : "Richard Bloggs",
  "text" : "one two",
  "eyecolor": "brown",
  "children": [ {"name": "Frank", "school": "Coyote"},
                {"name": "Glenda", "school": "Coyote"}]
}'