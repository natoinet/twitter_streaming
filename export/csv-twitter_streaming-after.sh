#!/bin/bash

# ./json-twitter_streaming.sh '<COLLECTION_NAME>' 'PATH'
# Run with ./friendsgraph.sh '2014-12-05' '/Users/blourp/src/tucat/tucat/twitter_extraction/export/'

DBNAME=$1
COLNAME=$2
OUTPUT_FILES=$3
FIELDS=$4
BEFORE=$5
AFTER=$6

#echo "dbname:$DBNAME colname:$COLNAME outfile:$OUTPUT_FILES fields:$FIELDS mongohost:$MONGOHOST mongouname:$MONGO_INITDB_ROOT_USERNAME mongopwd:$MONGO_INITDB_ROOT_PASSWORD"
QUERY="{following : {\$ne : [ ]}, dt_created_at : { \$gte : new Date($BEFORE), \$lte : new Date($AFTER) }}"

mongoexport --quiet --host=$MONGOHOST --username=$MONGO_INITDB_ROOT_USERNAME --password=$MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase=admin --db=$DBNAME --collection=$COLNAME --fields=$MONGO_FIELDS_NODE --query="$QUERY" --type=csv -out="$OUTPUT_FILES/archivo-node-$COLNAME.csv"

echo "archivo-node-$COLNAME.csv"
