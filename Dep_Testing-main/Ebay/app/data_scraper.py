import os
import requests
from bs4 import BeautifulSoup
from lxml import html, etree
from datetime import datetime

import sqlite3

from django.db import connection


# Create a SQLite database connection
# db_path = '../Ebay/db.sqlite3'  # Update this with the actual path
# conn = sqlite3.connect(db_path)
# conn.execute('PRAGMA foreign_keys = ON;')

# # Create a table to store product data
# conn.execute('''
# CREATE TABLE IF NOT EXISTS Product (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     title TEXT,
#     price REAL,
#     link TEXT,
#     updated_date TEXT,
#     condition TEXT,
#     rarity TEXT,
#     game_name TEXT,
#     specialty TEXT,
#     card_name TEXT,
#     manufacturer TEXT,
#     material TEXT,
#     card_type TEXT,
#     ebay_id TEXT UNIQUE
# );
# ''')

# def connect_to_database(db_path):
    # Connect to the SQLite database
    # conn = sqlite3.connect(db_path)
    # conn.execute('PRAGMA foreign_keys = ON;')
    # return conn

# def create_product_table(conn):
    # Create a table to store product data
    # conn.execute('''
    #     CREATE TABLE IF NOT EXISTS Product (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         title TEXT,
    #         price REAL,
    #         link TEXT,
    #         updated_date TEXT,
    #         condition TEXT,
    #         rarity TEXT,
    #         game_name TEXT,
    #         specialty TEXT,
    #         card_name TEXT,
    #         manufacturer TEXT,
    #         material TEXT,
    #         card_type TEXT,
    #         ebay_id TEXT UNIQUE
    #     );
    # ''')                        

def get_data(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

def parse(soup):
    productslist = []
    results = soup.find_all('div', {'class': 's-item__info clearfix'})
    for item in results:
        product = {
            'title': item.find('div', {'class': 's-item__title'}).text,
            'price': item.find('span', {'class': 's-item__price'}).text.replace('$', '').replace(',', '').strip(),
            'link': item.find('a', {'class': 's-item__link'})['href']
        }
        productslist.append(product)
    return productslist

def extract_highest_price(price_str):
    if ' to ' in price_str:
        prices = [float(val) for val in price_str.split(' to ')]
        highest_price = max(prices)
    else:
        highest_price = float(price_str)
    return highest_price

def extract_updated_date(link):
    item_response = requests.get(link)
    item_soup = BeautifulSoup(item_response.text, 'html.parser')
    updated_date_element = item_soup.find('div', class_='ux-layout-section__textual-display ux-layout-section__textual-display--revisionHistory')
    if updated_date_element:
        updated_date_span = updated_date_element.find_all('span')[1]  # Get the second span element
        updated_date = updated_date_span.text.strip()
    else:
        updated_date = 'Updated date not available'
    
    return updated_date

def extract_condition(link, xpath):
    item_response = requests.get(link)
    tree = html.fromstring(item_response.content)
    condition_element = tree.xpath(xpath)
    if condition_element:
        condition = condition_element[0].text_content().strip()
    else:
        condition = 'Condition not found on the webpage.'
    return condition

def extract_rarity(url):
    response = requests.get(url)
    if response.status_code == 200:
        tree = etree.HTML(response.text)
        xpath_expr = '//*[@id="viTabs_0_is"]/div/div[2]/div/div[1]/div[2]/dl/dd/div/div/span'
        rarity_element = tree.xpath(xpath_expr)
        if rarity_element and len(rarity_element) > 0:  # Check if rarity_element is not None and not empty
            rarity_text = rarity_element[0].text
            if rarity_text:  # Check if rarity_text is not None or empty
                return rarity_text.strip().lower()
            else:
                return "Rarity information not available."
        else:
            return "Rarity element not found."
    else:
        return "Failed to fetch the URL: " + str(response.status_code)

def extract_game_name_from_url(url, xpath):
    response = requests.get(url)
    if response.status_code == 200:
        tree = html.fromstring(response.content)
        game_name_element = tree.xpath(xpath)
        if game_name_element:
            game_name = game_name_element[0].text_content().strip()
            return game_name
        else:
            return "Game name not found on the webpage."
    else:
        return "Failed to fetch the webpage. Status code: {}".format(response.status_code)

def extract_specialty_from_url(url, xpath):
    response = requests.get(url)
    if response.status_code == 200:
        tree = html.fromstring(response.content)
        specialty_element = tree.xpath(xpath)
        if specialty_element:
            specialty = specialty_element[0].text_content().strip()
            return specialty
        else:
            return "Specialty not found on the webpage."
    else:
        return "Failed to fetch the webpage. Status code: {}".format(response.status_code)

def extract_card_name_from_url(url, xpath):
    response = requests.get(url)
    if response.status_code == 200:
        tree = html.fromstring(response.content)
        card_name_element = tree.xpath(xpath)
        if card_name_element:
            card_name = card_name_element[0].text_content().strip()
            return card_name
        else:
            return "Card name not found on the webpage."
    else:
        return "Failed to fetch the webpage. Status code: {}".format(response.status_code)

def extract_manufacturer_from_url(url, xpath):
    response = requests.get(url)
    if response.status_code == 200:
        tree = html.fromstring(response.content)
        manufacturer_element = tree.xpath(xpath)
        if manufacturer_element:
            manufacturer = manufacturer_element[0].text_content().strip()
            return manufacturer
        else:
            return "Manufacturer not found on the webpage."
    else:
        return "Failed to fetch the webpage. Status code: {}".format(response.status_code)

def extract_material_from_url(url, xpath):
    response = requests.get(url)
    if response.status_code == 200:
        tree = html.fromstring(response.content)
        material_element = tree.xpath(xpath)
        if material_element:
            material = material_element[0].text_content().strip()
            return material
        else:
            return "Material information not found on the webpage."
    else:
        return "Failed to fetch the webpage. Status code: {}".format(response.status_code)

def extract_card_type_from_url(url, xpath):
    response = requests.get(url)
    if response.status_code == 200:
        tree = html.fromstring(response.content)
        card_type_element = tree.xpath(xpath)
        if card_type_element:
            card_type = card_type_element[0].text_content().strip()
            return card_type
        else:
            return "Card Type information not found on the webpage."
    else:
        return "Failed to fetch the webpage. Status code: {}".format(response.status_code)

from datetime import datetime

def save_to_database(product):
    ebay_id = product['link'].split('/')[-1].split('?')[0]
    price_str = product['price']
    price = extract_highest_price(price_str)
    date_str = product['updated_date']

    # Define a dictionary for mapping month names to their respective numbers
    month_map = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
        "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
    }

    # Split the input date string into parts
    parts = date_str.split()

    # Check if the date string has enough parts
    if len(parts) >= 4:
        month = month_map.get(parts[0], None)
        day = parts[1][:-1] if len(parts[1]) >= 2 else None
        year = parts[2]
        time = parts[3]

        # Check if all date components are valid
        if month and day and year and time:
            # Concatenate the components in the desired format
            formatted_date = f"{year}-{month}_{day}"

            # Use Django's parameterized query approach
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id FROM Product WHERE ebay_id = %s
                    """,
                    [ebay_id]
                )
                existing_record = cursor.fetchone()

                if existing_record:
                    print(f"Updating product with existing ebay_id: {ebay_id}")
                    existing_id = existing_record[0]

                    cursor.execute(
                        """
                        UPDATE Product
                        SET title = %s, price = %s, updated_date = %s
                        WHERE id = %s
                        """,
                        [product['title'], price, formatted_date, existing_id]
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO Product (
                            title, price, link, updated_date, condition, rarity, game_name, specialty,
                            card_name, manufacturer, material, card_type, ebay_id
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            product['title'], price, product['link'], formatted_date,
                            product.get('condition', ''), product.get('rarity', ''), product.get('game_name', ''),
                            product.get('specialty', ''), product.get('card_name', ''), product.get('manufacturer', ''),
                            product.get('material', ''), product.get('card_type', ''), ebay_id
                        )
                    )

            # Commit the transaction
            connection.commit()
        else:
            print("Invalid date format."+date_str)
    else:
        print("Invalid date format."+date_str)

def scrape_and_save(data):
    base_url = data.get('base_url', '')
    num_pages = data.get('num_pages', 0)
    xpath_condition = data.get('xpath_condition', '')
    xpath_rarity = data.get('xpath_rarity', '')
    xpath_specialty = data.get('xpath_specialty', '')
    xpath_card_name = data.get('xpath_card_name', '')
    xpath_manufacturer = data.get('xpath_manufacturer', '')
    xpath_material = data.get('xpath_material', '')
    xpath_card_type = data.get('xpath_card_type', '')

    for page in range(1, num_pages + 1):
        url = base_url + '&_pgn=' + str(page)
        soup = get_data(url)
        productslist = parse(soup)
        for product in productslist:
            updated_date = extract_updated_date(product['link'])
            product['updated_date'] = updated_date
            condition = extract_condition(product['link'], xpath_condition)
            product['condition'] = condition
            rarity = extract_rarity(product['link'])  # Use extract_rarity with just the URL parameter
            if rarity != "Rarity element not found.":
                product['rarity'] = rarity
            else:
                product['rarity'] = "N/A"  # Handle the absence of rarity information appropriately
            game_name = extract_game_name_from_url(product['link'], '//*[@id="viTabs_0_is"]/div/div[2]/div/div[2]/div[1]/dl/dd/div/div')
            product['game_name'] = game_name
            specialty = extract_specialty_from_url(product['link'], xpath_specialty)
            product['specialty'] = specialty
            card_name = extract_card_name_from_url(product['link'], xpath_card_name)
            product['card_name'] = card_name
            manufacturer = extract_manufacturer_from_url(product['link'], xpath_manufacturer)
            product['manufacturer'] = manufacturer
            material = extract_material_from_url(product['link'], xpath_material)
            product['material'] = material
            card_type = extract_card_type_from_url(product['link'], xpath_card_type)
            product['card_type'] = card_type
            
            save_to_database(product)


# Close the SQLite database connection after scraping and saving
# db_path = 'Ebay/db.sqlite3' 
# db_path = '/home/ibtasamahmad/AI ML/Ebay_Application/Ebay/db.sqlite3'
# conn = connect_to_database(db_path)
# create_product_table(conn)
# conn.commit()
# conn.close()
# conn.close()
