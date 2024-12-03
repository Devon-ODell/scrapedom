from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
import csv
import time
import random

def random_wait():
    time.sleep(random.randint(2, 4))

def save_to_csv(locations, filename='nb-locations.csv', mode='a'):
    with open(filename, mode, newline='') as f:
        writer = csv.writer(f)
        for loc in locations:
            writer.writerow(loc)

def read_urls(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def scrape_brooks_locations():
    chromedriver_autoinstaller.install()
    options = Options()
    driver = webdriver.Chrome(options=options)
    locations = []
    count = 0
    
    try:
        # Initialize CSV with header
        with open('nb-locations.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Store Name', 'Address', 'City', 'State', 'Zip', 'Phone'])
        
        # Read URLs from file
        urls = read_urls('stores.csv')
        total_urls = len(urls)
        print(f"Found {total_urls} URLs to process")
        
        for index, url in enumerate(urls, 1):
            try:
                driver.get(url)
                random_wait()
                
                # Get store name
                store_name = driver.find_element(By.CLASS_NAME, "landing-header-title").text.strip()
                
                # Get address section
                address_section = driver.find_element(By.CLASS_NAME, "landing-header-address").text
                
                # Parse address components
                address_parts = address_section.split('\n')
                street_address = address_parts[0].strip()
                
                # Parse city, state, zip
                location_parts = address_parts[1].strip().split(',')
                if len(location_parts) == 2:
                    city = location_parts[0].strip()
                    state_zip = location_parts[1].strip().split()
                    state = state_zip[0].strip()
                    zip_code = state_zip[1].strip()
                else:
                    city, state, zip_code = "", "", ""
                
                # Get phone if available
                phone = ""
                if len(address_parts) > 2:
                    phone = address_parts[2].strip()
                
                location = [store_name, street_address, city, state, zip_code, phone]
                locations.append(location)
                count += 1
                
                print(f"Processed {index}/{total_urls}: {store_name}")
                
                # Save every 50 locations
                if count % 50 == 0:
                    save_to_csv(locations)
                    print(f"\nIntermediate save: {count} locations saved to CSV")
                    locations = []
                
            except Exception as e:
                print(f"Error processing URL {url}: {str(e)}")
                continue
            
        # Save remaining locations
        if locations:
            save_to_csv(locations)
            print(f"\nFinal save: {count} total locations")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_brooks_locations()