import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sqlite3
import logging
import time

class eBayScraper:
    def __init__(self, title='Pokemon Card', num_pages=9):
        self.title = title
        self.num_pages = num_pages

    def add_arguments(self, parser):
        parser.add_argument('title', type=str, nargs='?', default='Pokemon Card', help='Enter the eBay search title')

    def handle(self):
        conn = sqlite3.connect('test.db')
        # conn = sqlite3.connect('./db.sqlite3')

        def get_data(url):
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            return soup

        def extract_ebay_id(ebay_link):
            return ebay_link.split('/')[-1].split('?')[0]  # Extract ID before the '?'

        def parse(soup):
            productslist = []
            results = soup.find_all('div', {'class': 's-item__info clearfix'})
            for item in results:
                product = {
                    'title': item.find('div', {'class': 's-item__title'}).text,
                    'price': item.find('span', {'class': 's-item__price'}).text.replace('$', '').replace(',', '').strip(),
                    'link': item.find('a', {'class': 's-item__link'})['href']
                }
                # Extract eBay ID and add it to the product dictionary
                product['ebay_id'] = extract_ebay_id(product['link'])
                productslist.append(product)
            return productslist

        def create_product_prices_table():
            try:
                # Create Product_Prices table with foreign key constraint
                create_table_query = """
                CREATE TABLE IF NOT EXISTS Product_Prices (
                    id INTEGER PRIMARY KEY,
                    ebay_id INTEGER,
                    date TEXT,
                    price REAL,
                    FOREIGN KEY (ebay_id) REFERENCES Product(ebay_id)
                )
                """
                cursor = conn.cursor()
                cursor.execute(create_table_query)
                conn.commit()
            except sqlite3.Error as e:
                print(f"Error creating Product_Prices table: {e}")

        def save_to_database(product):
            ebay_id = product['ebay_id']
            date_today = datetime.now().date().isoformat()
            price = extract_highest_price(product['price'])

            try:
                # Insert data into Product_Prices table
                insert_query = "INSERT INTO Product_Prices (ebay_id, date, price) VALUES (?, ?, ?)"
                cursor = conn.cursor()
                cursor.execute(insert_query, (ebay_id, date_today, price))
                conn.commit()
            except sqlite3.Error as e:
                print(f"Error inserting data into Product_Prices table: {e}")

        def extract_highest_price(price_str):
            if ' to ' in price_str:
                prices = [float(val) for val in price_str.split(' to ')]
                highest_price = max(prices)
            else:
                highest_price = float(price_str)
            return highest_price

        def scrape_and_save(title, num_pages):
            base_url = f'https://www.ebay.com/sch/i.html?_nkw={title.replace(" ", "+")}'
            all_products = []

            for page in range(1, num_pages + 1):
                url = f'{base_url}&_pgn={page}'
                soup = get_data(url)
                productslist = parse(soup)

                for product in productslist:
                    ebay_link = product['link']
                    ebay_id = extract_ebay_id(ebay_link)
                    product['ebay_id'] = ebay_id
                    save_to_database(product)

                all_products.extend(productslist)

            return all_products

        # Create Product_Prices table
        create_product_prices_table()

        # Scrape and save data for the custom title entered by the user
        scraped_products = scrape_and_save(self.title, self.num_pages)

        conn.close()
        logging.info("Successfully completed the scheduled task.")

# Parse command line arguments
parser = argparse.ArgumentParser()
scraper = eBayScraper()
scraper.add_arguments(parser)
args = parser.parse_args()

# Execute the scraper
scraper.handle()

