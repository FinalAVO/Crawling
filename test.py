import pandas as pd
import xmltodict
import requests
import os
import json
import sys
from datetime import datetime


def appstore_crawler(url):
    if url == '':
        print("URL empty")
        return
    result = []
    response = requests.get(url).content.decode('utf8')
    xml = xmltodict.parse(response)

    # id값 별도 저장
    id_index = url.find("id=") + 3
    xml_index = url.find("/xml")
    id_value = url[id_index:xml_index]

    while(True):
        try:
            for i in range(len(xml['feed']['entry'])):
                review_fixed = xml['feed']['entry'][i]['content'][0]['#text'].replace("\n", " ")
                result.append({
                    'APP_ID': id_value,
                    'APP_NAME' : "NO_NAME",
                    'USER': xml['feed']['entry'][i]['author']['name'],
                    'DATE': xml['feed']['entry'][i]['updated'],
                    'STAR': int(xml['feed']['entry'][i]['im:rating']),
                    'LIKE': int(xml['feed']['entry'][i]['im:voteSum']),
                    'TITLE': xml['feed']['entry'][i]['title'],
                    # 'REVIEW': xml['feed']['entry'][i]['content'][0]['#text']
                    'REVIEW': review_fixed
                })

            print(result)
            #res_df = pd.DataFrame(result)
            #res_df.to_csv("./data/appstore_reviews.csv", encoding='utf-8-sig', index=False)
            return

        except KeyError:
            print("Wrong URL")
            return

# url = "https://itunes.apple.com/kr/rss/customerreviews/id=1520354659/xml"
url = sys.argv[1]

appstore_crawler(url)
