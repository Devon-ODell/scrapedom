from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import random

def scrape_footlocker_locations():
    driver = webdriver.Chrome()
    
    try:
        # Read URLs and create output file
        with open('store-urls.csv', 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        with open('footlocker-locations.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Store Name', 'Full Address'])
        
        print(f"Found {len(urls)} URLs to process")
        processed_count = 0
        
        for url_index, url in enumerate(urls, 1):
            try:
                driver.get(url)
                time.sleep(2)  # Wait for page load
                
                # Find all store listings on the page
                store_listings = driver.find_elements(By.CLASS_NAME, "map-list-item")
                
                for store in store_listings:
                    try:
                        # Get store name
                        name_element = store.find_element(By.CLASS_NAME, "location-name")
                        store_name = name_element.text.replace('\n', ' ').strip()
                        
                        # Get address
                        address_div = store.find_element(By.CSS_SELECTOR, 
                            'div.address[data-show-on-countries="US, CA, PR, GU, VI"]')
                        address_parts = address_div.find_elements(By.TAG_NAME, "div")
                        time.sleep(3)
                        
                        street = address_parts[0].text.strip()
                        city_state_zip = address_parts[1].text.strip()
                        
                        # Format full address
                        full_address = f"{store_name}, {street}, {city_state_zip}"
                        processed_count += 1
                        
                        # Save to CSV
                        with open('footlocker-locations.csv', 'a', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow([store_name, full_address])
                        
                        print(f"Processed {processed_count}: {full_address}")
                        
                    except Exception as e:
                        print(f"Error processing store in {url}: {str(e)}")
                        continue
                
                print(f"\nCompleted URL {url_index}/{len(urls)} with {len(store_listings)} stores")
                
            except Exception as e:
                print(f"Error processing URL {url}: {str(e)}")
                continue
            
            time.sleep(random.uniform(3, 5))
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        driver.quit()
        print(f"\nScraping complete. Processed {processed_count} total stores")

if __name__ == "__main__":
    scrape_footlocker_locations()