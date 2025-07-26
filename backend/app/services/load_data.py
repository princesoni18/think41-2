import os
import pandas as pd
from app.services.database import db

CSV_FOLDER = os.path.join(os.path.dirname(__file__), '../../dataset/archive')

CSV_COLLECTION_MAP = {
    'distribution_centers.csv': 'distribution_centers',
    'inventory_items.csv': 'inventory_items',
    'order_items.csv': 'order_items',
    'orders.csv': 'orders',
    'products.csv': 'products',
    'users.csv': 'users',
}

def load_csv_to_mongo():
    for csv_file, collection_name in CSV_COLLECTION_MAP.items():
        file_path = os.path.abspath(os.path.join(CSV_FOLDER, csv_file))
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            records = df.to_dict(orient='records')
            if records:
                db[collection_name].delete_many({})  # Clear existing data
                db[collection_name].insert_many(records)
                print(f"Loaded {len(records)} records into '{collection_name}' collection.")
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    load_csv_to_mongo()
