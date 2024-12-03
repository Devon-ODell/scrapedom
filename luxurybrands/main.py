import requests
from bs4 import BeautifulSoup
import csv
import time
from urllib.parse import urljoin

base_url = "https://locations.michaelkors.com/"
headers = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_soup(url):
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise exception for HTTP errors
    return BeautifulSoup(response.text, 'html.parser')

def get_states():
    url = urljoin(base_url, "us.html")
    soup = fetch_soup(url)
    state_links = []
    # Select all state links
    for state in soup.select('ul.c-directory-list-content a.c-directory-list-content-item-link'):
        href = state.get('href')
        state_name = state.text.strip()
        full_url = urljoin(url, href)
        state_links.append((state_name, full_url))
    return state_links

def get_cities_or_stores(state_url):
    soup = fetch_soup(state_url)
    city_or_store_links = []
    # Select all city or store links
    entries = soup.select('ul.c-directory-list-content a.c-directory-list-content-item-link')
    if entries:
        for entry in entries:
            href = entry.get('href')
            name = entry.text.strip()
            full_url = urljoin(state_url, href)
            city_or_store_links.append((name, full_url))
    return city_or_store_links

def is_store_page(soup):
    return bool(soup.find('address', class_='c-address'))

def extract_store_info(soup, processed_addresses):
    stores = []
    # Find all address tags directly
    address_tags = soup.find_all('address', class_='c-address')
    for address_tag in address_tags:
        # Extract address components
        street_address1 = address_tag.find('span', class_='c-address-street-1')
        street_address2 = address_tag.find('span', class_='c-address-street-2')
        city = address_tag.find('span', class_='c-address-city')
        state = address_tag.find('abbr', class_='c-address-state')
        postal_code = address_tag.find('span', class_='c-address-postal-code')

        # Combine street addresses
        street = ''
        if street_address1:
            street += street_address1.get_text(strip=True)
        if street_address2:
            street += ' ' + street_address2.get_text(strip=True)

        # Format city information
        city_info = ''
        if city:
            city_info += city.get_text(strip=True)
        if state:
            city_info += ', ' + state.get_text(strip=True)
        if postal_code:
            city_info += ' ' + postal_code.get_text(strip=True)

        # Assemble full address
        full_address = f"{street}, {city_info}"

        # Check if address is already processed
        if full_address in processed_addresses:
            continue  # Skip duplicate address
        processed_addresses.add(full_address)

        # Build the store info dictionary
        store_info = {
            'company': 'Michael Kors',
            'street': street,
            'city': city_info,
        }
        stores.append(store_info)

        # Print the full address
        print(f"Extracted Address: {full_address}")

    return stores

def main():
    all_stores = []
    processed_addresses = set()
    state_links = get_states()
    print(f"Found {len(state_links)} states.")

    for state_name, state_url in state_links:
        print(f"\nProcessing state: {state_name}")
        entries = get_cities_or_stores(state_url)

        if not entries:
            print(f"No entries found for {state_name}, skipping.")
            continue

        for name, url in entries:
            print(f"Processing: {name}")
            soup = fetch_soup(url)

            if is_store_page(soup):
                # Directly extract store info
                stores = extract_store_info(soup, processed_addresses)
                all_stores.extend(stores)
            else:
                # Assume it's a city page; get stores within the city
                sub_entries = get_cities_or_stores(url)
                if not sub_entries:
                    print(f"No sub-entries found for {name}, skipping.")
                    continue
                for sub_name, sub_url in sub_entries:
                    print(f"Processing store: {sub_name}")
                    soup = fetch_soup(sub_url)
                    if is_store_page(soup):
                        stores = extract_store_info(soup, processed_addresses)
                        all_stores.extend(stores)
                    else:
                        print(f"Unexpected structure at {sub_url}")
                    time.sleep(1)  # Be polite
            time.sleep(1)  # Be polite
        time.sleep(1)  # Be polite

    # Save the data to CSV
    fieldnames = ['company', 'street', 'city']
    with open('MK-USA.CSV', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for store in all_stores:
            writer.writerow(store)

    print("\nScraping complete.")
    print(f"Total stores found: {len(all_stores)}")

if __name__ == "__main__":
    main()

