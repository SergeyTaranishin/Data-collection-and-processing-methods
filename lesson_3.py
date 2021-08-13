import requests, re
from bs4 import BeautifulSoup as bs
from pprint import pprint
from pymongo import MongoClient

def db_update(ID, data):
      try:
            vacancy.update_one({'_id': job_data['_id']},
                               {'$set': job_data},
                               upsert=True)
      except:
            pass

client = MongoClient('127.0.0.1', 27017)
db = client['VacancyFromHHru']
vacancy = db.vacancy

position = 'python'
min_oklad = int(input('Показать вакансии Python с минимальным окладом (валюта не учитывается) от:'))

number_page = 0
page_next = True

while page_next:
      # узнаём User-agent через запрос в браузере "chrome://version/"
      headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'}
      url = 'https://hh.ru/' \
            'search/vacancy?clusters=true&enable_snippets=true&ored_clusters=true&text='+position+'&search_period=0&' \
            'page=' + str(number_page)
      response = requests.get(url, headers=headers)
      soup = bs(response.text, 'html.parser')

      jobs_block = soup.find('div', {'class': 'vacancy-serp'})
      jobs_list = jobs_block.findChildren(recursive=False)
      for job in jobs_list:
            job_data = {}
            req = job.find('span', {'class': 'g-user-content'})
            if req != None:    #проверка на пустоту
                  main_info = req.findChild()
                  job_link = main_info['href']
                  job_data['name'] = main_info.getText()
                  job_data['link'] = job_link
                  job_data['_id'] = int(re.search('hh.ru/vacancy/(\d*)\?from', job_link).group(1))
                  job_data['site'] = 'hh.ru'

                  req = job.find('div', {'class': 'vacancy-serp-item__sidebar'})
                  job_salary = req.findChild()
                  if job_salary:
                        salary = str(job_salary.getText()).replace('\u202f','')
                        salary_list = salary.split(' ')
                        if salary_list[0] == '':
                              job_data['salary_min'] = None
                              job_data['salary_max'] = None
                              job_data['salary_currency'] = None
                        elif salary_list[0] == 'от':
                              job_data['salary_min'] = int(salary_list[1])
                              job_data['salary_max'] = None
                              job_data['salary_currency'] = salary_list[2]
                        elif salary_list[0] == 'до':
                              job_data['salary_min'] = None
                              job_data['salary_max'] = int(salary_list[1])
                              job_data['slaary_currency'] = salary_list[2]
                        elif salary_list[1] == '–':
                              job_data['salary_min'] = int(salary_list[0])
                              job_data['salary_max'] = int(salary_list[2])
                              job_data['slaary_currency'] = salary_list[3]
                  else:
                        job_data['salary_min'] = None
                        job_data['salary_max'] = None
                        job_data['slaary_currency'] = None
                  # Обновляем наличие вакансии в БД. Если нет ID вакансии, то добавляем, если есть, то обновляем целиком.
                  db_update(job_data['_id'], job_data)

      number_page += 1
      page_next = soup.find('a', {'class': 'bloko-button', 'data-qa': 'pager-next'})

for doc in db.vacancy.find( {'$or':[ {'salary_min': {'$gt': min_oklad } },
                                     {'salary_max': {'$gt': min_oklad } }  ] } ):
    pprint(doc)
