import time
import pandas as pd
from selenium import webdriver
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

# Load the zip codes from the CSV file
zipcodes_path = os.path.join(os.path.dirname(__file__), 'zipcodes.csv')
zipcodes_df = pd.read_csv(zipcodes_path)
zipcodes = zipcodes_df['zipcode'].tolist()

# Set up the Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Function to search for coffee shops in a specific zip code
def search_coffee_shops(zipcode):
    search_url = f'https://www.google.com/maps'
    driver.get(search_url)
    
    # Allow the page to load
    time.sleep(2)

    # Search for "coffee shops in {zipcode}"
    search_box = driver.find_element(By.XPATH, "//input[@id='searchboxinput']")
    search_box.send_keys(f'coffee shops in {zipcode}')
    search_box.send_keys(Keys.ENTER)

    # Allow results to load
    time.sleep(5)

    # Extract coffee shop details
    coffee_shops = []
    results = driver.find_elements(By.XPATH, "//div[contains(@class, 'section-result-content')]//h3")
    for result in results:
        name = result.text
        coffee_shops.append({'name': name, 'zipcode': zipcode})

    return coffee_shops

# Iterate through each zip code and gather coffee shop data
all_coffee_shops = []
for zipcode in zipcodes:
    try:
        coffee_shops = search_coffee_shops(zipcode)
        all_coffee_shops.extend(coffee_shops)
    except Exception as e:
        print(f"Error occurred for zipcode {zipcode}: {e}")

# Save results to a CSV file
output_path = os.path.join(os.path.dirname(__file__), 'coffee_shops.csv')
coffee_shops_df = pd.DataFrame(all_coffee_shops)
coffee_shops_df.to_csv(output_path, index=False)

# Close the driver
driver.quit()

