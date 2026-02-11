import json
import random
import os

TOTAL_PRODUCTS = 30

BASE_PRODUCTS = [
    "iPhone 14",
    "Samsung Galaxy S23",
    "OnePlus 11",
    "Redmi Note 13",
    "Realme GT Neo",
    "Google Pixel 7"
]

STORAGE = ["128GB", "256GB"]
COLORS = ["Black", "Blue", "Green", "White"]
SUFFIX = ["5G", "Smartphone", "Model 2023", ""]

DATA_DIR = "data"


def generate_title(base):
    return f"{base} ({random.choice(STORAGE)}, {random.choice(COLORS)}) {random.choice(SUFFIX)}".strip()


def generate_amazon():
    return [
        {
            "id": f"A{i+100}",
            "title": generate_title(random.choice(BASE_PRODUCTS)),
            "cost": random.randint(45000, 90000),
            "discount_percent": random.randint(5, 18),
            "in_stock": random.choice([True, True, False])
        }
        for i in range(TOTAL_PRODUCTS)
    ]


def generate_flipkart():
    return [
        {
            "product_id": f"F{i+200}",
            "name": generate_title(random.choice(BASE_PRODUCTS)),
            "price": random.randint(43000, 88000),
            "offer": random.randint(3000, 12000),
            "availability": random.choice(["available", "unavailable"])
        }
        for i in range(TOTAL_PRODUCTS)
    ]


def generate_myntra():
    return [
        {
            "itemCode": f"M{i+300}",
            "productName": generate_title(random.choice(BASE_PRODUCTS)),
            "mrp": random.randint(46000, 92000),
            "discount": random.randint(4000, 15000),
            "stock": random.choice(["yes", "no"])
        }
        for i in range(TOTAL_PRODUCTS)
    ]


def generate_ajio():
    return [
        {
            "sku": f"J{i+400}",
            "label": generate_title(random.choice(BASE_PRODUCTS)),
            "selling_price": random.randint(44000, 89000),
            "availability_status": random.choice([True, False])
        }
        for i in range(TOTAL_PRODUCTS)
    ]


def save_json(filename, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, filename), "w") as f:
        json.dump(data, f, indent=2)


def main():
    save_json("amazon_data.json", generate_amazon())
    save_json("flipkart_data.json", generate_flipkart())
    save_json("myntra_data.json", generate_myntra())
    save_json("ajio_data.json", generate_ajio())

    print(f"✅ Generated {TOTAL_PRODUCTS} synthetic products per platform")


if __name__ == "__main__":
    main()
