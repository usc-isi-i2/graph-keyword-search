#!/usr/bin/env python

import sys, os
from networkx import DiGraph
from pprint import pprint
import json
import re
import word2vec
from collections import defaultdict

LEAF_VOCAB_CACHE = "/Users/philpot/Documents/project/graph-keyword-search/src/es-example/cache"

def loadLeafVocab(pathdesc, root=LEAF_VOCAB_CACHE):
    pathname = os.path.join(root, pathdesc  + ".json")
    # print("load from {}".format(pathname), file=sys.stderr)
    with open(pathname, 'r') as f:
        j = json.load(f)
    # dict of (value, count)
    byCount = sorted([(v,k) for (k,v) in j['histo'].items()], reverse=True)
    return [t[1] for t in byCount]

# http://stackoverflow.com/a/9283563/2077242
def camelCaseWords(label):
    label = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', label)
    return label

class KGraph(DiGraph):
    def __init__(self, domainType='ht'):
        super(KGraph, self).__init__()
        if domainType == 'ht':
   
            self.add_node('seller', nodeType='Class', className='PersonOrOrganization')
        
            self.add_node('phone', nodeType='Class', className='PhoneNumber')
            self.add_edge('seller', 'phone', edgeType='ObjectProperty', relationName='telephone')
        
            self.add_node('phone.name', nodeType='leaf', values=loadLeafVocab('seller_telephone_name'), vocabDescriptor='seller_telephone_name')
            self.add_edge('phone', 'phone.name', edgeType='DataProperty', relationName='name')
        
            self.add_node('email', nodeType='Class', className='EmailAddress')
            # for now this ES query doesn't work
            # self.add_node('email.name', nodeType='leaf', values=loadLeafVocab('seller_email_name'), vocabDescriptor='seller_email_name')
            # so use flat data instead
            self.add_node('email.name', nodeType='leaf', values=loadLeafVocab('email_name'), vocabDescriptor='email_name')
        
            self.add_node('offer', nodeType='Class', className='Offer')
            self.add_edge('offer', 'seller', edgeType='ObjectProperty', relationName='seller')
            self.add_edge('seller', 'offer', edgeType='ObjectProperty', relationName='makesOffer')
        
            self.add_node('priceSpecification', nodeType='Class', className='PriceSpecification')
            self.add_node('priceSpecification.billingIncrement', nodeType='Leaf', values=loadLeafVocab('offer_priceSpecification_billingIncrement'), vocabDescriptor='offer_priceSpecification_billingIncrement')
            self.add_node('priceSpecification.price', nodeType='Leaf', values=loadLeafVocab('offer_priceSpecification_price'), vocabDescriptor='offer_priceSpecification_price')
            self.add_node('priceSpecification.name', nodeType='Leaf', values=loadLeafVocab('offer_priceSpecification_name'), vocabDescriptor='offer_priceSpecification_name')
            self.add_node('priceSpecification.unitCode', nodeType='Leaf', values=loadLeafVocab('offer_priceSpecification_unitCode'), vocabDescriptor='offer_priceSpecification_unitCode')
        
            self.add_node('adultservice', nodeType='Class', className='AdultService')
            self.add_node('adultservice.eyeColor', nodeType='leaf', values=loadLeafVocab('adultservice_eyeColor'), vocabDescriptor='adultservice_eyeColor')
            self.add_edge('adultservice', 'adultservice.eyeColor', edgeType='DataProperty', relationName='eyeColor')
            self.add_node('adultservice.hairColor', nodeType='leaf', values=loadLeafVocab('adultservice_hairColor'), vocabDescriptor='adultservice_hairColor')
            self.add_edge('adultservice', 'adultservice.hairColor', edgeType='DataProperty', relationName='hairColor')
            self.add_node('adultservice.name', nodeType='leaf', values=loadLeafVocab('adultservice_name'), vocabDescriptor='adultservice_name')
            self.add_edge('adultservice', 'adultservice.name', edgeType='DataProperty', relationName='name')
            self.add_node('adultservice.personAge', nodeType='leaf', values=loadLeafVocab('adultservice_personAge'), vocabDescriptor='adultservice_personAge')
            self.add_edge('adultservice', 'adultservice.personAge', edgeType='DataProperty', relationName='personAge')
        
            self.add_edge('offer', 'adultservice', edgeType='ObjectProperty', relationName='itemOffered')
            self.add_edge('adultservice', 'offer', edgeType='ObjectProperty', relationName='offers')
        
            self.add_node('place', nodeType='Class', className='Place')
            self.add_node('postaladdress', nodeType='Class', className='PostalAddress')
        
            self.add_edge('offer', 'place', edgeType='ObjectProperty', relationName='availableAtOrFrom')
            self.add_edge('place', 'postaladdress', edgeType='ObjectProperty', relationName='address')
        
            self.add_node('postaladdress.addressLocality', nodeType='leaf', values=loadLeafVocab('offer_availableAtOrFrom_address_addressLocality'), vocabDescriptor='offer_availableAtOrFrom_address_addressLocality')
            self.add_node('postaladdress.addressRegion', nodeType='leaf', values=loadLeafVocab('offer_availableAtOrFrom_address_addressRegion'), vocabDescriptor='offer_availableAtOrFrom_address_addressRegion')
            self.add_node('postaladdress.addressCountry', nodeType='leaf', values=loadLeafVocab('offer_availableAtOrFrom_address_addressCountry'), vocabDescriptor='offer_availableAtOrFrom_address_addressCountry')

    def populateValues(self, nodeOrEdge):
        try:
            node = nodeOrEdge
            nodeType = self.node[node]['nodeType']
            if nodeType == 'leaf':
                self.populateLeafNode(node)
            elif nodeType == 'Class':
                self.populateClassNode(node)
        except Exception as e:
            edge = nodeOrEdge
            (node1, node2) = edge
            edgeType = self.edge[node1][node2]['edgeType']
            if edgeType == 'ObjectProperty':
                self.populateRelationEdge(edge)
            elif edgeType == 'DataProperty':
                self.populateAttributeEdge(edge)
    
    def populateLeafNode(self, node):
        self.node[node]['values'] = loadLeafVocab(self.node[node]['vocabDescriptor'])
    
    def populateClassNode(self, node):
        self.node[node]['values'] = list(set([node, self.node[node]['className']]))
    
    def populateRelationEdge(self, edge):
        (node1, node2) = edge
        self.edge[node1][node2]['values'] = [self.edge[node1][node2]['relationName']]
    
    def populateAttributeEdge(self, edge):
        (node1, node2) = edge
        self.edge[node1][node2]['values'] = [self.edge[node1][node2]['relationName']]    
    
    def populateAll(self):
        for node in self.nodes():
            self.populateValues(node)
        for edge in self.edges():
            self.populateValues(edge)


"""SPECS=[ {"docType": "adultservice", "fieldName": "eyeColor", "size": 10},
        {"docType": "adultservice", "fieldName": "hairColor", "size": 10},
        {"docType": "adultservice", "fieldName": "name", "size": 200},
        {"docType": "adultservice", "fieldName": "personAge", "size": 20},

        {"docType": "phone", "fieldName": "name", "size": 200},
        
        {"docType": "email", "fieldName": "name", "size": 200},

        {"docType": "webpage", "innerPath": "publisher", "fieldName": "name", "size": 200},
        # Ignore webpage.description, webpage.dateCreated

        # Ignore offer.identifier
        {"docType": "offer", "innerPath": "priceSpecification", "fieldName": "billingIncrement", "size": 10},
        {"docType": "offer", "innerPath": "priceSpecification", "fieldName": "price", "size": 200},
        {"docType": "offer", "innerPath": "priceSpecification", "fieldName": "name", "size": 200},
        {"docType": "offer", "innerPath": "priceSpecification", "fieldName": "unitCode", "size": 10},
        {"docType": "offer", "innerPath": "availableAtOrFrom.address", "fieldName": "addressLocality", "size": 200},
        {"docType": "offer", "innerPath": "availableAtOrFrom.address", "fieldName": "addressRegion", "size": 200},
        {"docType": "offer", "innerPath": "availableAtOrFrom.address", "fieldName": "addressCountry", "size": 200},
        # Ignore offer.availableAtOrFrom.name
        # Ignore offer.availableAtOrFrom.geo.lat, offer.availableAtOrFrom.geo.lon
    ]"""
    
g = None
    
def htGraph():
    global g
    g = KGraph(domainType='ht')
    g.populateAll()
    return g
