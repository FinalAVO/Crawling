#!/bin/sh

mongoimport --port 46171 -d review -c $1 --headerline --type csv --file /data/Crawling/result/app_review_android.csv
