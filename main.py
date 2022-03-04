"""
SETUP

PIP INSTALLATION
selenium
webdriver-manager
beautifulsoup4
requests
"""


import requests
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

#Function for downloading images
def download_image(url, folder_name, num):
    # write image to file
    try:
        response = requests.get(url,timeout=10)
    except requests.exceptions.Timeout as err:
        print(err)
        
    print("Response status code: " + str(response.status_code))
    if response.status_code==200:
        print("Starting download...")
        with open(os.path.join(folder_name, str(num)+".jpg"), 'wb') as file:
            file.write(response.content)

#Start webdriver
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('--ignore-gpu-blocklist')
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--disable-software-rasterizer")
driver = webdriver.Chrome(service=service,chrome_options=options)
images_downloaded=0

#User inputs    
searches = []
desired_amount = int(input("Enter desired amount of images for each search: "))
with open("search.txt","r") as file:
    searches = file.read().splitlines()

for search in searches:
    if not os.path.isdir(search):
        os.makedirs(search)
        print(f"---{search} folder created---")
    # Get query url and search for result
    query = search.replace(" ", "+")
    search_URL = f"https://www.google.com/search?q={query}&source=lnms&tbm=isch"
    folder_to_save = search
    driver.get(search_URL)

    # Scroll all the way to the end, then scroll back up
    continue_scrolling = True

    while (continue_scrolling):
        print("scrolling...")
        try:
            button = WebDriverWait(driver, 1).until(EC.visibility_of_all_elements_located(
                (By.XPATH, r'//*[@id="islmp"]/div/div/div/div[1]/div[2]/div[2]/input')))
            button[0].click()
        except(TimeoutException):
            pass
        try:
            button = WebDriverWait(driver, 1).until(EC.visibility_of_all_elements_located(
                (By.XPATH, r'//*[@id="islmp"]/div/div/div/div[1]/div[2]/div[1]/div[2]/div[1]/div')))
            print("REACHED END OF ALL RESULTS")
            continue_scrolling = False
        except(TimeoutException):
            pass
        try:
            button = WebDriverWait(driver, 1).until(EC.visibility_of_all_elements_located(
                (By.XPATH, r'//*[@id="islmp"]/div/div/div/div[2]')))
            print("REACHED END OF RELEVANT RESULTS")
            continue_scrolling = False
        except(TimeoutException):
            pass

        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    driver.execute_script("window.scrollTo(0, 0);")

    # Get the number of images to download
    page_html = driver.page_source
    pageSoup = bs4.BeautifulSoup(page_html, 'html.parser')
    containers = pageSoup.findAll('div', {'class': "isv-r PNCib MSM1fd BUooTd"})
    len_containers = len(containers)
    len_containers = desired_amount if desired_amount <= len_containers else len_containers

    # Loops through each div
    for i in range(1, len_containers + 1):
        xPath = """//*[@id="islrg"]/div[1]/div[%s]""" % (i)  # This xpath refers to the div that contains the img

        timeStarted = time.time()

        try:
            previewImageXPath = """//*[@id="islrg"]/div[1]/div[%s]/a[1]/div[1]/img""" % (i)
            previewImageElement=WebDriverWait(driver, 1).until(EC.visibility_of_all_elements_located((By.XPATH, previewImageXPath)))
            previewImageURL = previewImageElement[0].get_attribute("src")
            driver.find_element(By.XPATH, xPath).click()

            # A loop to try and get the highest resolution of the image possible
            while True:
                print("waitinng for high res...")
                imageElement = WebDriverWait(driver, 1).until(EC.visibility_of_all_elements_located((By.XPATH, """//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div[2]/div[1]/a/img""")))
                imageURL = imageElement[0].get_attribute('src')

                # When imageurl is different from previewimageurl, the full res has been loaded
                if imageURL != previewImageURL:
                    break

                else:
                    # making a timeout if the full res image can't be loaded
                    currentTime = time.time()
                    if currentTime - timeStarted > 10:
                        print("Timeout! Will download a lower resolution image and move onto the next one")
                        break
                time.sleep(2)

            # Downloads the image
            try:
                download_image(imageURL, folder_to_save, i)
                currentTime = time.time()
                if currentTime - timeStarted > 20:
                        print("Skipping image")
                        time.sleep(5)
                        continue
                print("Downloaded element %s out of %s total. URL: %s" % (i, len_containers + 1, imageURL))
                images_downloaded += 1
            except Exception as e:
                print(e)
                print("Couldn't download an image %s, continuing downloading the next one" % (i))

        except(NoSuchElementException):
            print("Not an image")
        except(TimeoutException):
            print("Not an image")
            

print("Images downloaded: " + str(images_downloaded))


