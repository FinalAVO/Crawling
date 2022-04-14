import time
import mysql.connector
import json

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

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

sql = "INSERT INTO test (ran) VALUES (1);"

cursor.execute(sql)
cnx.commit()
