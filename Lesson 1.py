import requests, json
# from pprint import pprint
url = 'https://api.github.com/users/SergeyTaranishin/repos'

response = requests.get(url)
j_data = response.json()

count_des = len(j_data) - 1

i = 0
while i <= count_des:
    print(j_data[i]['name'])
    i += 1

with open('des.json','w') as file:
    file.write(json.dumps(j_data))