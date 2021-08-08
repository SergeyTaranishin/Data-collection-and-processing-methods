import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint

position = input('Укажите должность: ')

number_page = 0
page_next = True
jobs = []

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
                  job_name = main_info.getText()
                  job_link = main_info['href']
                  job_data['name'] = job_name
                  job_data['link'] = job_link
                  # job_data['site'] = 'hh.ru'

                  req = job.find('div', {'class': 'vacancy-serp-item__sidebar'})
                  job_salary = req.findChild()
                  if job_salary:
                        salary = str(job_salary.getText()).replace('\u202f','')
                        # job_data['salary'] = salary
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
                              job_data['salary_currency'] = salary_list[2]
                        elif salary_list[1] == '–':
                              job_data['salary_min'] = int(salary_list[0])
                              job_data['salary_max'] = int(salary_list[2])
                              job_data['salary_currency'] = salary_list[3]
                  else:
                        # job_data['salary'] = None
                        job_data['salary_min'] = None
                        job_data['salary_max'] = None
                        job_data['salary_currency'] = None
                  jobs.append(job_data)
      number_page += 1
      page_next = soup.find('a', {'class': 'bloko-button', 'data-qa': 'pager-next'})

if len(jobs) == 0:
      print('Вакансий не найдено')
else:
      print('Обнаружено ', len(jobs), ' вакансий')
      pprint(jobs)
