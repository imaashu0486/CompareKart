import json
import os

DATA_DIR = "data"
OUTPUT_FILE = "normalized_data.json"


def extract_base_product(name):
    return name.split("(")[0].strip()


def normalize_amazon(item):
    discount = int(item["cost"] * item["discount_percent"] / 100)
    return {
        "platform": "Amazon",
        "product_id": item["id"],
        "product_name": item["title"],
        "base_product": extract_base_product(item["title"]),
        "original_price": item["cost"],
        "discount": discount,
        "final_price": item["cost"] - discount,
        "availability": item["in_stock"]
    }


def normalize_flipkart(item):
    return {
        "platform": "Flipkart",
        "product_id": item["product_id"],
        "product_name": item["name"],
        "base_product": extract_base_product(item["name"]),
        "original_price": item["price"],
        "discount": item["offer"],
        "final_price": item["price"] - item["offer"],
        "availability": item["availability"] == "available"
    }


def normalize_myntra(item):
    return {
        "platform": "Myntra",
        "product_id": item["itemCode"],
        "product_name": item["productName"],
        "base_product": extract_base_product(item["productName"]),
        "original_price": item["mrp"],
        "discount": item["discount"],
        "final_price": item["mrp"] - item["discount"],
        "availability": item["stock"] == "yes"
    }


def normalize_ajio(item):
    return {
        "platform": "Ajio",
        "product_id": item["sku"],
        "product_name": item["label"],
        "base_product": extract_base_product(item["label"]),
        "original_price": item["selling_price"],
        "discount": 0,
        "final_price": item["selling_price"],
        "availability": item["availability_status"]
    }


def load_json(filename):
    with open(os.path.join(DATA_DIR, filename), "r") as f:
        return json.load(f)


def main():
    normalized = []

    for item in load_json("amazon_data.json"):
        normalized.append(normalize_amazon(item))

    for item in load_json("flipkart_data.json"):
        normalized.append(normalize_flipkart(item))

    for item in load_json("myntra_data.json"):
        normalized.append(normalize_myntra(item))

    for item in load_json("ajio_data.json"):
        normalized.append(normalize_ajio(item))

    with open(os.path.join(DATA_DIR, OUTPUT_FILE), "w") as f:
        json.dump(normalized, f, indent=2)

    print("✅ normalized_data.json generated successfully")


if __name__ == "__main__":
    main()
