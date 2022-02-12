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
    elem = browser.find_element(By.XPATH, '/html/body/div/div[1]/div[3]/div[3]/div[1]/div/ul/div/li[1]/div[1]/div/div/div[1]/a')
    app_url = elem.get_attribute('href')

    # url 분리해서 id찾기
    url_sep = app_url.split('/')
    app_id = url_sep[6][:url_sep[6].find("-")]
    return app_id

# 찾은 app_id를 이용해 크롤링
def appstore_crawler(app_id, app_name):
    # 내가 찾고 싶어하는 어플이 맞는지 확인 절차가 필요
    if app_id == '':
        print("Wrong App Name")
        return

    url = "https://itunes.apple.com/kr/rss/customerreviews/id=" + app_id + "/xml"
    response = requests.get(url).content.decode('utf8')
    xml = xmltodict.parse(response)

    result = []

    while(True):
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

            # 이제는 response에 넘기는게 아니라 mongo에 저장 후에 다른 lightsail로 보내는 기능을 추가
            print(result)
            #res_df = pd.DataFrame(result)
            #res_df.to_csv("./data/appstore_reviews.csv", encoding='utf-8-sig', index=False)
            return

        except KeyError:
            print("Wrong URL")
            return

# request에서 받아오는 parameter
app_name = "오딘"
# app_name = sys.argv[1]

app_id = find_appid(app_name)
appstore_crawler(app_id, app_name)
