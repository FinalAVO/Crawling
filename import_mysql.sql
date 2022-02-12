load data local infile '/data/node/final/Crawling/data/app_review.csv'
into table review
FIELDS TERMINATED BY ','
IGNORE 1 ROWS;
