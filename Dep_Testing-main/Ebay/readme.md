I'd be glad to create a README file for the API endpoints you've provided:

**API Documentation**

This document describes the product information API accessible at `http://127.0.0.1:8000/api/product/`.

**Endpoints**

* **GET http://127.0.0.1:8000/api/product/**

**Fetching all products:**

```
GET http://127.0.0.1:8000/api/product/
```

**Response (example):**

```json
[
  {
    "id": 1,
    "name": "Product A",
    "description": "A great product you'll love!",
    "price": 19.99,
    "category": "Electronics"
  },
  {
    "id": 2,
    "name": "Product B",
    "description": "Another fantastic product for you.",
    "price": 24.50,
    "category": "Clothing"
  }
  // ... more products
]
```

**Fetching a specific product:**

```
GET http://127.0.0.1:8000/api/product/<ebay_id>/ (replace <ebay_id> with the actual eBay ID)
```

**Response (example):**

```json
{
  "id": 12345,
  "name": "Amazing New Gadget",
  "description": "This cutting-edge gadget will change your life!",
  "price": 99.99,
  "category": "Technology",
  "image_url": "https://example.com/images/gadget.jpg"
}
```


**Creating a New Product**

The provided JSON structure lets you create new products via a POST request to `http://127.0.0.1:8000/api/products/create/`. Include the product details (title, price, etc.) in the request body as JSON.

**Example (using cURL):**

```bash
{
  "title": "test product title",
  "price": 123.45,
  "link": "https://www.example.com/your-product-link",
  "updated_date": "2024-05-09T00:00:00.000Z",
  "condition": "New",
  "rarity": "Common",
  "game_name": "Your game name",
  "specialty": "None",
  "card_name": "Your card name",
  "manufacturer": "Your product manufacturer",
  "material": "Plastic",
  "card_type": "Trading Card",
  "ebay_id": "010"
}
```

**Response:**

HTTP 200 OK
Allow: POST, OPTIONS
Content-Type: application/json
Vary: Accept



**Deleting a Product**

Use DELETE on `http://127.0.0.1:8000/api/products/delete/<ebay_id>` (replace `<ebay_id>` with the actual ID) to delete a product. The API will respond with a success message or an error (e.g., product not found).

**Caution:** Deletion is permanent. Ensure proper permissions and intent before deleting.


**Updating a Product**

- **PATCH** `http://127.0.0.1:8000/api/product/update/<ebay_id>`.
- Include only the properties to change in the JSON body (e.g., `title`, `price`).
```bash
{
  "title": "test product title",
  "price": 123.45,
}


**Scraping a Product**

POST http://127.0.0.1:8000/api/scrape-ebay/

Initiates a scrape on eBay to potentially find and add new products based on the provided criteria.
```bash
{
  "title": "Pokemo Card",
}


**Search & Downlaod Images of Product**

POST http://127.0.0.1:8000/api/search-and-download/

Initiates a scrape on eBay to potentially find and add new products images based on the provided criteria.
```bash
{
  "title": "Pokemo Card",
}

**Manage Image Paths**

POST http://127.0.0.1:8000/api/manage-image-paths/

Manage the images paths and save them in the database


** Prediction of Prices***
GET http://127.0.0.1:8000/api/predict/<ebayid>/

Responce:
```
{
  "prediction_dates": [
    "2024-05-08",
    "2024-05-09",
    "2024-05-10",
    "2024-05-11",
    "2024-05-12",
    "2024-05-13",
    "2024-05-14"
  ],
  "predicted_values": [20, 20, 20, 20, 20, 20, 20],
  "lower_values": [19.9999999767146, 19.9999999703113, 19.9999999476425, 19.9999999058832, 19.9999998530098, 19.9999997991289, 19.9999997357318],
  "upper_values": [20.0000000270637, 20.0000000303097, 20.0000000534215, 20.0000000875528, 20.0000001405796, 20.0000001912497, 20.0000002593055]
}
```