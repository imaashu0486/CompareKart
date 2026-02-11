import json
import os

DATA_PATH = os.path.join("data", "normalized_data.json")


def load_normalized_data():
    """
    Loads normalized product data from JSON file
    """
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError("normalized_data.json not found")

    with open(DATA_PATH, "r") as file:
        return json.load(file)


def extract_base_product(product_name):
    """
    Converts:
    'iPhone 14 (128GB, Blue)' → 'iPhone 14'
    """
    return product_name.split("(")[0].strip()


def compare_prices(search_query):
    """
    Core comparison logic:
    - Match products
    - Filter available items
    - Sort by lowest final price
    """
    data = load_normalized_data()
    matched_products = []

    for item in data:
        base_name = extract_base_product(item["product_name"])

        if search_query.lower() in base_name.lower():
            if item["availability"]:
                matched_products.append(item)

    # Sort results by final price (ascending)
    matched_products.sort(key=lambda x: x["final_price"])

    return matched_products


def get_best_deal(search_query):
    """
    Returns the cheapest available product
    """
    results = compare_prices(search_query)

    if not results:
        return None

    return results[0]


if __name__ == "__main__":
    query = "iPhone 14"
    results = compare_prices(query)

    print(f"Price comparison results for '{query}':\n")
    for item in results:
        print(
            f"{item['platform']} | ₹{item['final_price']} | {item['product_name']}"
        )

    best = get_best_deal(query)
    if best:
        print("\nBest Deal:")
        print(f"{best['platform']} at ₹{best['final_price']}")
    else:
        print("No product found")
