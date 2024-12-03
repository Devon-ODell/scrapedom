from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import csv
import time
import random

def random_wait():
    # Add variability to our waiting times to appear more human-like
    time.sleep(random.randint(2, 4))

def scrape_nike_locations():
    chromedriver_autoinstaller.install()
    driver = webdriver.Chrome()
    locations = []
    
    try:
        with open('nike-locations2.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Store Name', 'Street Address', 'City', 'State', 'Zip'])
        
        urls = [url.strip() for url in open('state-urls.csv') if url.strip()]
        print(f"Found {len(urls)} URLs to process")
        
        for index, url in enumerate(urls, 1):
            state = url.split('/')[-1].replace('-', ' ').title()
            print(f"\nProcessing {state} ({index}/{len(urls)})")
            
            driver.get(url)
            time.sleep(3)  # Allow page load
            
            store_sections = driver.find_elements(By.CSS_SELECTOR, "a > section.ncss-col-sm-12")
            print(f"Found {len(store_sections)} locations")
            
            for section in store_sections:
                try:
                    name = section.find_element(By.CSS_SELECTOR, "h3.headline-5").text.strip()
                    address_div = section.find_element(By.CSS_SELECTOR, "div.body-2.text-color-secondary")
                    address_parts = [p.text.strip() for p in address_div.find_elements(By.TAG_NAME, "p")]
                    
                    if len(address_parts) >= 2:
                        street = address_parts[-2]
                        city, state_zip = address_parts[-1].split(',', 1)
                        state, zip_code = state_zip.strip().split()[:2]
                        locations.append([name, street, city.strip(), state, zip_code.split(',')[0]])
                        random_wait()
                        
                except Exception as e:
                    print(f"Error with {name if 'name' in locals() else 'store'}: {str(e)}")
            
            # Save progress after each state
            with open('nike-locations2.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(locations)
            locations = []  # Clear list after saving
            
            time.sleep(random.uniform(1, 2))
            
    finally:
        driver.quit()
        print("\nDone scraping")

if __name__ == "__main__":
    scrape_nike_locations()