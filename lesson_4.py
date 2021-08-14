from lxml import html
import re
import requests
from pprint import pprint
from pymongo import MongoClient

def db_update(link, data):
    try:
        db.news.update_one({'link': link},
                           {'$set': data},
                           upsert=True)
    except:
        pass

client = MongoClient('127.0.0.1', 27017)
db = client['News_Lenta_ru']

url = 'https://lenta.ru/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'}
response = requests.get(url, headers=headers)
dom = html.fromstring(response.text)
top_news = dom.xpath("//section[contains(@class,'top7')]//div[@class='first-item']/h2 | //section[contains(@class,'top7')]//div[@class='item']")
# top_news_list = []
for i in top_news:
    news = {}
    news['link'] =  i.xpath('.//a/@href')[0]

    if news['link'][0] == '/':
        news['source_name'] = 'lenta.ru'
    else:
        news['source_name'] = re.search('https://(.*)/news', news['link']).group(1)
    name = i.xpath('.//a/text()')[0].replace('\xa0', ' ')
    news['name'] = name.rstrip()

    if news['source_name'] == 'lenta.ru':
        news['link'] = 'https://lenta.ru' + i.xpath('.//a/@href')[0]
    else:
        news['link'] = i.xpath('.//a/@href')[0]

    news['time'] = i.xpath('.//a/time/@datetime')[0]

    db_update(news['link'], news)
    # top_news_list.append(news)

# pprint(top_news_list)
for doc in db.news.find({}):
    pprint(doc)

