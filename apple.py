from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep

import pandas as pd
import xmltodict
import requests
import os
import json
import sys
from datetime import datetime
import subprocess

# app_id 찾아주는 기능
def find_appid(app_name):
    option = Options()
    option.add_argument("disable-infobars")
    option.add_argument("disable-extensions")
    #option.add_argument("start-maximized")
    option.add_argument('--no-sandbox')
    option.add_argument('disable-gpu')
    option.add_argument('headless')

    # fnd.io site에 접속
    # 본인 chrome driver 위치 쓰기
    browser = webdriver.Chrome('/usr/bin/chromedriver', options=option)
    url = "https://fnd.io/#/kr/search?mediaType=all&term=" + app_name
    browser.get(url)

    # 해당 a tag 안 url 찾기 *** 광고성이 있다면 어떻게 처리할지 ***
    elem_url = browser.find_element(By.XPATH, '/html/body/div/div[1]/div[3]/div[3]/div[1]/div/ul/div/li[1]/div[1]/div/div/div[1]/a')
    app_url = elem_url.get_attribute('href')

    # url 분리해서 id찾기
    url_sep = app_url.split('/')
    app_id = url_sep[6][:url_sep[6].find("-")]

    # 실제 앱 이름 찾기
    elem_name = browser.find_element(By.XPATH, '/html/body/div/div[1]/div[3]/div[3]/div[1]/div/ul/div/li[1]/div[1]/div/div/div[1]/a/div/span')
    real_app_name = elem_name.get_attribute('title')

    return (app_id, real_app_name)

# 마지막 페이지 인덱스 찾기
def get_page_index(xml):
    last_url = [_link['@href'] for _link in xml['feed']['link'] if (_link['@rel'] == 'last')][0]
    last_index = [int(_list.replace('page=', '')) for _list in last_url.split('/') if ('page=' in _list)][0]
    return last_index



# 찾은 app_id를 이용해 크롤링
def appstore_crawler(app_id, app_name):
    # 내가 찾고 싶어하는 어플이 맞는지 확인 절차가 필요
    if app_id == '':
        print("Wrong App Name")
        return

    url = "https://itunes.apple.com/kr/rss/customerreviews/id=" + app_id + "/xml"
    response = requests.get(url).content.decode('utf8')
    xml = xmltodict.parse(response)

    last_index = get_page_index(xml)

    result = []

    # 모든 페이지 받아오기
    for idx in range(1, last_index+1):
        url = "https://itunes.apple.com/kr/rss/customerreviews/page=" + str(idx) + "/id=" + app_id + "/xml"
        response = requests.get(url).content.decode('utf8')
    # while(True):
        try:
            for i in range(len(xml['feed']['entry'])):
                review_fixed = xml['feed']['entry'][i]['content'][0]['#text'].replace("\n", " ")
                result.append({
                    'APP_ID': app_id,
                    'APP_NAME' : app_name,
                    'USER': xml['feed']['entry'][i]['author']['name'],
                    'DATE': xml['feed']['entry'][i]['updated'],
                    'STAR': int(xml['feed']['entry'][i]['im:rating']),
                    'LIKE': int(xml['feed']['entry'][i]['im:voteSum']),
                    'TITLE': xml['feed']['entry'][i]['title'],
                    # 'REVIEW': xml['feed']['entry'][i]['content'][0]['#text']
                    'REVIEW': review_fixed
                })

        except KeyError:
            print("Wrong URL")
            return

    # print(result)
    res_df = pd.DataFrame(result)
    res_df.to_csv("./data/appstore_review.csv", encoding='utf-8-sig', index=False)

    # pip3 install subprocess.run
    # chmod 755 mongo.sh
    subprocess.run(["./shell_file/mongo.sh"], shell=True)
    return

# request에서 받아오는 parameter
# app_name = "오딘"
app_name = sys.argv[1]

app_id, real_app_name = find_appid(app_name)
appstore_crawler(app_id, real_app_name)
