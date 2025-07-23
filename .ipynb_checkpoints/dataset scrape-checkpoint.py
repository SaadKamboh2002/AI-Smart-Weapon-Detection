from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os
import time
import random
import requests


opt = Options()
opt.add_argument("--disable-notifications")
opt.add_argument("--disable-infobars")
opt.add_argument("--start-maximized")
# hide automation works
opt.add_argument('--disable-blink-features=AutomationControlled')
# opt.add_argument('--headless')  # runs in the background


cservice = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=cservice, options=opt)
wait = WebDriverWait(driver, 10)


# function to download an image
def download_image(img_url, folder, img_name):
    try:
        img_data = requests.get(img_url, timeout=10).content
        with open(os.path.join(folder, img_name), 'wb') as img_file:
            img_file.write(img_data)
        print(f"Downloaded: {img_name}")
    except Exception as e:
        print(f"Error downloading {img_name}: {e}")

# search query
search_query = "revolver"
url = f"https://www.google.com/search?q={search_query}&tbm=isch"

# open Google Images
driver.get(url)

# scroll down to load more images
for _ in range(5):  # Scroll 5 times
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
    time.sleep(random.uniform(2, 4))  # Random sleep to avoid detection

# extract image URLs
page = driver.page_source
soup = BeautifulSoup(page, 'html.parser')
all_images = soup.find_all("img")

# process image urls
image_links = []
for img in all_images:
    src = img.get("data-src") or img.get("src")  # Prefer data-src if available
    if src and "http" in src:
        image_links.append(src)

print(f"Found {len(image_links)} images.")

# create folder to save images
save_folder = os.path.join(os.getcwd(), search_query + "_images")
os.makedirs(save_folder, exist_ok=True)


for i, img_url in enumerate(image_links[:]):  # downloading images
    img_name = f"{search_query}_{i+1}.jpg"
    download_image(img_url, save_folder, img_name)
    time.sleep(random.uniform(1, 3))  # random delay
driver.quit()  # close the browser
print(f"All images saved in: {save_folder}")
