import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import time
import random

# Set up random user agent
software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
user_agent = user_agent_rotator.get_random_user_agent()

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--headless=new")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

actions = ActionChains(driver)

def random_wait():
    time.sleep(random.randint(4, 9))

def scroll_down():
    actions.send_keys(Keys.PAGE_DOWN).perform()

def search_business_and_address(business_name, street_address):
    query = f"{business_name} {street_address}"
    url = f"https://www.google.com/maps/search/{query}"
    driver.get(url)
    random_wait()

    try:
        # Get the page HTML source
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        address_element = soup.find(class_="Io6YTe")
        full_address = address_element.text if address_element else 'Address not found'
        return full_address

    except Exception as e:
        print(f"Error finding address: {e}")
        return 'Address not found'

# Load the CSV file
csv_file_path = 'reo-tx.csv'
df = pd.read_csv(csv_file_path)

# Add a new column for the full address
df['Full Address'] = ''

# Iterate over each row and search for the full address
for index, row in df.iterrows():
    business_name = row['Name']
    street_address = row["Address"]
    full_address = search_business_and_address(business_name, street_address)
    df.at[index, 'Full Address'] = full_address
    print(f"Completed: {business_name}, {street_address} -> {full_address}")
    # Save every 200 entries
    if (index + 1) % 200 == 0:
        partial_output_path = f'Real Estate Agencies - Partial {index + 1}.csv'
        df.to_csv(partial_output_path, index=False)
        print(f"Partial save completed: {partial_output_path}")

# Save the updated dataframe back to a new CSV file
output_csv_file_path = 'reo-tx-final.csv'
df.to_csv(output_csv_file_path, index=False)

driver.quit()

output_csv_file_path

