import json
import requests
import sys


def find_app_id(app_name):
    url = 'https://itunes.apple.com/search'
    values = {'term' : app_name,
              'country' : 'KR',
              'media' : 'software',
              'limit' : '1'}

    url_ = requests.get(url, params=values)
    url_.encoding = 'utf-8'
    the_page = url_.json()

    real_app_name = the_page['results'][0]['trackName']
    app_img = the_page["results"][0]["artworkUrl512"]

    r_app_name =  'A' + real_app_name
    characters = '~!@#$%^&*(){}[]_-+:.,/?;|""'
    app = r_app_name.replace(' ', '')
    for i in range(len(characters)):
        app = app.replace(characters[i],'')

    return (real_app_name, app, app_img)





# app_name = "오딘"
app_name = sys.argv[1]

try:
    real_app_name, app, app_img = find_app_id(app_name)

    print(real_app_name)
    print(app)
    print(app_img)
except:
    print("SSL issue")
    print("SSL issue")
    print("SSL issue")
