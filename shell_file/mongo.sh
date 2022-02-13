#python3 /data/node/final/Crawling/selenium.py

mongoimport -d review -c apple --headerline --type csv /data/node/final/Crawling/data/appstore_review.csv

sleep 1

mongoexport -d review -c apple -f APP_ID,APP_NAME,USER,DATE,STAR,LIKE,TITLE,REVIEW --type=csv -o /data/node/final/Crawling/data/apple_review.csv
