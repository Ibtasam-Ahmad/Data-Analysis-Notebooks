import re
import requests
from bs4 import BeautifulSoup
import os

# Global variable to store extracted eBay IDs
extracted_ebay_ids = set()

# Function to extract eBay ID from eBay link
def extract_ebay_id(ebay_link):
    pattern = r'\/(\d+)\?'
    match = re.search(pattern, ebay_link)
    if match:
        return match.group(1)
    else:
        return None

# Function to extract and save images
def extract_and_save_images(url, ebay_id):
    try:
        if not url:
            print("Empty URL, skipping image extraction.")
            return

        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for unsuccessful responses

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, "html.parser")

        # Create the initial "Images" folder if it doesn't exist
        os.makedirs("Images", exist_ok=True)

        # Create the subfolder for this eBay ID
        image_folder = os.path.join("Images", ebay_id)
        os.makedirs(image_folder, exist_ok=True)

        # Extract and save images
        image_tags = soup.find_all('img')[1:-4]
        for idx, img in enumerate(image_tags):
            if img.has_attr('src'):
                image_url = img["src"]
                if not image_url:
                    print("Empty image URL, skipping.")
                    continue

                image_name = f"{ebay_id}_{idx+1}.jpg"
                image_path = os.path.join(image_folder, image_name)
                image_content = requests.get(image_url).content
                with open(image_path, "wb") as image_file:
                    image_file.write(image_content)
                print(f"Image {idx+1} saved as: {image_path}")
    except requests.exceptions.HTTPError as err:
        print(f"HTTPError: {err}")

# Function to scrape eBay listings and extract prices, titles, and updated dates
def scrape_ebay_listings(base_url, num_pages):
    all_products = []
    for page in range(1, num_pages + 1):
        url = base_url + '&_pgn=' + str(page)  # Modify URL to navigate through pages
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        results = soup.find_all('div', {'class': 's-item__info clearfix'})
        for item in results:
            product = {
                'title': item.find('div', {'class': 's-item__title'}).text,
                'price': item.find('span', {'class': 's-item__price'}).text.replace('$', '').replace(',', '').strip(),
                'link': item.find('a', {'class': 's-item__link'})['href']
            }
            all_products.append(product)
    return all_products

# Function to extract updated date from eBay listing
def extract_updated_date(link):
    item_response = requests.get(link)
    item_soup = BeautifulSoup(item_response.content, 'html.parser')
    updated_date_element = item_soup.find('span', class_='ux-textspans')
    updated_date = updated_date_element.text.strip() if updated_date_element else 'Updated date not found'
    return updated_date

# Main function to scrape eBay listings and save images
def save_images(base_url, num_pages):
    # Scrape eBay listings
    all_products = scrape_ebay_listings(base_url, num_pages)

    # Output the scraped data to CSV
    for product in all_products:
        # Extract eBay ID
        ebay_id = extract_ebay_id(product['link'])
        if ebay_id and ebay_id not in extracted_ebay_ids:
            print("eBay ID:", ebay_id)
            extracted_ebay_ids.add(ebay_id)
            
            # Extract and save images using eBay ID
            extract_and_save_images(product['link'], ebay_id)
            
            # Extract updated date
            updated_date = extract_updated_date(product['link'])
            product['updated_date'] = updated_date
        else:
            print("Skipping duplicate or empty eBay ID.")

    print('Saved eBay Images')