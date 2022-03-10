import pymongo
from pymongo import MongoClient
import pandas as pd


collection_name = "A카카오톡KakaoTalk"
client = MongoClient("mongodb://3.34.14.98:46171")
db = client["review"]
db_col = db[collection_name]
df = pd.DataFrame(list(db_col.find()))


client.close()
