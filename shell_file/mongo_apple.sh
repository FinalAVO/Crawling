#!/bin/sh

# query="db.${1}.drop()"

# mongo --eval $query review

mongoimport --port 46171 -d review -c $1 --headerline --type csv --file /data/Crawling/result/${1}_app_review_ios.csv

# mongoexport --port 46171 -d review -c $1 -f COMMENT --type=csv -o /data/Crawling/result/app_review_final.csv
