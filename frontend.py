import requests
from tkinter import Tk, Label, Button, Canvas, Frame, Scrollbar, Entry, StringVar, PhotoImage, Scale  # Import Scale
from PIL import Image, ImageTk  # Import Pillow for image handling
import json

# API URL to fetch product data from the backend
API_URL = "http://127.0.0.1:5000/scrape-ebay"

def fetch_products():
    """
    Fetches product data from the backend API.

    Returns:
        list: A list of products as dictionaries.
    """
    response = requests.get(API_URL)
    if response.status_code == 200:
        print("Fetched Products:", response.json())  # Debugging
        return response.json()
    else:
        print("Failed to fetch products:", response.status_code)  # Debugging
        return []

def load_ratings():
    """
    Loads product ratings from a JSON file.

    Returns:
        dict: A dictionary of product ratings.
    """
    try:
        with open('ratings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_rating(product_name, rating):
    """
    Saves a product rating to a JSON file.

    Args:
        product_name (str): The name of the product.
        rating (int): The rating to save.
    """
    ratings = load_ratings()
    ratings[product_name] = rating
    with open('ratings.json', 'w') as f:
        json.dump(ratings, f)

def filter_products(products, search_query=None):
    """
    Filters products based on ratings and a search query.

    Args:
        products (list): A list of product dictionaries.
        search_query (str): A search term to filter products by name.

    Returns:
        list: A filtered list of products.
    """
    ratings = load_ratings()
    filtered = [product for product in products if ratings.get(product['name'], 5) >= 3]
    if search_query:
        filtered = [product for product in filtered if search_query.lower() in product['name'].lower()]
    print("Filtered Products:", filtered)  # Debugging
    return filtered

def display_products(products, canvas, frame, search_query=None):
    """
    Displays products in a scrollable frame.

    Args:
        products (list): A list of product dictionaries.
        canvas (Canvas): The canvas to display the products on.
        frame (Frame): The frame inside the canvas to hold product widgets.
        search_query (str): A search term to filter products by name.
    """
    for widget in frame.winfo_children():
        widget.destroy()

    filtered_products = filter_products(products, search_query)

    # Alternating background colors for product frames
    colors = ["#f0f8ff", "#f0fff0"]  # Light blue and light green

    for index, product in enumerate(filtered_products):
        bg_color = colors[index % len(colors)]  # Alternate between colors
        product_frame = Frame(frame, bg=bg_color, padx=10, pady=10, bd=2, relief="groove")
        product_frame.pack(fill='x', pady=5, padx=10, expand=True)

        # Product Image
        try:
            # Download the image from the URL
            image_response = requests.get(product['image_url'], stream=True)
            image_response.raise_for_status()

            # Open the image with Pillow
            image = Image.open(image_response.raw)

            # Resize the image to a reasonable size (e.g., 150x150)
            image = image.resize((150, 150), Image.Resampling.LANCZOS)  # Use Image.Resampling.LANCZOS

            # Convert the image to a Tkinter-compatible format
            tk_image = ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading image: {e}")
            # Fallback image (use a local placeholder image)
            try:
                image = Image.open("placeholder.jpg")  # Use placeholder.jpg
                image = image.resize((150, 150), Image.Resampling.LANCZOS)  # Use Image.Resampling.LANCZOS
                tk_image = ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Error loading fallback image: {e}")
                continue  # Skip this product if the fallback image also fails

        # Display the image
        image_label = Label(product_frame, image=tk_image, bg=bg_color)
        image_label.image = tk_image  # Keep a reference to avoid garbage collection
        image_label.grid(row=0, column=0, rowspan=7, padx=10)

        # Product Details
        Label(product_frame, text=f"Name: {product['name']}", font=("Arial", 12, "bold"), bg=bg_color, fg="#333333").grid(row=0, column=1, sticky='w')
        Label(product_frame, text=f"Price: {product['price']}", font=("Arial", 11), bg=bg_color, fg="#555555").grid(row=1, column=1, sticky='w')
        Label(product_frame, text=f"Type: {product['type']}", font=("Arial", 11), bg=bg_color, fg="#555555").grid(row=2, column=1, sticky='w')
        Label(product_frame, text=f"Description: {product['description']}", font=("Arial", 11), bg=bg_color, fg="#555555").grid(row=3, column=1, sticky='w')
        Label(product_frame, text=f"Rate: {product['rate']}", font=("Arial", 11), bg=bg_color, fg="#555555").grid(row=4, column=1, sticky='w')
        Label(product_frame, text=f"Production Year: {product['production_year']}", font=("Arial", 11), bg=bg_color, fg="#555555").grid(row=5, column=1, sticky='w')
        Label(product_frame, text=f"Store Availability: {product['store_availability']}", font=("Arial", 11), bg=bg_color, fg="#555555").grid(row=6, column=1, sticky='w')

        # Rating Widget
        rating_scale = Scale(product_frame, from_=1, to=5, orient='horizontal', command=lambda rating, p=product['name']: save_rating(p, int(rating)), bg=bg_color)
        rating_scale.set(load_ratings().get(product['name'], 5))
        rating_scale.grid(row=7, column=1, pady=5)

def refresh_data(canvas, frame, search_query=None):
    """
    Refreshes the product data and displays it.

    Args:
        canvas (Canvas): The canvas to display the products on.
        frame (Frame): The frame inside the canvas to hold product widgets.
        search_query (str): A search term to filter products by name.
    """
    products = fetch_products()
    display_products(products, canvas, frame, search_query)

def search_products(canvas, frame, search_var):
    """
    Searches for products based on a search query.

    Args:
        canvas (Canvas): The canvas to display the products on.
        frame (Frame): The frame inside the canvas to hold product widgets.
        search_var (StringVar): The search query variable.
    """
    search_query = search_var.get()
    refresh_data(canvas, frame, search_query)

def main():
    """
    The main function to initialize the Tkinter application.
    """
    root = Tk()
    root.title("eBay Product Viewer")
    root.geometry("800x600")
    root.configure(bg="#f0f0f0")

    # Header Frame
    header_frame = Frame(root, bg="#4CAF50", padx=10, pady=10)
    header_frame.pack(fill='x')

    Label(header_frame, text="Beauty Finest", font=("Arial", 16, "bold"), fg="white", bg="#4CAF50").pack(side='left')

    # Search Bar
    search_var = StringVar()
    search_entry = Entry(header_frame, textvariable=search_var, font=("Arial", 12), width=30)
    search_entry.pack(side='left', padx=10)

    search_btn = Button(header_frame, text="Search", command=lambda: search_products(canvas, scrollable_frame, search_var), bg="#388E3C", fg="black", font=("Arial", 12))
    search_btn.pack(side='left')

    # Main Content
    canvas = Canvas(root, bg="#f0f0f0")
    scrollbar = Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas, bg="#f0f0f0")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Refresh Button
    refresh_btn = Button(root, text="Refresh Products", command=lambda: refresh_data(canvas, scrollable_frame), bg="#4CAF50", fg="black", font=("Arial", 12))
    refresh_btn.pack(pady=10)

    # Initial data load
    refresh_data(canvas, scrollable_frame)

    root.mainloop()

if __name__ == "__main__":
    main()