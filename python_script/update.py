import pymysql
import mysql.connector
import pymongo
from pymongo import MongoClient
import pandas as pd
import json
import os
import warnings
import sys
import subprocess
import time
from datetime import datetime, timedelta
warnings.filterwarnings("ignore")

# Update Apple
def update_apple(apple_app_id, real_app_name, app_name_for_db, crawled_date):

    subprocess.call(['python3', '/data/Crawling/python_script/apple.py', apple_app_id, real_app_name, "update", app_name_for_db])
    time.sleep(1)
    filename = "/data/Crawling/update/" + app_name_for_db + "_app_review_ios.csv"
    new_review = pd.read_csv(filename)
    new_review['DATE'] = pd.to_datetime(new_review['DATE']).dt.tz_localize(None)

    df_updated = new_review[new_review["DATE"] > crawled_date]

    if len(df_updated) == 0:
        return
    else:
        filename = "/data/Crawling/update/" + app_name_for_db + "_app_review_ios_updated.csv"
        df_updated.to_csv(filename, encoding='utf-8-sig', index=False)
        time.sleep(1)
        subprocess.call(['sh', '/data/Crawling/shell_file/update_apple.sh', app_name_for_db])
        time.sleep(1)

# Update Google
def update_google(google_app_id, app_name_for_db):

    # MongoDB 연결
    with open('/data/Crawling/config/mongo.json') as f:
        mongo_config = json.load(f)
        f.close()

    client = MongoClient(mongo_config["host"])
    db = client["review"]
    mongodb_col = db[app_name_for_db]

    # mongoDB에 있는 마지막 최근 날짜에서 하루 빼기
    mongo_date = pd.DataFrame(list(mongodb_col.find({'OS' : 'android'}, { 'DATE': 1 }).sort('DATE', -1).limit(1)))
    mongo_date['DATE'] = pd.to_datetime(mongo_date['DATE'])
    new_start_date = str(mongo_date['DATE'][0] - timedelta(days=2))
    # print(new_start_date)
    # new_start_date = '2022-03-18'
    # new_end_date = '2022-03-20'
    # 18 ~ 19
    # , '$lte' : new_end_date

    # 비교할 기존 데이터
    mongo_df_review_google = pd.DataFrame(list(mongodb_col.find({'OS' : 'android', 'DATE' : { '$gte' : new_start_date }} ).sort('DATE', -1)))
    mongo_df_review_google["DATE"] = pd.to_datetime(mongo_df_review_google["DATE"])
    mongo_df_review_google = mongo_df_review_google.loc[:, mongo_df_review_google.columns!='_id']

    subprocess.call(['python3', '/data/Crawling/python_script/google.py', google_app_id, "update", app_name_for_db])
    # time.sleep(1)
    filename = "/data/Crawling/update/" + app_name_for_db + "_app_review_android.csv"
    new_review_google = pd.read_csv(filename)
    new_review_google["DATE"] = pd.to_datetime(new_review_google["DATE"])
    # .dt.tz_localize(None)
    new_filtered = new_review_google[new_review_google["DATE"] >= new_start_date]

    # pd_diff = pd.concat([mongo_df_review_google, new_filtered]).drop_duplicates(keep=False)
    pd_diff = mongo_df_review_google.merge(new_filtered, how = 'outer' ,indicator=True).loc[lambda x : x['_merge']=='right_only']
    pd_diff = pd_diff.loc[:, pd_diff.columns!='_merge']

    # print(pd_diff)

    if len(pd_diff) == 0:
        return
    else:
        filename = "/data/Crawling/update/" + app_name_for_db + "_app_review_android_updated.csv"
        pd_diff.to_csv(filename, encoding='utf-8-sig', index=False)
        time.sleep(1)
        subprocess.call(['sh', '/data/Crawling/shell_file/update_google.sh', app_name_for_db])
        time.sleep(1)

# RDS 연결
with open('/data/Crawling/config/rds_config.json') as f:
    rds_config = json.load(f)
    f.close()

config = {
  'user': rds_config["user"],
  'password': rds_config["password"],
  'host': rds_config["host"],
  'database': rds_config["database"],
  'raise_on_warnings': rds_config["raise_on_warnings"]
}

# crawling_log 가져오기
# mysqlCon = pymysql.connect(host="mymysql.csstqmpesreg.ap-northeast-2.rds.amazonaws.com", user="admin", password="abcd1234", db="avo_review")

cnx = mysql.connector.connect(**config)

sql = "SELECT * FROM crawling_log"
log = pd.read_sql_query(sql, cnx)

for idx in range(len(log)):
    app_name_for_db = log.iloc[idx][0]
    crawled_date = log.iloc[idx][1]
    apple_app_id = log.iloc[idx][2]
    google_app_id = log.iloc[idx][3]
    real_app_name = log.iloc[idx][4]

    update_apple(apple_app_id, real_app_name, app_name_for_db, crawled_date)
    # update_google(google_app_id, app_name_for_db)
