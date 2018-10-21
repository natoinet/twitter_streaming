#!/bin/bash

# ./json-twitter_streaming.sh '<COLLECTION_NAME>' 'PATH'
# Run with ./friendsgraph.sh '2014-12-05' '/Users/blourp/src/tucat/tucat/twitter_extraction/export/'

DBNAME=$1
COLNAME=$2
EXP_PATH=$3
OUTPUT_FILES=$4
FIELDS=$5

mongoexport --quiet --host $MONGOHOST --username $MONGO_INITDB_ROOT_USERNAME --password $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin --db $DBNAME --collection $COLNAME --fields $MONGO_FIELDS_NODE --csv -o "$OUTPUT_FILES/archivo-node-$COLNAME.csv"
