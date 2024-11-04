"""
Redis Queries Module

This module provides functions to perform specific queries on a Redis database, such as finding the supplier with the most expensive product and listing products by a specific supplier.

Available Functions:
- find_supplier_with_most_expensive_product(): Returns the ID of the supplier with the most expensive product.
- list_products_by_supplier(supplier_id): Lists all products provided by a specific supplier.

Usage:
1. Ensure your terminal is pointed at the directory where redisQueries.py is located, or add the directory to your Python path.
2. Run the following commands in your Python environment:

Example Commands:
from redis_queries import find_supplier_with_most_expensive_product, list_products_by_supplier

# Find the supplier with the most expensive product and print the result.
print(find_supplier_with_most_expensive_product())

# List all products from a specific supplier (e.g., supplier ID '1') and print the results.
print(list_products_by_supplier('1'))

Ensure that Redis server is running and properly configured to connect through the specified host and port in this script.
"""


import redis
import sys

def list_products_by_supplier(supplier_id):
    r = redis.Redis(host='localhost', port=6379, db=0)
    all_product_keys = r.scan_iter("product:*")
    product_names = []
    for product_key in all_product_keys:
        product = r.hgetall(product_key)
        # Checking if this product belongs to the requested supplier
        if product.get(b'supplier_id', b'').decode('utf-8') == supplier_id:
            product_names.append(product[b'name'].decode('utf-8'))
    return product_names



def find_supplier_with_most_expensive_product():
    r = redis.Redis(host='localhost', port=6379, db=0)
    max_price = -1
    supplier_id_of_most_expensive_product = None
    for key in r.scan_iter("product:*"):
        product = r.hgetall(key)
        price_data = product.get(b'price', b'').decode('utf-8').strip()
        if price_data:
            try:
                price = float(price_data)
                if price > max_price:
                    max_price = price
                    supplier_id_of_most_expensive_product = product[b'supplier_id'].decode('utf-8')
            except ValueError:
                continue
    if supplier_id_of_most_expensive_product:
        return f"Supplier ID {supplier_id_of_most_expensive_product} sells the most expensive product at ${max_price:.2f}"
    else:
        return "No valid product prices found."

def main_menu():
    print("Select an option:")
    print("1. List products by supplier")
    print("2. Find supplier with the most expensive product")
    print("0. Exit")
    choice = input("Enter choice: ")
    return choice

if __name__ == "__main__":
    while True:
        user_choice = main_menu()
        if user_choice == "1":
            supplier_id = input("Enter supplier ID: ")
            products = list_products_by_supplier(supplier_id)
            print(f"Products by supplier {supplier_id}: {products}")
        elif user_choice == "2":
            result = find_supplier_with_most_expensive_product()
            print(result)
        elif user_choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")
