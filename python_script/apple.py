from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep

import pandas as pd
import requests
import os
import json
import sys
from datetime import datetime

# 마지막 페이지 인덱스 찾기
def get_page_index(_json):
    last_url = [_link['attributes']['href'] for _link in _json['feed']['link'] if (_link['attributes']['rel'] == 'last')][0]
    last_index = [int(_list.replace('page=', '')) for _list in last_url.split('/') if ('page=' in _list)][0]
    return last_index


# 찾은 app_id를 이용해 크롤링
def appstore_crawler(app_id, app_name, purpose, app_name_for_db):
    # 내가 찾고 싶어하는 어플이 맞는지 확인 절차가 필요
    if app_id == '':
        print("Wrong App Name")
        return

    url = "https://itunes.apple.com/kr/rss/customerreviews/id=" + app_id + "/json"

    response = requests.get(url)
    _json = response.json()

    last_index = get_page_index(_json)

    result = []

    # 모든 페이지 받아오기
    for idx in range(1, last_index+1):
        url = "https://itunes.apple.com/kr/rss/customerreviews/page=" + str(idx) + "/id=" + app_id + "/json"
        response = requests.get(url)
        _json = response.json()

        try:
            for i in range(len(_json['feed']['entry'])):
                review_fixed = _json['feed']['entry'][i]['content']['label'].replace("\n", " ")

                result.append({
                    'APP_NAME' : app_name,
                    'USER': _json['feed']['entry'][i]['author']['name']['label'],
                    'DATE': _json['feed']['entry'][i]['updated']['label'],
                    'STAR': int(_json['feed']['entry'][i]['im:rating']['label']),
                    'LIKE': int(_json['feed']['entry'][i]['im:voteSum']['label']),
                    'COMMENT': review_fixed,
                    'OS': "ios"
                })

        except KeyError:
            print("Wrong URL")
            return

    res_df = pd.DataFrame(result)
    res_df['DATE'] = pd.to_datetime(res_df['DATE'])
    res_df['DATE'] = res_df['DATE'].dt.tz_convert('Asia/Seoul')

    if purpose == "update":
        filename = "/data/Crawling/update/" + app_name_for_db + "_app_review_ios.csv"
        res_df.to_csv(filename, encoding='utf-8-sig', index=False)

    else:
        filename = "/data/Crawling/result/" + app_name_for_db + "_app_review_ios.csv"
        res_df.to_csv(filename, encoding='utf-8-sig', index=False)

    # pip3 install subprocess.run
    # chmod 755 mongo.sh
    # subprocess.run(["./shell_file/mongo.sh"], shell=True)
    print("Apple Done")
    return

# request에서 받아오는 parameter
# app_name = "페이스북"
app_id = sys.argv[1]
real_app_name = sys.argv[2]
purpose = sys.argv[3]
app_name_for_db = sys.argv[4]

# app_id, real_app_name = find_appid(app_name)
appstore_crawler(app_id, real_app_name, purpose, app_name_for_db)
