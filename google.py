from selenium import webdriver
from bs4 import BeautifulSoup
import time, os, sys
import pandas as pd
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

option = Options()
option.add_argument("disable-infobars")
option.add_argument("disable-extensions")
# option.add_argument("start-maximized")
option.add_argument('—no-sandbox')
option.add_argument('disable-gpu')
option.add_argument('headless')



def find_app_id(app_name):
    driver = webdriver.Chrome('./chromedriver', options=option)
    link = "https://play.google.com/store/search?q=" + str(app_name) + "&c=apps&hl=ko&gl=KR"
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
    return app_id


#com.kakaogames.odin
def playstore_crawler(app_id):
    driver = webdriver.Chrome('./chromedriver', options=option)
    link = 'https://play.google.com/store/apps/details?id=' + str(app_id) + '&hl=ko&gl=US&showAllReviews=true'
    driver.get(link)


    os.makedirs('result', exist_ok=True)

    scroll_cnt = 1
    #스크롤 횟수 정하기
    for i in range(scroll_cnt):

        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(2)

        #더보기 버튼 클릭
        try:
            #load_more = driver.find_element(By.xpath, '/html/body/div[1]/div[4]/c-wiz[3]/div/div[2]/div/div/main/div/div[1]/div[2]/div[2]/div/div[2]').click()
            load_more = driver.find_element_by_xpath('//*[contains(@class, "U26fgb O0WRkf oG5Srb C0oVfc n9lfJ M9Bg4d")]').click()
        except:
            print('Cannot find load more button..')



    #리뷰 컨테이너 가져오기
    reviews = driver.find_elements(By.XPATH, '//*[@jsname="fk8dgd"]//div[@class="d15Mdf bAhLNe"]')

    print('There are %d reviews available!' % len(reviews))
    print('Writing the data...')

    # #리뷰를 데이터프레임에 저장
    df = pd.DataFrame(columns=['APP_NAME','USER', 'DATE', 'STAR', 'LIKE', 'COMMENT' ])

    # #리뷰테이터 GET
    for review in reviews:
        soup = BeautifulSoup(review.get_attribute('innerHTML'), 'html.parser')

        #APP_NAME
        #APP_NAME = soup.find('span', class_='AHFaub').text
        APP_NAME = driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/c-wiz/div/div[2]/div/div/main/c-wiz/c-wiz[1]/div/div[2]/div/div[1]/c-wiz[1]/h1/span').text

        #user
        USER = soup.find(class_='X43Kjb').text

        #review date
        DATE = soup.find(class_='p2TkOb').text
        #DATE = datetime.strptime(DATE, '%Y년 %m월 %d일')
        #DATE = DATE.strftime('%Y-%m-%d')

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
            'id': "",
            'APP_NAME': APP_NAME,
            'USER': USER,
            'DATE': DATE,
            'STAR': STAR,
            'LIKE': LIKE,
            'TITLE': "non-title",
            'COMMENT': COMMENT,
            'OS': "android"
        }, ignore_index=True)

    #csv file로 저장
    # filename = datetime.now().strftime('result/%Y-%m-%d_%H-%M-%S.csv')
    filename = "result/app_review_android.csv"
    df.to_csv(filename, encoding='utf-8-sig', index=False)
    driver.stop_client()



    print('DONE!')

# app_name = "유튜브"

app_name = sys.argv[1]
app_id = find_app_id(app_name)
playstore_crawler(app_id)
