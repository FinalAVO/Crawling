import pandas as pd
import xmltodict
import requests
import os
import json
import sys
from datetime import datetime

# url = "https://itunes.apple.com/kr/rss/customerreviews/id=1435566757638/xml"


def appstore_crawler(url):
    if url == '':
        print("URL empty")
        return
    result = []
    response = requests.get(url).content.decode('utf8')
    xml = xmltodict.parse(response)

    while(True):
        try:
            for i in range(len(xml['feed']['entry'])):
                review_fixed = xml['feed']['entry'][i]['content'][0]['#text'].replace("\n", " ")
                result.append({
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
            #res_df.to_csv("./appstore_reviews.csv", encoding='utf-8-sig', index=False)
            return

        except KeyError:
            print("Wrong URL")
            return


url = sys.argv[1]

appstore_crawler(url)
