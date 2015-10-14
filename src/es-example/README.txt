Per document queries such as _termvector and _mtermvectors seem to
mostly be concerned with multiple occurrences of the (presumed)
repeated word in a single analyzed field.

POST http://localhost:9200/twitter/tweet/3/_termvector
{
}

looks good

Multi-term queries require that we specify all document IDs in the body

POST http://localhost:9200/twitter/tweet/_mtermvectors
{"ids" : ["1", "2"],
    "parameters": {
        "fields": ["text"],
        "term_statistics": "false"
    }
}

looks good

Not as meaningful for our more nominal/enumerable values.


https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-terms-aggregation.html
Term aggregation seems reasonable for our needs:

POST http://localhost:9200/twitter/tweet/_search?search_type=count
{
   "query": {
      "match_all": {}
   },
   "aggs": {
      "eyecolors": {
         "terms": {
            "field": "eyecolor"
         }
      }
   }
}

This is the nested equivalent:

POST http://localhost:9200/twitter2/tweet/_search?search_type=count
{
   "query": {
      "match_all": {}
   },
   "aggs": {
      "schools": {
         "nested": {
            "path": "children"
         },
         "aggs": {
            "aggname": {
               "terms": {
                "field": "children.school"}
            }
         }
      }
   }
}

giving result such as 

{
   "took": 1,
   "timed_out": false,
   "_shards": {
      "total": 1,
      "successful": 1,
      "failed": 0
   },
   "hits": {
      "total": 3,
      "max_score": 0,
      "hits": []
   },
   "aggregations": {
      "schools": {
         "doc_count": 7,
         "aggname": {
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
            "buckets": [
               {
                  "key": "Aardvark",
                  "doc_count": 4
               },
               {
                  "key": "Badger",
                  "doc_count": 1
               },
               {
                  "key": "Factory",
                  "doc_count": 1
               },
               {
                  "key": "Junkyard",
                  "doc_count": 1
               }
            ]
         }
      }
   }
}

For our domain, the query looks like:

POST https://darpamemex:darpamemex@esc.memexproxy.com/dig-ht-latest/offer/_search?search_type=count
{
   "query": {
      "match_all": {}
   },
   "aggs": {
      "itemOfferedAgg": {
         "nested": {
            "path": "itemOffered"
         },
         "aggs": {
            "termsSubAgg": {
               "terms": {
                  "field": "itemOffered.hairColor",
                  "size" : 20
               }
            }
         }
      }
   }
}

yielding

{
   "took": 1492,
   "timed_out": false,
   "_shards": {
      "total": 20,
      "successful": 20,
      "failed": 0
   },
   "hits": {
      "total": 19134836,
      "max_score": 0,
      "hits": []
   },
   "aggregations": {
      "itemOfferedAgg": {
         "doc_count": 19134836,
         "termsSubAgg": {
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 345,
            "buckets": [
               {
                  "key": "blond",
                  "doc_count": 813715
               },
               {
                  "key": "brown",
                  "doc_count": 605642
               },
               {
                  "key": "NONE",
                  "doc_count": 295217
               },
               {
                  "key": "black",
                  "doc_count": 199892
               },
               {
                  "key": "red",
                  "doc_count": 142948
               },
               {
                  "key": "blonde",
                  "doc_count": 27069
               },
               {
                  "key": "auburn",
                  "doc_count": 14732
               },
               {
                  "key": "gray",
                  "doc_count": 6624
               },
               {
                  "key": "brunette",
                  "doc_count": 3396
               },
               {
                  "key": "light brown",
                  "doc_count": 1813
               },
               {
                  "key": "dark brown",
                  "doc_count": 1350
               },
               {
                  "key": "other",
                  "doc_count": 862
               },
               {
                  "key": "chestnut",
                  "doc_count": 735
               },
               {
                  "key": "dirty brown",
                  "doc_count": 345
               },
               {
                  "key": "auburn red",
                  "doc_count": 259
               },
               {
                  "key": "auburnred",
                  "doc_count": 142
               },
               {
                  "key": "strawberry blonde",
                  "doc_count": 142
               },
               {
                  "key": "white",
                  "doc_count": 29
               },
               {
                  "key": "long",
                  "doc_count": 23
               },
               {
                  "key": "long brown",
                  "doc_count": 18
               }
            ]
         }
      }
   }
}

For the basis to make sense, the filter portion should be specified to include only those documents with the aggregated value?

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
      "itemOfferedAgg": {
         "nested": {
            "path": "itemOffered"
         },
         "aggs": {
            "termsSubAgg": {
               "terms": {
                  "field": "itemOffered.eyeColor",
                  "size" : 100
               }
            }
         }
      }
   }
}

TOPLEVEL objects in our ES are (with useful attributes):
webpage (root WebPage)
	mainEntity* -> offer
	publisher.name [y]
adultservice (root AdultService)
	eyeColor
	hairColor
	name
	personAge
	offers* -> offer
offer (root Offer)
	availableAtOrFrom* -> place/address
	itemOffered* -> adultservice
	priceSpecification.price [x]
	priceSpecification.billingIncrement [x]
	priceSpecification.unitCode [x]
	priceSpecification.name	[x]
phone (root PhoneNumber)
seller (root PersonOrOrganization)
email (root EmailAddress)

Thus non-toplevel objects include:
address
geo
priceSpecification
publisher

