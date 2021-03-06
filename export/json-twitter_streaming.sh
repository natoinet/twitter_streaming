#!/bin/bash

# ./json-twitter_streaming.sh '<COLLECTION_NAME>' 'PATH'
# Run with ./friendsgraph.sh '2014-12-05' '/Users/blourp/src/tucat/tucat/twitter_extraction/export/'

DBNAME=$1
COLNAME=$2
OUTPUT_FILES=$3

#echo "dbname:$DBNAME colname:$COLNAME outfile:$OUTPUT_FILES mongohost:$MONGOHOST mongouname:$MONGO_INITDB_ROOT_USERNAME mongopwd:$MONGO_INITDB_ROOT_PASSWORD"
mongoexport --quiet --host=$MONGOHOST --username=$MONGO_INITDB_ROOT_USERNAME --password=$MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase=admin --db=$DBNAME --collection=$COLNAME --type=json --out="$OUTPUT_FILES/twitter_streaming-$COLNAME.json"

echo "twitter_streaming-$COLNAME.json"
