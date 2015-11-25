import os
import rdflib
from rdflib.util import guess_format

def loadModel(*pathnames):
    """Not general"""
    d = "data/ontology"
    if not pathnames:
        pathnames = [os.path.join(d, f) for f in os.listdir(d)]
    g = rdflib.Graph()
    for pathname in pathnames:
        fmt = guess_format(pathname)
        result = g.parse(pathname, format=fmt)
    return g
#               
#               
# # result = g.parse("http://www.w3.org/People/Berners-Lee/card")
# result1 = g.parse("data/ontology/memex-ontology.ttl", format="turtle")
# result2 = g.parse("data/ontology/rdf-schema.owl", format="xml")
# result3 = g.parse("data/ontology/skos.rdf", format="xml")
# 
# print("graph has %s statements." % len(g))
# # prints graph has 79 statements.
# 
# for subj, pred, obj in g:
#     if (subj, pred, obj) not in g:
#         raise Exception("It better be!")
# 
# s = g.serialize(format='n3', destination="/tmp/g.n3")

qres = g.query(
    """SELECT DISTINCT ?aname ?bname
       WHERE {
          ?a schema:telephone ?b .
          ?a foaf:name ?aname .
          ?b foaf:name ?bname .
       }""")

SELECT ?p ?o
{ 
  <http://nasa.dataincubator.org/spacecraft/1968-089A> ?p ?o
}

for row in qres:
    print("%s knows %s" % row)
