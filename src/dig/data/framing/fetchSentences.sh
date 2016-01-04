#!/bin/sh

HERE=$(dirname "$0")

ENDPOINT=esc.memexproxy.com
USERNAME=darpamemex
PASSWORD=darpamemex
IDXNAME="dig-ht-latest"
TYPE=$1
SIZE=1

QUERY=$(jq ".size=$SIZE" query.json)
curl -s -g -k -XGET "https://$USERNAME:$PASSWORD@$ENDPOINT/$IDXNAME/$TYPE/_search" -d "$QUERY" | jq ".hits.hits[]._source" > esdoc-$TYPE.json
