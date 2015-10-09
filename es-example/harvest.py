#!/usr/bin/env python3

from elasticsearch import Elasticsearch
import pprint

es = Elasticsearch(
    [
        'https://darpamemex:darpamemex@esc.memexproxy.com/' # dig-ht-latest/offer
        # 'http://user:secret@localhost:9200/', 
        ],
    verify_certs=False
    )

def makeBody(fieldName="name", innerObject="itemOffered", size=10):
    return {
        "query": {
            "match_all": {}
            },
        "aggs": {
            "itemOfferedAgg": {
                "nested": {
                    "path": innerObject
                    },
                "aggs": {
                    "termsSubAgg": {
                        "terms": {
                            "field": "{}.{}".format(innerObject, fieldName),
                            "size" : size
                            }
                        }
                    }
                }
            }
        }


def test(fieldName="name", innerObject="itemOffered", size=10):
    # res = es.search(index="test-index", body={"query": {"match_all": {}}})
    body=makeBody(fieldName=fieldName, innerObject=innerObject, size=size)
    pprint.pprint(body)
    res = es.search(index="dig-ht-latest",
                    doc_type="offer",
                    body=body,
                    search_type="count")
    print("Got %d Hits:" % res['hits']['total'])
    pprint.pprint(res)
    for hit in res['aggregations']['itemOfferedAgg']['termsSubAgg']['buckets']:
        # print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])
        print(hit)

"""
{'_shards': {'failed': 0, 'successful': 20, 'total': 20},
 'aggregations': {'itemOfferedAgg': {'doc_count': 19134836,
                                     'termsSubAgg': {'buckets': [{'doc_count': 18104,
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

def test2(docType="webpage",fieldName="addressCountry", innerPath="mainEntity.availableAtOrFrom.address", size=10):
    # res = es.search(index="test-index", body={"query": {"match_all": {}}})
    body=makeBody(fieldName=fieldName, innerObject=innerPath, size=size)
    # pprint.pprint(body)
    result = es.search(index="dig-ht-latest",
                       doc_type=docType,
                       body=body,
                       search_type="count")
    # print("Got %d Hits:" % res['hits']['total'])
    # pprint.pprint(res)
    termsSubAgg = result['aggregations']['itemOfferedAgg']['termsSubAgg']
    report = {"docType": docType,
              "fieldName": fieldName,
              "innerPath": innerPath,
              "size": size,
              # use this later to get hitsTotal, sum_other_doc_count if needed
              "result": result,
              "histo": {}}
    for bucket in termsSubAgg['buckets']:
        pprint.pprint(bucket)
        report["histo"][bucket["key"]] = bucket["doc_count"]
    return report

r = test2()
pprint.pprint(r)

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
"""
