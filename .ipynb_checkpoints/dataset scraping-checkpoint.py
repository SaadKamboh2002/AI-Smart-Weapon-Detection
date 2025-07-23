from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup # to parse html
import os # to save them to folder
import wget # to download images
import time

# when chromedriver manager is of older version, this code is better used than
# the one installed as it automatically downloads the latest drivers
from webdriver_manager.chrome import ChromeDriverManager
cservice = Service(ChromeDriverManager().install())  


opt = Options()
opt.add_argument("--disable-notifications")
opt.add_argument("--disable-infobars")
opt.add_argument("--start-maximized")
# opt.add_argument('--headless')
# tried using proxies to avoid captcha but failed
# opt.add_argument('--proxy-server=http://54.179.39.14:3128')
# hide automation works
opt.add_argument('--disable-blink-features=AutomationControlled')  



url = 'https://www.google.com'

driver = webdriver.Chrome(service=cservice, options=opt)
wait = WebDriverWait(driver, 60)
driver.get(url=url)


# finding the search box
# search_box = soup.find(attrs={"name": "q"})
search_query = 'revolver'
wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="APjFqb"]'))).send_keys(search_query)
wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="APjFqb"]'))).send_keys(Keys.ENTER)
wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="hdtb-sc"]/div/div/div[1]/div/div[2]/a/div'))).click()

page = driver.page_source
soup = BeautifulSoup(page, 'lxml')

all_images = soup.find_all('img')
time.sleep(5)
source_image = []
for image in all_images:
    source_image.append(image.get('src'))
time.sleep(5)
print(len(source_image), ' image sources found incl Nonetypes')
#checking how many images have no src element
print(sum(1 for i in source_image if i is None), 'image have no sources')
source_image = [img for img in source_image if img is not None]
print(len(source_image), ' image sources remaining after removing nonetypes')


path = os.getcwd()
path = os.path.join(path, search_query+' images')
os.makedirs(path, exist_ok=True)

# adding https: before // to the image links
new_source = []
for src in source_image:
    new_source.append('https:'+src)


counter = 1
for image in new_source:
    saving = os.path.join(path, search_query+str(counter)+'.jpg')
    wget.download(image, out=saving)
    print(f'downloaded image {counter}')
    counter += 1
    time.sleep(2)




# browser = mechanicalsoup.StatefulBrowser()
# url = 'https://www.google.com'
# browser.open(url)
# browser.select_form()
# # browser.get_current_form().print_summary()
# search_query = 'revolver'
# browser['q'] = search_query
# browser.submit_selected()
# images = browser.page.find_all('img')
# source = []
# for image in images:
#     source.append(image.get('src'))
# path = os.getcwd()
# path = os.path.join(path, search_query)
# if not os.path.exists(path):
#     os.mkdir(path)
# new_source = []
# for src in source:
#     new_source.append('https:'+src)
# counter = 1
# for image in new_source:
#     saving = os.path.join(path, search_query+str(counter)+'.jpg')
#     wget.download(image, out=saving)
    # counter += 1