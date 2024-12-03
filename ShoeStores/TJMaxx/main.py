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
    time.sleep(random.randint(3, 5))

def save_to_csv(locations, filename='locations.csv'):
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        for loc in locations:
            writer.writerow(loc)

def scrape_locations():
    chromedriver_autoinstaller.install()
    options = Options()
    driver = webdriver.Chrome(options=options)
    locations = []
    count = 0
    
    try:
        driver.get("https://tjmaxx.tjx.com/store/stores/allStores.jsp")
        
        # Handle popup
        wait = WebDriverWait(driver, 10)
        popup_close = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "bx-close-inside")))
        popup_close.click()
        random_wait()
        
        # Initialize CSV
        with open('locations.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Store', 'Street', 'City', 'State', 'Zip'])
        
        # Get list of states
        state_elements = driver.find_elements(By.CSS_SELECTOR, "div.state-filter > div.accordion")
        print(f"Found {len(state_elements)} state elements")
        
        for index, state_element in enumerate(state_elements, 1):
            try:
                # Print state name for debugging
                state_name = state_element.text
                print(f"\nProcessing state {index}: {state_name}")
                
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView(true);", state_element)
                time.sleep(1)
                
                # Click the state
                state_element.click()
                random_wait()
                
                # Get the number of stores from the state name (e.g., "Alabama (29)")
                expected_stores = int(state_name.split('(')[1].split(')')[0])
                print(f"Expecting {expected_stores} stores")
                
                # Find stores within this state's panel
                stores = driver.find_elements(By.CSS_SELECTOR, f"div.panel[style*='display: block'] .storelist-item")
                print(f"Found {len(stores)} stores in {state_name}")
                
                store_count = 0
                for store in stores:
                    try:
                        street = store.find_element(By.CLASS_NAME, "street-address").text
                        city = store.find_element(By.CLASS_NAME, "locality").text
                        state = store.find_element(By.CLASS_NAME, "region").text
                        zip_code = store.find_element(By.CLASS_NAME, "postal-code").text
                        
                        if street and city and state and zip_code:  # Only process if all fields have data
                            location = ["TJ Maxx", street, city, state, zip_code]
                            locations.append(location)
                            count += 1
                            store_count += 1
                            print(f"Processed store: {city}, {state}")
                            time.sleep(1)
                            if store_count >= expected_stores:
                                break
                            
                    except Exception as e:
                        print(f"Error processing store: {str(e)}")
                        continue
                
            except Exception as e:
                print(f"Error processing state {state_name}: {str(e)}")
                continue
            
        # Save all locations
        if locations:
            save_to_csv(locations)
            print(f"\nSaved {count} total locations")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_locations()

