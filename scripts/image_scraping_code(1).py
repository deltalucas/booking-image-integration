from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from multiprocessing import Pool, Lock, Manager
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import date
import requests
import psutil
import math
import json
import time
import re
import os

# Creates a json directory and adds each hotel's data to it
def create_jsonfile(country, st, city, hotel_name, gps, address, rating, url, images):

    date_accessed = str(date.today())

    dictionary = {
        "hotel_name": hotel_name,
        "date_accessed": date_accessed,
        "gps": gps,
        "address": address,
        "rating": rating,
        "url": url,
        "images": images
    }

    # Creates the path for the new json file

    if country == "United-States":
        country = "United-States-of-America"

    path = f'./country/{country}/{st}/{city}/'
    if not os.path.exists(path):
        os.makedirs(path)
    filename = f'{path}/{hotel_name}.json'
    with open(filename, 'w', newline='') as jsonfile:
        json.dump(dictionary, jsonfile)

# Takes in an individual hotel link and gets the hotel's images and metadata. It then adds that data to a json directory
def get_images_and_metadata(link):
    print("in get images")
    options = Options()
    options.headless = True
    driver_path = '/Applications/Firefox.app/Contents/MacOS/firefox'
    options.binary = FirefoxBinary(driver_path) # DEPRECEATED
    driver = webdriver.Firefox(options=options)
    driver.get(link)
    time.sleep(5)

    print(link)
    # Get's the hotel's name
    print("getting hotel name")
    try:
        hotel_name_element = driver.find_element(By.CLASS_NAME, "bui_breadcrumb__link_masked")
        hotel_name = hotel_name_element.text
        if "(Hotel)" not in hotel_name and "(Inn)" not in hotel_name and "(Motel)" not in hotel_name and "(Bed and Breakfast)" not in hotel_name:
            print("not hotel: ", hotel_name)
            return
        hotel_name = hotel_name.replace(" ", "-").replace("/", "-")[:-12]
    except Exception as e:
        print(e)
        hotel_name = "Hotel name not found"

    # Gets the hotel's gps coordinates
    print("getting gps")
    try:
        gps_elements = driver.find_elements(By.CSS_SELECTOR, "a")
        gps = None
        for gp in gps_elements:
            if gp.get_attribute('data-atlas-latlng') is not None:
                gps = str(gp.get_attribute('data-atlas-latlng'))
                break
        if gps is None:
            gps = "GPS Coordinates not found"
    except Exception as e:
        print(e)
        gps = "GPS Coordinates not found"

    # Get's the hotel's address
    print("getting address")
    try:
        address_element = driver.find_element(By.ID, "showMap2")
        address = address_element.text
        if " - " in address:
            address = address.split(" - ")[0]
        elif " – " in address:  # Note: different dash character
            address = address.split(' – ')[0]
    except Exception as e:
        try:
            address_element = driver.find_element(By.ID, "showMap2")
            address = address_element.text
            if " - " in address:
                address = address.split(" - ")[0]
            elif " – " in address:  # Note: different dash character
                address = address.split(' – ')[0]
        except Exception as e:
            print(e)
            address = "Address not found"


    # Get's the hotel's url address
    print("getting url")
    try:
        page_url = driver.current_url
        page_url = str(page_url)
        print("url to save: ", page_url)
    except Exception as e:
        print(e)
        page_url = "URL not found"

    # Gets the hotel's rating. They do not all have a rating
    print("getting rating")
    rating = "No Rating"
    try:
        ratings = driver.find_elements(By.ID, "js--hp-gallery-scorecard")
        for rating in ratings:
            if rating.get_attribute('data-review-score') is not None:
                rating = str(rating.get_attribute('data-review-score'))
                break
    except Exception as e:
        print(e)

    country = "Country not found"
    state = "State not found"
    city = "City not found"
    print("getting country, state, city")
    try:
        countryToFind = "United States of America"
        countryToFind2 = "United States"
        breadcrumb_elements = driver.find_elements(By.CLASS_NAME, "bui-breadcrumb__item.hp-breadcrumb__item")
        for i in range(len(breadcrumb_elements)):
            if breadcrumb_elements[i].text in [countryToFind, countryToFind2]:
                country = breadcrumb_elements[i].text.replace(" ", "-")
                state = breadcrumb_elements[i + 1].text.replace(" ", "-") if i + 1 < len(breadcrumb_elements) else "State not found"
                city = breadcrumb_elements[i + 2].text.replace(" ", "-") if i + 2 < len(breadcrumb_elements) else "City not found"
                print(country, "\n", state, "\n", city, "\n")
                break
    except Exception as e:
        print("Error getting country, state, city")
        print(e)
    print(hotel_name)
    path = f'./country/{country}/{state}/{city}/{hotel_name}.json'
    if os.path.exists(path):
        print("path already exists: ", path)
        return

    # Gets the images
    this_page_image_links = []
    try: 
        frame = driver.find_element(By.CLASS_NAME, "k2-hp--gallery-header.bui-grid__column.bui-grid__column-9")
        frame.click()
        #print("url after frame:", driver.current_url)
        time.sleep(5)
        # Scrolls through the new frame to load all images
        modal_box = driver.find_element(By.CLASS_NAME, "bh-photo-modal-thumbs-grid.js-bh-photo-modal-layout.js-no-close")
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight / 4", modal_box)
        time.sleep(3)
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight / 2", modal_box)
        time.sleep(3)
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight / 1.5", modal_box)
        time.sleep(3)
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal_box)
        print("url after scroll: ", driver.current_url)
        time.sleep(3)
        # Finds all the links on the page
        links = driver.find_elements(By.TAG_NAME, 'img')
        for link in links:
            if link.get_attribute('src') is None:
                continue
            else:
                try:
                    urls = link.get_attribute('src')
                    urls = urls.splitlines()
                    for url in urls:
                        if "bstatic.com/xdata/images/hotel/max1024" in str(url):
                            this_page_image_links.append(url)
                except:
                    continue
    except Exception as e:
        print(e)
        pass
    
    driver.quit()
    create_jsonfile(country, state, city, hotel_name, gps, address, rating, page_url, this_page_image_links)

# Scrapes all the city links from the provided website and returns a list of those links
def get_city_links(link):
    print("in get_cities")
    city_links = set()
    try:
        page = requests.get(str(link))
        soup = BeautifulSoup(page.content, 'html.parser')
        links = soup.find_all('a', attrs={'href': re.compile("^/city/")})
        for link in links:
            link = link.get('href')
            link = "https://www.booking.com" + str(link)
            city_links.add(link)
    except Exception as e:
        print(e)
    return city_links

# Scrapes all of the hotels from each city, calling the get images and metadata function to get the metadata from each along the way
def get_hotels(city):
    options = Options()
    options.headless = True
    driver_path = '/Applications/Firefox.app/Contents/MacOS/firefox'
    options.binary = FirefoxBinary(driver_path)
    driver = webdriver.Firefox(options=options)
    this_page_hotel_links = []
    hotel_links = []

    try:
        driver.get(str(city))
        print(str(city))
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            good_link = driver.find_element(By.CSS_SELECTOR, 'a.bf33709ee1.a190bb5f27.c73e91a7c9.e8d0e5d0c1.e47e45fccd.a94fe207f7')
            good_link = good_link.get_attribute('href')
        except:
            print("secondary webpage")
            search_button = driver.find_elements(By.CSS_SELECTOR, "button")
            print("found all buttons")
            for button in search_button:
                if button.text == "Search":
                    print("clicked search button")
                    button.click()
                    break
            good_link = driver.current_url
        # Navigates the driver to the new link which works with image scraper
        driver.get(str(good_link))
        print(good_link)
        driver.refresh()
        time.sleep(5)
        
        max_tries = 15
        tries = 0
        while tries < max_tries:
            try:
                checkboxes = driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
                for box in checkboxes:
                    if str(box.get_attribute('aria-label')).startswith("Hotels: "):
                        checkbox = box
                        break
                checkbox.click()
                print("Checkbox is clicked: ", checkbox.is_selected())
                break
            except Exception as e:
                driver.refresh()
                tries += 1
                print(f"Attempt {tries+1}")
        
        print("checkbox clicked")
        driver.refresh()
        time.sleep(5)
        after_checkbox = driver.current_url
        print(after_checkbox)

        h1s = driver.find_elements(By.CSS_SELECTOR, 'h1')
        count = None
        for h1 in h1s:
            if str(h1.get_attribute('aria-label')).startswith("Search results updated."):
                counts = h1.text.split()
                print(counts)
                try:
                    count = int(counts[-3])
                except Exception as e:
                    print(f"Error parsing count: {e}")
                break
            else:
                print("in else")
        print("count: ", count)
        if count is None:
            print("No valid count found")
            driver.quit()
            with open('processed_cities.txt', 'a') as f:
                f.write(city + '\n')
            return
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        for i in range(30):
            driver.find_element(By.CSS_SELECTOR,'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)
        print(count)
        if int(count) > 75:
            no_button = False
            k = 0
            while no_button == False:
                try:
                    print("trying to load button")
                    load_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'c82435a4b8.f581fde0b8')))
                    load_button.click()
                    print("clicked button")
                    for i in range(10):
                        driver.find_element(By.CSS_SELECTOR,'body').send_keys(Keys.PAGE_DOWN)
                        time.sleep(0.3)
                    k += 1
                except WebDriverException as e:
                    if k > 0:
                        no_button = True
                    else:   
                        print("webdriver exception")
                        driver.get(after_checkbox)
                        time.sleep(5)
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        for i in range(30):
                            driver.find_element(By.CSS_SELECTOR,'body').send_keys(Keys.PAGE_DOWN)
                            time.sleep(0.3)
        num_hotels = len(driver.find_elements(By.CLASS_NAME, 'a78ca197d0'))
        if num_hotels == 0:
            print("No hotels found")
            driver.refresh()
            time.sleep(5)
            num_hotels = len(driver.find_elements(By.CLASS_NAME, 'a78ca197d0'))
        print(f"number of hotels = {num_hotels}") 
        this_page_hotel_links = driver.find_elements(By.CLASS_NAME, 'a78ca197d0')
        print(len(this_page_hotel_links))

        print("url: ", driver.current_url)
        gone_through = 0
        for link in this_page_hotel_links:
            link = link.get_attribute('href')
            hotel_link = link.split("?")[0]
            if hotel_link.startswith("https://www.booking.com/hotel/"):
                if hotel_link not in hotel_links:
                    hotel_links.append(hotel_link)
                    get_images_and_metadata(hotel_link)
            gone_through += 1
            print(f"gone through {gone_through} hotels")
            if gone_through > count:
                break
    except Exception as e:
        print(e)
        pass

    driver.quit()

    with open('processed_cities.txt', 'a') as f:
        f.write(city + '\n')



if __name__ == '__main__':
    city_repo = 'https://www.booking.com/destination/country/us.html?label=gen173nr-1FCAoouAI46AdIM1gEaJ0CiAEBmAExuAEHyAEP2AEB6AEB-AECiAIBqAIDuALOu92yBsACAdICJDIxYTNlYzViLWI3YjctNGEyZC1hY2IyLTBjOGNmMWZkZWZhYtgCBeACAQ&sid=82a5a8b88655128c0c7a8290c2214878&inac=0&'
    
    # calls the get_city_links function to scrape all the images from the website in city_repo
    city_links_to_visit = get_city_links(city_repo)
    print(len(city_links_to_visit))

    if os.path.exists('/Users/vislabmini/Code/processed_cities.txt'):
        with open('/Users/vislabmini/Code/processed_cities.txt', 'r') as f:
            processed_cities = set(f.read().splitlines())
    city_links_to_visit = city_links_to_visit - processed_cities
    print(len(city_links_to_visit))

    with Pool(processes = 4) as pool:
        # Starts doing multiprocessing, performing the get_hotels function for each city link
        pool.map(get_hotels, list(city_links_to_visit))
    
    #get_hotels('https://www.booking.com/city/us/orlando.html?label=gen173nr-1FCAoouAI46AdIM1gEaJ0CiAEBmAExuAEHyAEP2AEB6AEB-AECiAIBqAIDuALOu92yBsACAdICJDIxYTNlYzViLWI3YjctNGEyZC1hY2IyLTBjOGNmMWZkZWZhYtgCBeACAQ&sid=82a5a8b88655128c0c7a8290c2214878')

    print("Process Finished")
