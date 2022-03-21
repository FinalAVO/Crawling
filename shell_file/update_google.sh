#!/bin/sh

mongoimport --port 46171 -d review -c $1 --headerline --type csv --file /data/Crawling/update/${1}_app_review_android_updated.csv
