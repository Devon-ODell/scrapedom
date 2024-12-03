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

def save_to_csv(locations, filename='rackroom_locations.csv', mode='a'):
    with open(filename, mode, newline='') as f:
        writer = csv.writer(f)
        for loc in locations:
            writer.writerow(loc)

def scrape_rackroom_locations():
    chromedriver_autoinstaller.install()
    options = Options()
    driver = webdriver.Chrome(options=options)
    locations = []
    count = 0
    current_page = 1
    total_pages = 111  # 551 listings / 5 per page = 111 pages
    
    try:
        # Initialize CSV with header
        with open('rackroom_locations.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Store', 'Address', 'City', 'State', 'ZIP'])
        
        while current_page <= total_pages:
            try:
                # Visit the page
                url = f"https://www.rackroomshoes.com/store-finder?page={current_page}"
                driver.get(url)
                random_wait()
                
                # Get all addresses on current page
                addresses = driver.find_elements(By.CSS_SELECTOR, "p.mb-0")
                
                for address in addresses:
                    address_text = address.text.strip()
                    if address_text:  # Only process if address isn't empty
                        location = ["Rack Room Shoes", address_text]
                        locations.append(location)
                        count += 1
                        print(f"Processed address {count}: {address_text}")
                
                # Save every 20 locations (every 4 pages)
                if count % 20 == 0:
                    save_to_csv(locations)
                    print(f"\nIntermediate save: {count} locations saved to CSV")
                    locations = []
                
                print(f"Completed page {current_page}/{total_pages}")
                current_page += 1
                
            except Exception as e:
                print(f"Error processing page {current_page}: {str(e)}")
                current_page += 1
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
    scrape_rackroom_locations()