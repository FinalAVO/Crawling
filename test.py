import pandas as pd
import xmltodict
import requests
import os
import json
import sys

url = "https://itunes.apple.com/kr/rss/customerreviews/id=1435757638/xml"


def appstore_crawler(url):
    result = []
    response = requests.get(url).content.decode('utf8')
    xml = xmltodict.parse(response)
    for i in range(len(xml['feed']['entry'])):
        result.append({
            'USER': xml['feed']['entry'][i]['author']['name'],
            'DATE': xml['feed']['entry'][i]['updated'],
            'STAR': int(xml['feed']['entry'][i]['im:rating']),
            'LIKE': int(xml['feed']['entry'][i]['im:voteSum']),
            'TITLE': xml['feed']['entry'][i]['title'],
            'REVIEW': xml['feed']['entry'][i]['content'][0]['#text']
        })
    print(result)
    res_df = pd.DataFrame(result)
    res_df.to_csv("./appstore_reviews.csv", encoding='utf-8-sig', index=False)


appstore_crawler(url)
