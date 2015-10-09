#!/usr/bin/env python3

from elasticsearch import Elasticsearch
from pprint import pprint
import json
import os

es = Elasticsearch(
    [
        'https://darpamemex:darpamemex@esc.memexproxy.com/' # dig-ht-latest/offer
        # 'http://user:secret@localhost:9200/', 
        ],
    verify_certs=False
    )

def makeBody(fieldName="name", innerPath="itemOffered", size=10):
    return {
        "query": {
            "match_all": {}
            },
        "aggs": {
            "itemOfferedAgg": {
                "nested": {
                    "path": innerPath
                    },
                "aggs": {
                    "termsSubAgg": {
                        "terms": {
                            "field": "{}.{}".format(innerPath, fieldName),
                            "size" : size
                            }
                        }
                    }
                }
            }
        }


def test(fieldName="name", innerPath="itemOffered", size=10):
    # res = es.search(index="test-index", body={"query": {"match_all": {}}})
    body=makeBody(fieldName=fieldName, innerPath=innerPath, size=size)
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

def harvest(docType="webpage",fieldName="addressCountry", innerPath="mainEntity.availableAtOrFrom.address", size=10):
    # res = es.search(index="test-index", body={"query": {"match_all": {}}})
    body=makeBody(fieldName=fieldName, innerPath=innerPath, size=size)
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
        report["histo"][bucket["key"]] = bucket["doc_count"]
    return report

def outputPathname(docType="webpage", innerPath="mainEntity.availableAtOrFrom.address", fieldName="addressCountry", root="/tmp", **kwargs):
    return os.path.join(root, "{}_{}_{}.json".format(docType, innerPath.replace('.', '_'), fieldName))


SPECS=[{"docType": "webpage", "innerPath": "mainEntity.availableAtOrFrom.address", "fieldName": "addressCountry", "size": 20},
       {"docType": "offer", "innerPath": "itemOffered", "fieldName": "name", "size": 20}]

def harvestToFile(spec):
    outPath = None
    try:
        outPath = outputPathname(**spec)
    except:
        pass
    try:
        h = harvest(**spec)
        with open(outPath, 'w') as f:
            json.dump(h, f, indent=4, sort_keys=True)
    except Exception as e:
        print("Error [{}] during processing of {}".format(e, outPath))


for spec in SPECS:
    harvestToFile(spec)
    

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
