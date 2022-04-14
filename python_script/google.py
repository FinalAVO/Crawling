from selenium import webdriver
from bs4 import BeautifulSoup
import time, os, sys
import pandas as pd
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import warnings
warnings.filterwarnings("ignore")

option = Options()
option.add_argument("disable-infobars")
option.add_argument("disable-extensions")
option.add_argument('—no-sandbox')
option.add_argument('disable-gpu')
option.add_argument('headless')


#리뷰 링크 접속
def playstore_crawler(app_id, purpose, app_name_for_db):
    driver = webdriver.Chrome('/data/Crawling/chromedriver', options=option)
    driver.set_window_position(0, 0)
    driver.set_window_size(1500, 900)
    link = 'https://play.google.com/store/apps/details?id=' + str(app_id) + '&hl=ko&gl=US&showAllReviews=true'
    driver.get(link)

    os.makedirs('result', exist_ok=True)

    box = driver.find_element_by_xpath('/html/body/div[1]/div[4]/c-wiz/div/div[2]/div/div/main/div/div[1]/div[2]/c-wiz/div[1]/div')
    box.click()

    time.sleep(1)

    box2 = driver.find_element_by_xpath('/html/body/div[1]/div[4]/c-wiz/div/div[2]/div/div/main/div/div[1]/div[2]/c-wiz/div[1]/div/div[2]/div[1]')
    box2.click()

    scroll_cnt = 10
    #스크롤 횟수 정하기
    for i in range(scroll_cnt):

        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(1.5)

        #더보기 버튼 클릭
        try:
            load_more = driver.find_element_by_xpath('//*[contains(@class, "U26fgb O0WRkf oG5Srb C0oVfc n9lfJ M9Bg4d")]').click()
        except:
            continue

    #리뷰 컨테이너 가져오기
    reviews = driver.find_elements(By.XPATH, '//*[@jsname="fk8dgd"]//div[@class="d15Mdf bAhLNe"]')

    # #리뷰를 데이터프레임에 저장
    df = pd.DataFrame(columns=['APP_IMG', 'APP_NAME','USER', 'DATE', 'STAR', 'LIKE', 'COMMENT' ])

    # #리뷰테이터 GET
    for review in reviews:
        soup = BeautifulSoup(review.get_attribute('innerHTML'), 'html.parser')

        #APP_IMG
        IMG_url = driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/c-wiz/div/div[2]/div/div/main/c-wiz/c-wiz[1]/div/div[1]/div/img')
        APP_IMG = IMG_url.get_attribute('src')

        #APP_NAME
        APP_NAME = driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/c-wiz/div/div[2]/div/div/main/c-wiz/c-wiz[1]/div/div[2]/div/div[1]/c-wiz[1]/h1/span').text

        #user
        USER = soup.find(class_='X43Kjb').text

        #review date
        DATE = soup.find(class_='p2TkOb').text
        DATE = datetime.strptime(DATE, '%Y년 %m월 %d일')
        DATE = DATE.strftime('%Y-%m-%d')

        #STAR
        STAR = int(soup.find("div", role="img").get('aria-label').replace('별표 5개 만점에',  '').replace('개를 받았습니다.', '').strip())

        #LIKE
        LIKE = soup.find(class_='jUL89d y92BAb').text
        if not LIKE:
            LIKE = 0

        #COMMENT
        COMMENT = soup.find('span', jsname='bN97Pc').text


        #append to DataFrame
        df = df.append({
            'APP_IMG' : APP_IMG,
            'APP_NAME': APP_NAME,
            'USER': USER,
            'DATE': DATE,
            'STAR': STAR,
            'LIKE': LIKE,
            'COMMENT': COMMENT,
            'OS': "android"
        }, ignore_index=True)

    df['DATE'] = pd.to_datetime(df['DATE'])
    df['DATE'] = df['DATE'].dt.tz_localize('Asia/Seoul')

    #csv file로 저장
    if purpose == "update":
        filename = "/data/Crawling/update/" + app_name_for_db + "_app_review_android.csv"
        df.to_csv(filename, encoding='utf-8-sig', index=False)
    else:
        filename = "/data/Crawling/result/" + app_name_for_db + "_app_review_android.csv"
        df.to_csv(filename, encoding='utf-8-sig', index=False)

    driver.stop_client()
    print('Google Done')

# app_name = "페이스북"

app_id  = sys.argv[1]
purpose = sys.argv[2]
app_name_for_db = sys.argv[3]
# app_id = find_app_id(app_name)
playstore_crawler(app_id, purpose, app_name_for_db)
