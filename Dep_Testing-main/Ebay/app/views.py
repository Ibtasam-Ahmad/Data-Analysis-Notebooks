from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.decorators import api_view


from django.views import View
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.utils import OperationalError


from statsmodels.tsa.seasonal import seasonal_decompose
from prophet import Prophet
import pandas as pd
import logging


from .image_downloader import save_images  
from .data_scraper import scrape_and_save  

import os
import sqlite3

from django.http import JsonResponse
import json

# Create your views here.

class ScrapeEbay(APIView):
    conn = sqlite3.connect('db.sqlite3')
    conn.execute('PRAGMA foreign_keys = ON;')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price REAL,
            link TEXT,
            updated_date DATETIME,
            condition TEXT,
            rarity TEXT,
            game_name TEXT,
            specialty TEXT,
            card_name TEXT,
            manufacturer TEXT,
            material TEXT,
            card_type TEXT,
            ebay_id TEXT UNIQUE
        );
    ''') 
    def post(self, request, *args, **kwargs):
        title = request.data.get('title', '')  # Extract the title from request data

        if not title:
            return Response({'error': 'Title parameter is required'}, status=400)

        base_url = f'https://www.ebay.com/sch/i.html?_nkw={title}'
        num_pages = 9
        xpath_condition = '//*[@id="viTabs_0_is"]/div/div[2]/div/div[1]/div[1]'
        xpath_rarity = '//*[@id="viTabs_0_is"]/div/div[2]/div/div[1]/div[2]/dl/dd/div/div/span'
        xpath_specialty = '//*[@id="viTabs_0_is"]/div/div[2]/div/div[2]/div[2]/dl/dd/div/div'
        xpath_card_name = '//*[@id="viTabs_0_is"]/div/div[2]/div/div[3]/div[1]/dl/dd/div/div'
        xpath_manufacturer = '//*[@id="viTabs_0_is"]/div/div[2]/div/div[3]/div[2]/dl/dd/div/div'
        xpath_material = '//*[@id="viTabs_0_is"]/div/div[2]/div/div[4]/div[1]/dl/dd/div/div'
        xpath_card_type = '//*[@id="viTabs_0_is"]/div/div[2]/div/div[4]/div[2]/dl/dd/div/div'

        data = {
            'base_url': base_url,
            'num_pages': num_pages,
            'xpath_condition': xpath_condition,
            'xpath_rarity': xpath_rarity,
            'xpath_specialty': xpath_specialty,
            'xpath_card_name': xpath_card_name,
            'xpath_manufacturer': xpath_manufacturer,
            'xpath_material': xpath_material,
            'xpath_card_type': xpath_card_type,
        }

        scrape_and_save(data)
        
        return Response({'message': 'Scraping and saving completed'})
    conn.close()

class SearchAndDownloadImages(APIView):
    def post(self, request, format=None):
        # Get the title from the request data
        title = request.data.get('title', '')

        if not title:
            return Response({'error': 'Title parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        base_url = f'https://www.ebay.com/sch/i.html?_nkw={title}'
        num_pages = 9  # Example: Scraping first 9 pages

        try:
            save_images(base_url, num_pages)
            return Response({'message': 'Images downloaded successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class ManageImagePaths(APIView):
    def post(self, request, format=None):
        # Connect to the SQLite database
        conn = sqlite3.connect('db.sqlite3')
        conn.execute('PRAGMA foreign_keys = ON;')

        try:
            # Create ImagePaths table if not exists
            conn.execute('''
            CREATE TABLE IF NOT EXISTS ImagePaths (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ebay_id TEXT,
                folder_path TEXT,
                FOREIGN KEY (ebay_id) REFERENCES Product(ebay_id)
            );
            ''')

            # Function to insert data into ImagePaths table
            def insert_image_path(ebay_id, folder_path):
                try:
                    conn.execute("INSERT INTO ImagePaths (ebay_id, folder_path) VALUES (?, ?)", (ebay_id, folder_path))
                    conn.commit()
                    print(f"Image path for eBay ID {ebay_id} saved to ImagePaths table successfully.")
                except sqlite3.IntegrityError as e:
                    print("Error inserting data into ImagePaths table:", e)
                    conn.rollback()

            # Function to get eBay IDs from the "Images" subfolder
            def get_ebay_ids_from_images_folder():
                images_folder_path = os.path.join(os.getcwd(), 'Images')
                ebay_ids = []
                if os.path.isdir(images_folder_path):
                    for ebay_id in os.listdir(images_folder_path):
                        ebay_ids.append(ebay_id)
                return ebay_ids

            # Get eBay IDs from "Images" subfolder
            ebay_ids_list = get_ebay_ids_from_images_folder()

            # Insert eBay IDs and folder paths into ImagePaths table
            for ebay_id in ebay_ids_list:
                folder_path = os.path.join(os.getcwd(), 'Images', ebay_id)
                insert_image_path(ebay_id, folder_path)

            return Response({'message': 'Image paths managed successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            # Close the database connection after all operations are done
            conn.close()


class ProductListView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM Product;')
            # products = [dict(row) for row in cursor.fetchall()]  # Convert rows to dictionaries
            products = cursor.fetchall()
        return JsonResponse({'products': products})

class ProductDetailView(APIView):
    def get(self, request, ebay_id):
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM Product WHERE ebay_id = %s;', [ebay_id])
            product = cursor.fetchone()

        if product:
            return JsonResponse({'product': product})
        else:
            return JsonResponse({'error': 'Product not found'}, status=404)

class ProductCreateView(APIView):
    def post(self, request):
        if not request.data:
            return JsonResponse({'error': 'Missing data in request body'}, status=400)

        try:
            data = request.data
            with connection.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO Product (title, price, link, updated_date, condition, rarity, game_name,
                                       specialty, card_name, manufacturer, material, card_type, ebay_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                ''', [
                    data['title'], data['price'], data['link'], data['updated_date'], data['condition'],
                    data['rarity'], data['game_name'], data['specialty'], data['card_name'],
                    data['manufacturer'], data['material'], data['card_type'], data['ebay_id']
                ])
            return JsonResponse({'message': 'Product created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ProductDeleteView(APIView):
    @csrf_exempt
    def delete(self, request, ebay_id):
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM Product WHERE ebay_id = %s;', [ebay_id])
            rows_deleted = cursor.rowcount

        if rows_deleted > 0:
            return JsonResponse({'message': 'Product deleted successfully'})
        else:
            return JsonResponse({'error': 'Product not found'}, status=404)


class ProductUpdateView(APIView):
    def put(self, request, ebay_id):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data in request body'}, status=400)

        # Update product in database
        with connection.cursor() as cursor:
            # Construct the UPDATE query with fields to update based on provided data
            update_query = """
                UPDATE Product
                SET """

            update_params = []
            for field, value in data.items():
                if field not in ['ebay_id']:  # Prevent updating ebay_id (primary key)
                    update_query += f"{field} = %s, "
                    update_params.append(value)

            # Remove trailing comma from update query
            update_query = update_query[:-2]

            update_query += """
                WHERE ebay_id = %s;
            """
            update_params.append(ebay_id)

            cursor.execute(update_query, update_params)

            # Check if update was successful
            if cursor.rowcount > 0:
                return JsonResponse({'message': 'Product updated successfully'})
            else:
                return JsonResponse({'error': 'Product not found or no update performed'}, status=404)
            

# Forecasting Function

logger = logging.getLogger(__name__)

def get_predicted_prices(request, ebay_id):
    try:
        with connection.cursor() as cursor:
            # Fetch data for the specified ebay_id from Product_Prices table
            query = f"SELECT date, price FROM Product_Prices WHERE ebay_id = {ebay_id}"
            cursor.execute(query)
            rows = cursor.fetchall()

            # Convert fetched data to DataFrame
            df_data = pd.DataFrame(rows, columns=['date', 'price'])

            # Check if there's enough data for forecasting
            if len(df_data) < 12:
                return JsonResponse({'error': 'Insufficient data for forecasting'})

            # Perform time series forecasting
            decompose = seasonal_decompose(df_data['price'], model='additive', extrapolate_trend='freq', period=12)
            df_train_prophet = df_data.rename(columns={"date": "ds", "price": "y"})
            model_prophet = Prophet()
            model_prophet.fit(df_train_prophet)

            # Get the last date in the dataset and extend predictions by 6 days
            last_date = df_data['date'].max()
            future_dates = pd.date_range(start=last_date, periods=7)  # Extend by 6 days (total 7 days)

            forecast = model_prophet.predict(pd.DataFrame({'ds': future_dates}))

            # Format prediction dates without time component
            prediction_dates = forecast['ds'].dt.strftime('%Y-%m-%d').tolist()
            predicted_values = forecast['yhat'].tolist()
            lower_values = forecast['yhat_lower'].tolist()
            upper_values = forecast['yhat_upper'].tolist()

            # Return JSON response with prediction data
            response_data = {
                'prediction_dates': prediction_dates,
                'predicted_values': predicted_values,
                'lower_values': lower_values,
                'upper_values': upper_values
            }
            return JsonResponse(response_data)
    except OperationalError as e:
        logger.error(f"Database connection error: {e}")
        return JsonResponse({'error': 'Database connection error'}, status=500)