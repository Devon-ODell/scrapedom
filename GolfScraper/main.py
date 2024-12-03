import datetime
import csv
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, ElementNotInteractableException

start_time = datetime.datetime.now()

user_agent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
    'Mozilla/5.0 (Linux; Android 9; SM-G960F) AppleWebKit/537.36 Chrome/84.0.4147.125 Mobile Safari/537.36',
]

def sleep_timer():
    seconds_digit = random.randint(3, 5)
    time.sleep(seconds_digit)

def setup_driver():
    options = Options()
    options.headless = False  # Change to True for headless mode
    options.set_preference("general.useragent.override", random.choice(user_agent_list))
    service = Service('geckodriver.exe')
    driver = webdriver.Firefox(service=service, options=options)
    return driver

def search_query(driver, query):
    input_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".searchboxinput"))
    )
    input_element.clear()
    input_element.send_keys(query)
    input_element.send_keys(Keys.RETURN)
    sleep_timer()

def process_listings(driver):
    initial_listing_selector = ".CdoAJb > a"
    subsequent_listing_selector = ".PLbyfe > div"
    address_selector = "button[jsaction*='pane.wfvdle609'] .Io6YTe"
    business_name_selector = "span.a5H0ec"

    results = []
    try:
        listings = driver.find_elements(By.CSS_SELECTOR, initial_listing_selector)
        listings += driver.find_elements(By.CSS_SELECTOR, subsequent_listing_selector)

        for listing in listings:
            attempt = 0
            while attempt < 3:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", listing)
                    time.sleep(1)  # Give some time for the element to come into view
                    listing.click()
                    sleep_timer()

                    address_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, address_selector)))
                    address_text = address_element.text

                    business_name_element = WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.CSS_SELECTOR, business_name_selector)))
                    business_name_text = business_name_element.text

                    results.append([business_name_text, address_text])
                    break
                except (StaleElementReferenceException, ElementNotInteractableException):
                    attempt += 1
                    print(f"Retrying due to exception... {attempt}")
                except (NoSuchElementException, TimeoutException):
                    break
    except (NoSuchElementException, TimeoutException):
        print("No listings were found")

    return results

def save_progress(corpAddress, index):
    if index % 200 == 0 and index > 0:
        with open('hqScraper_progress.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['domain_name', 'address'])
            writer.writerows(corpAddress)

def main():
    driver = setup_driver()
    results = []
    query = "Golf resorts, Canton, OH"  # Modify this query as needed
    
    try:
        driver.get('https://www.google.com/maps')
        sleep_timer()

        search_query(driver, query)
        query_results = process_listings(driver)

        if query_results:
            for result in query_results:
                results.append(result)
                print(f"Result found: {result}")
        else:
            results.append(["No matching golf resorts found", query])
            print(f"No matching golf resorts found for {query}")

    finally:
        with open('golf_resorts.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['business_name', 'address'])
            writer.writerows(results)
        driver.quit()

if __name__ == "__main__":
    main()

elapsed = datetime.datetime.now() - start_time
print("The time it took for this to run: " + str(elapsed))


