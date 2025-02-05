import argparse
from datetime import datetime
import logging
import os
import requests
from bs4 import BeautifulSoup
from lxml import html
import json
import sqlite3

class EbayScraper:
    def add_arguments(self, parser):
        parser.add_argument('search_title', type=str, nargs='?', default='Pokemon Card', help='Enter the eBay search title')

    def handle(self, title):
        logging.info("Starting eBay scraper...")
        num_pages = 9
        self.scrape_and_store(title, num_pages)
        response = self.check_price_changes()
        logging.info("eBay scraper completed.")

    def scrape_and_store(self, title, num_pages):
        logging.info("Scraping eBay data...")
        conn = sqlite3.connect('./db.sqlite3')
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Price_Fluctuations (
                ebay_id TEXT PRIMARY KEY,
                title TEXT,
                price REAL,
                link TEXT,
                image_folder_path TEXT
            )
        """)
        conn.commit()
        base_url = f'https://www.ebay.com/sch/i.html?_nkw={title.replace(" ", "+")}'
        for page in range(1, num_pages + 1):
            url = f'{base_url}&_pgn={page}'
            soup = self.get_data(url)
            productslist = self.parse(soup, url)
            for product in productslist:
                ebay_id = product['ebay_id']
                title = product['title']
                price = float(product['price'])
                link = product['link']
                folder_path = os.path.join(os.getcwd(), 'Images', ebay_id)
                cursor.execute("SELECT ebay_id FROM Price_Fluctuations WHERE ebay_id=?", (ebay_id,))
                existing_ebay_id = cursor.fetchone()
                if existing_ebay_id:
                    cursor.execute("UPDATE Price_Fluctuations SET image_folder_path=? WHERE ebay_id=?", (folder_path, ebay_id))
                else:
                    cursor.execute("""
                        INSERT INTO Price_Fluctuations (ebay_id, title, price, link, image_folder_path) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (ebay_id, title, price, link, folder_path))
                conn.commit()
        conn.close()
        logging.info("Scraping and storing data completed.")

    def get_data(self, url):
        logging.info(f"Getting data from URL: {url}")
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup

    def check_price_changes(self):
        logging.info("Checking price changes...")
        conn = sqlite3.connect('./db.sqlite3')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Price_Fluctuations")
        products = cursor.fetchall()
        response_list = []
        for product in products:
            ebay_id, title, price, link, image_folder_path = product
            response = requests.get(link)
            first_xpath = '//*[@id="mainContent"]/div[1]/div[3]/div/div/div/span/text()'
            second_xpath = '//*[@id="mainContent"]/div[1]/div[3]/div/div/div[1]/span'
            tree = html.fromstring(response.content)
            # price_elem = tree.xpath('//*[@id="mainContent"]/div[1]/div[3]/div/div/div/span/text()')
            # Attempt to extract text using the first XPath
            price_elem = tree.xpath(first_xpath)
            if not price_elem:
                # If first XPath didn't work, try the second XPath
                price_elem = tree.xpath(second_xpath)
            if price_elem:
                price_text = price_elem[0].strip()
                price_text = ''.join(char for char in price_text if char.isdigit() or char == '.')
                current_price = float(price_text) if price_text else None
                # print(price_elem, current_price)
                if current_price != price:
                    percentage_change = ((current_price - price) / price) * 100
                    response = {
                        'ebay_id': ebay_id,
                        'title': title,
                        'previous_price': price,
                        'current_price': current_price,
                        'percentage_change': round(percentage_change, 2),
                        'link': link,
                        'image_folder_path': image_folder_path
                    }
                    response_list.append(response)
                    cursor.execute("UPDATE Price_Fluctuations SET price=? WHERE ebay_id=?", (current_price, ebay_id))
                    conn.commit()
            else:
                logging.warning(f"Price element not found for eBay ID: {ebay_id}")
        conn.close()
        logging.info("Price change check completed.")
        file_path = "./app/static/price_fluctuations.json"
        # Write JSON data to the file
        with open(file_path, "w") as json_file:
            json.dump(response_list, json_file)
        return json.dumps(response_list)

    def parse(self, soup, url):
        logging.info("Parsing data...")
        productslist = []
        results = soup.find_all('div', {'class': 's-item__info clearfix'})
        for item in results:
            title_elem = item.find('div', {'class': 's-item__title'})
            price_elem = item.find('span', {'class': 's-item__price'})
            link_elem = item.find('a', {'class': 's-item__link'})
            if title_elem and price_elem and link_elem:
                product = {
                    'title': title_elem.text,
                    'price': self.extract_highest_price(price_elem.text.replace('$', '').replace(',', '').strip()),
                    'link': link_elem['href']
                }
                product['ebay_id'] = self.extract_ebay_id(product['link'])
                productslist.append(product)
            else:
                logging.warning(f"Skipping product at URL: {url} due to missing information.")
        return productslist

    def extract_ebay_id(self, ebay_link):
        logging.info("Extracting eBay ID...")
        try:
            return ebay_link.split('/')[-1].split('?')[0]
        except (IndexError, ValueError):
            return None

    def extract_highest_price(self, price_str):
        logging.info("Extracting highest price...")
        if ' to ' in price_str:
            prices = [float(val) for val in price_str.split(' to ')]
            highest_price = max(prices)
        else:
            highest_price = float(price_str)
        return highest_price

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    scraper = EbayScraper()

    scraper.add_arguments(parser)  # Add the argument with default value

    args = parser.parse_args()

    try:
        scraper.handle(args.search_title)
    except Exception as e:
        logging.error("An error occurred: %s", e)