from selenium import webdriver
from bs4 import BeautifulSoup
import time, os, sys
import pandas as pd
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import json
import requests
import urllib.parse
import urllib.request

option = Options()
option.add_argument("disable-infobars")
option.add_argument("disable-extensions")
# option.add_argument("start-maximized")
option.add_argument('—no-sandbox')
option.add_argument('disable-gpu')
option.add_argument('headless')

def find_app_id(app_name):

    ## APPLE APP_ID

    # link2 = "https://fnd.io/#/kr/search?mediaType=all&term=" + app_name
    # driver.get(link2)

    # 해당 a tag 안 url 찾기 *** 광고성이 있다면 어떻게 처리할지 ***
    # try:
    #     elem_url = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[3]/div[3]/div[1]/div/ul/div/li[1]/div[1]/div/div/div[1]/a')
    # except:
    #     elem_url = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[3]/div[2]/div[1]/div/ul/div/li[1]/div[1]/div/div/div[1]/a')
    #
    # app_url = elem_url.get_attribute('href')

    url = 'https://itunes.apple.com/search'
    values = {'term' : app_name,
              'country' : 'KR',
              'media' : 'software',
              'limit' : '1'}

    data = urllib.parse.urlencode(values)
    data = data.encode('utf-8') # data should be bytes
    req = urllib.request.Request(url, data)
    with urllib.request.urlopen(req) as response:
        the_page = response.read()
    the_page = json.loads(the_page)

    # url 분리해서 id찾기
    app_id2 = the_page['results'][0]['trackId']
    # url_sep = app_url.split('/')
    # app_id2 = url_sep[6][:url_sep[6].find("-")]

    # 실제 앱 이름 찾기
    # try:
    #     elem_name = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[3]/div[3]/div[1]/div/ul/div/li[1]/div[1]/div/div/div[1]/a/div/span')
    # except:
    #     elem_name = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[3]/div[2]/div[1]/div/ul/div/li[1]/div[1]/div/div/div[1]/a/div/span')
    #
    # real_app_name = elem_name.get_attribute('title')
    real_app_name = the_page['results'][0]['trackName']

    r_app_name =  'A' + real_app_name
    characters = '~!@#$%^&*()_+:.,/?'
    app = r_app_name.replace(' ', '')
    for i in range(len(characters)):
        app = app.replace(characters[i],'')


    # GOOGLE APP_ID
    driver = webdriver.Chrome('./chromedriver', options=option)
    link = "https://play.google.com/store/search?q=" + str(app[1:]) + "&c=apps&hl=ko&gl=KR"
    driver.get(link)

    flag = False
    for i in range(1,10):
        try:
            elem_url = driver.find_element(By.XPATH, '/html/body/c-wiz[' + str(i) + ']/div/div/c-wiz/c-wiz[1]/c-wiz/section/div/div/a')
            flag=True
            break
        except:
            continue

    if(flag == False):
        for i in range(1,10):
            try:
                elem_url = driver.find_element(By.XPATH, '/html/body/c-wiz[' + str(i) + ']/div/div/c-wiz/c-wiz[1]/c-wiz/section/div/div/div/div[1]/div[1]/div/div/div/a')
                flag=True
                break
            except:
                continue

    if(flag == False):
        for i in range(1,10):
            try:
                elem_url = driver.find_element(By.XPATH, '/html/body/c-wiz[' + str(i) + ']/div/div/c-wiz/c-wiz/c-wiz/section/div/div/div[1]/div/div/div/a')
                break
            except:
                continue

    app_url = elem_url.get_attribute('href')

    url_sep = app_url.split('/')
    app_id = url_sep[5][url_sep[5].find("=")+1:]




    return (app_id, app_id2, app, real_app_name)

# app_name = "오딘"
app_name = sys.argv[1]

app_id, app_id2, app, real_app_name = find_app_id(app_name)

print(app_id2)
print(app_id)
print(app)
print(real_app_name)
