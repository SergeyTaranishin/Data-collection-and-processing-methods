from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import ast
from pymongo import MongoClient
from pprint import pprint

def db_update(id, data):
    try:
        db.new_products.update_one({'productId': id},
                                   {'$set': data},
                                    upsert = True)
    except:
        pass

chrome_options = Options()
chrome_options.add_argument("start-maximized")  # во весь экран
chrome_options.add_argument("--incognito")   # режим инкогнито
driver = webdriver.Chrome(executable_path='./chromedriver.exe', options=chrome_options)
driver.get("https://www.mvideo.ru/?cityId=CityCZ_1780")       # Сразу локация в Самаре оставил, хотя научился выбирать город )))

# Вот такой способ нашёл избавления от навязчевого баннера.
# Кликнуть в стороне и тогда он исчезает и даже авторизовация уже не мешает )))
actions = ActionChains(driver)
actions.move_by_offset(10, 10).perform() # клик по координатам
actions.click().perform()

# обработка блока "Новинки"
block_new = driver.find_element_by_xpath('//div[contains(h2, "Новинки")]')
actions.move_to_element(block_new).perform()    # перемещение к блоку

wait = WebDriverWait(driver, 10)

while True:
    try:
        btn_next = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//div[contains(h2, "Новинки")]/../..//a[contains(@class, "next-btn")]')))
    except TimeoutException:
        break
    except ElementClickInterceptedException:
        break
    else:
        btn_next.click()

# Собираем элементы товаров в Новинках
new_products = driver.find_elements_by_xpath(
    '//div[contains(h2, "Новинки")]/../..//a[contains(@class, "fl-product-tile-picture")]')

# Запись в БД
client = MongoClient('127.0.0.1', 27017)
db = client['MVideo']

# Получение и запись данных по каждому элементу
for i in new_products:
    product_info = i.get_attribute('data-product-info')
    dict_product_info = ast.literal_eval(product_info) # нашёл такой метод преобразования на просторах сети, но до конца не понимаю как так красиво он преобразует.
    db_update(dict_product_info.get('productId'), dict_product_info)

# Закрываем окно браузера driver
driver.close()

# Показать данные в БД
for doc in db.new_products.find({}):
    pprint(doc)