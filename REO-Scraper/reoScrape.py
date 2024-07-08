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
import csv
import random

# URL of the web page
url = "https://www.google.com/maps/search/\"real+estate+agency\"+" "\"TX\""

# Set up random user agent
software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
user_agent = user_agent_rotator.get_random_user_agent()

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument(f'user-agent={user_agent}')
# Set up the WebDriver with proxy
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define the actions
actions = ActionChains(driver)

#Basic Functions
def random_wait():
    time.sleep(random.randint(7, 12))
# Function to scroll down
def scroll_down():
    actions.send_keys(Keys.PAGE_DOWN).perform()

driver.get(url)
random_wait()

# Function to click on each element
def click_elements():
    elements = driver.find_elements(By.CSS_SELECTOR, ".Nv2PK.THOPZb.CpccDe")
    for index, elem in elements:
        try:
            
            actions.move_to_element(elem).click().perform()
            random_wait()
            
            # Get the page HTML source
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            address_element = soup.find(class_="Io6YTe")
            random_wait()
            # Specify the CSV file path
            csv_file_path = 'TX-REO.csv'
            # Open a CSV file in append mode
            with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
                # Create a CSV writer object
                csv_writer = csv.writer(csv_file)
                
                # Write the header row only if the file is empty
                if csv_file.tell() == 0:
                    csv_writer.writerow(['Place', 'Address'])
                
                # Write the extracted data
                title_text = "Real Estate Agencies, TX"
                address_text = address_element.text if address_element else 'Address not found'
                csv_writer.writerow([title_text, address_text]) 
            
            
            # After extraction, navigate back to the results page
            driver.back()
            time.sleep(2)

            # Scroll down after every 4 elements
            if index % 4 == 0:
                scroll_down()
        except Exception as e:
            print(f"Error clicking element: {e}")

# Scroll and click elements multiple times
for _ in range(10):  # Adjust the range as needed to ensure all elements are covered
    scroll_down()
    click_elements()

# Close the browser
driver.quit()
