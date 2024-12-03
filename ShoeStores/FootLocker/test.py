from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import csv
from pathlib import Path

def collect_and_save_state_urls():
    """
    First phase: Collect all state URLs and save them to a CSV file.
    This only needs to be run once to create our initial dataset.
    """
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options)
    
    state_data = []
    try:
        # Navigate to the main page and collect state information
        driver.get("https://stores.footlocker.com/browse/")
        time.sleep(3)
        states = driver.find_elements(By.CSS_SELECTOR, "div.map-list-item.is-single a")
        
        # Extract state information and store it in a structured format
        for state in states:
            state_data.append({
                'state_name': state.text.split('(')[0],  # Remove the store count
                'store_count': state.text.split('(')[1].rstrip(')'),
                'url': state.get_attribute('href')
            })
        
        # Save the collected data to a CSV file
        df = pd.DataFrame(state_data)
        df.to_csv('state_urls.csv', index=False)
        print(f"Saved {len(state_data)} state URLs to state_urls.csv")
        
    finally:
        driver.quit()
    return state_data

def collect_city_data(state_urls_file='state_urls.csv', output_file='city_data.csv'):
    """
    Second phase: Use the saved state URLs to collect city information.
    This function can be run separately and includes progress tracking.
    """
    # Read our saved state URLs
    states_df = pd.read_csv(state_urls_file)
    
    # Create or append to our cities file
    mode = 'a' if Path(output_file).exists() else 'w'
    with open(output_file, mode, newline='') as f:
        writer = csv.writer(f)
        if mode == 'w':  # Write headers only for new file
            writer.writerow(['state_name', 'city_name', 'city_stores', 'city_url'])
        
        driver = webdriver.Chrome()
        try:
            # Process each state from our saved data
            for index, row in states_df.iterrows():
                print(f"\nProcessing {row['state_name']} ({index + 1}/{len(states_df)})")
                
                driver.get(row['url'])
                time.sleep(2)  # Reduced wait time for efficiency
                
                city_elements = driver.find_elements(By.CSS_SELECTOR, 
                                                    "div.map-list-item.is-single a[data-city-item]")
                
                for city in city_elements:
                    city_name = city.text.split('(')[0].strip()
                    city_stores = city.text.split('(')[1].rstrip(')')
                    city_url = city.get_attribute('href')
                    
                    # Write each city's data immediately to the CSV
                    writer.writerow([row['state_name'], city_name, city_stores, city_url])
                    f.flush()  # Ensure data is written to file
                
                print(f"Processed {len(city_elements)} cities")
                
        finally:
            driver.quit()

def main():
    # Check if we already have state URLs saved
    if not Path('state_urls.csv').exists():
        print("Collecting state URLs...")
        collect_and_save_state_urls()
    
    # Collect city data using saved state URLs
    print("\nCollecting city data...")
    collect_city_data()

if __name__ == "__main__":
    main()