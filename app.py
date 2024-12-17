import requests # send http to ebay
from bs4 import BeautifulSoup # parse the html content of the ebay page
import random # used to select the random user agent from a predefined list
import time # used to introduce delays between requests to avoid overwhelming the server
from flask import Flask, jsonify # flask is web framework for backend api and jsonify used to convert python dictionaries into json responses

# create a flask applicatoin instance
app = Flask(__name__)

# List of user agents to mimic different browsers and devices, this help avoid being blocked by ebay anit-scraping measures
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1",
]

def fetch_with_retry(url, retries=5):
    # Set headers to mimic a real browser request
    headers = {
        "User-Agent": random.choice(USER_AGENTS),  # Randomly select a user agent
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.ebay.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Origin": "https://www.ebay.com",
        "Cache-Control": "no-cache",
    }

    # Create a session to manage cookies and headers
    session = requests.Session()
    session.headers.update(headers)

    # Initial request to set cookies
    session.get("https://www.ebay.com/", timeout=10)

    attempt = 0
    while attempt < retries:
        try:
            print(f"Fetching URL: {url}, Attempt: {attempt + 1}")
            response = session.get(url, timeout=10)
            response.raise_for_status()  # Raise an error for HTTP issues
            return response.text  # Return the HTML content
        except requests.exceptions.HTTPError as http_err:
            # Handle specific HTTP errors (e.g., 503 Service Unavailable)
            if response.status_code == 503:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Received 503. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                attempt += 1
            else:
                print(f"HTTP error occurred: {http_err}")
                break
        except requests.exceptions.RequestException as e:
            # Handle other request-related errors
            print(f"Request error occurred: {e}")
            break
    raise Exception("Failed after maximum retries")

@app.route('/scrape-ebay', methods=['GET'])
def scrape_ebay():
    """
    Scrapes eBay for beauty products and returns the data as JSON.

    Returns:
        JSON: A list of products with their details.
    """
    # Base URL for eBay search with specific query parameters
    base_url = "https://www.ebay.com/sch/i.html?_nkw=beauty+products&_sacat=0&_pgn="
    total_pages = 1 # Number of pages to scrape (for now, only 1 page)
    products = []  # List to store product data

    try:
        # Loop through the pages to scrape
        for page in range(1, total_pages + 1):
            url = f"{base_url}{page}"  # Construct the URL for the current page
            data = fetch_with_retry(url)  # Fetch the HTML content
            soup = BeautifulSoup(data, 'html.parser')  # Parse the HTML content

            # Extract product items from the page
            items = soup.select(".s-item")
            for item in items:
                # Extract product details
                name = item.select_one(".s-item__title").text.strip() if item.select_one(".s-item__title") else "Unnamed Product"
                price = item.select_one(".s-item__price").text.strip() if item.select_one(".s-item__price") else "Price not available"
                availability = item.select_one(".s-item__availability").text.strip() if item.select_one(".s-item__availability") else "Available at eBay"

                # Extract image URL
                image_element = item.select_one(".s-item__image-wrapper img")
                image_url = (
                    image_element.get("src") or
                    image_element.get("data-src") or
                    image_element.get("data-large-src") or
                    "https://via.placeholder.com/150"  # Fallback image
                )

                # Additional fields (mocked for now, replace with actual selectors)
                product_type = "Beauty Product"  # Replace with actual selector
                description = item.select_one(".s-item__subtitle").text.strip() if item.select_one(".s-item__subtitle") else "Product description is not available at the moment"  # Replace with actual selector
                rate = item.select_one(".s-item__seller-info").text.strip() if item.select_one(".s-item__seller-info") else "3.2 out of 5"  # Replace with actual selector
                production_year = "production year is not available at eBay store"  # Replace with actual selector
                store_availability = "Available at eBay"  # Replace with actual selector

                # Append the product details to the list
                products.append({
                    "name": name,
                    "price": price,
                    "availability": availability,
                    "type": product_type,
                    "description": description,
                    "rate": rate,
                    "production_year": production_year,
                    "store_availability": store_availability,
                    "image_url": image_url,  # Add image URL
                })
            # Add a delay between page requests to avoid overwhelming the server
            time.sleep(random.uniform(2, 5))
    except Exception as e:
        # Handle any exceptions and return an error message
        return jsonify({"error": str(e)}), 500

    # Log the product data and return it as JSON
    print(products)
    return jsonify(products)

# Run the Flask app if this file is executed directly
if __name__ == '__main__':
    app.run(debug=True)