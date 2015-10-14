#!/usr/bin/env python

import sys, os
import networkx as nx
from pprint import pprint
import json

OUTPUT_ROOT = "/Users/philpot/Documents/project/graph-keyword-search/src/es-example/cache"

def loadVocab(pathdesc, root=OUTPUT_ROOT):
    pathname = os.path.join(root, pathdesc  + ".json")
    # print("load from {}".format(pathname), file=sys.stderr)
    with open(pathname, 'r') as f:
        j = json.load(f)
    # dict of (value, count)
    byCount = sorted([(v,k) for (k,v) in j['histo'].items()], reverse=True)
    return [t[1] for t in byCount]

z = loadVocab('seller_telephone_name')
pprint(z)

g = nx.DiGraph()

g.add_node('seller', nodeType='Class', className='PersonOrOrganization')

g.add_node('phone', nodeType='Class', className='PhoneNumber')
g.add_edge('seller', 'phone', edgeType='ObjectProperty', relationName='telephone')

g.add_node('phone.name', nodeType='leaf', values=loadVocab('seller_telephone_name'))
g.add_edge('phone', 'phone.name', edgeType='DataProperty', relationName='name')

g.add_node('email', nodeType='Class', className='EmailAddress')
# for now this ES query doesn't work
# g.add_node('email.name', nodeType='leaf', values=loadVocab('seller_email_name'))
# so use flat data instead
g.add_node('email.name', nodeType='leaf', values=loadVocab('email_name'))

g.add_node('offer', nodeType='Class', className='Offer')
g.add_edge('offer', 'seller', edgeType='ObjectProperty', relationName='seller')
g.add_edge('seller', 'offer', edgeType='ObjectProperty', relationName='makesOffer')

g.add_node('priceSpecification', nodeType='Class', className='PriceSpecification')
g.add_node('priceSpecification.billingIncrement', nodeType='Leaf', values=loadVocab('offer_priceSpecification_billingIncrement'))
g.add_node('priceSpecification.price', nodeType='Leaf', values=loadVocab('offer_priceSpecification_price'))
g.add_node('priceSpecification.name', nodeType='Leaf', values=loadVocab('offer_priceSpecification_name'))
g.add_node('priceSpecification.unitCode', nodeType='Leaf', values=loadVocab('offer_priceSpecification_unitCode'))

g.add_node('adultservice', nodeType='Class', className='AdultService')
g.add_node('adultservice.eyeColor', nodeType='leaf', values=loadVocab('adultservice_eyeColor'))
g.add_edge('adultservice', 'adultservice.eyeColor', edgeType='DataProperty', relationName='eyeColor')
g.add_node('adultservice.hairColor', nodeType='leaf', values=loadVocab('adultservice_hairColor'))
g.add_edge('adultservice', 'adultservice.hairColor', edgeType='DataProperty', relationName='hairColor')
g.add_node('adultservice.name', nodeType='leaf', values=loadVocab('adultservice_name'))
g.add_edge('adultservice', 'adultservice.name', edgeType='DataProperty', relationName='name')
g.add_node('adultservice.personAge', nodeType='leaf', values=loadVocab('adultservice_personAge'))
g.add_edge('adultservice', 'adultservice.personAge', edgeType='DataProperty', relationName='personAge')

g.add_edge('offer', 'adultservice', edgeType='ObjectProperty', relationName='itemOffered')
g.add_edge('adultservice', 'offer', edgeType='ObjectProperty', relationName='offers')

g.add_node('place', nodeType='Class', className='Place')
g.add_node('postaladdress', nodeType='Class', className='PostalAddress')

g.add_edge('offer', 'place', edgeType='ObjectProperty', relationName='availableAtOrFrom')
g.add_edge('place', 'postaladdress', edgeType='ObjectProperty', relationName='address')

g.add_node('postaladdress.addressLocality', nodeType='leaf', values=loadVocab('offer_availableAtOrFrom_address_addressLocality'))
g.add_node('postaladdress.addressRegion', nodeType='leaf', values=loadVocab('offer_availableAtOrFrom_address_addressRegion'))
g.add_node('postaladdress.addressCountry', nodeType='leaf', values=loadVocab('offer_availableAtOrFrom_address_addressCountry'))


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
