"""
Redis Operations Module

This module defines functions to interact with Redis for an Inventory Management System, specifically managing product and supplier data. 
It encapsulates all CRUD operations for products and suppliers, including functions to retrieve all records from Redis.

Functions:
- create_product: Adds a new product record in Redis.
- create_supplier: Adds a new supplier record in Redis.
- retrieve_product: Retrieves a specific product record from Redis.
- retrieve_supplier: Retrieves a specific supplier record from Redis.
- update_supplier: Updates an existing supplier record in Redis.
- update_product: Updates an existing product record in Redis.
- delete_supplier: Deletes a supplier record from Redis.
- delete_product: Deletes a product record from Redis.
- get_all_products: Retrieves all product records from Redis.
- get_all_suppliers: Retrieves all supplier records from Redis.

Usage:
These functions are designed to be used within an Inventory Management GUI or in other parts of the system that require interaction with Redis for product and supplier data management.

Dependencies:
- redis-py: Redis Python Client that provides simple access to Redis functionalities in Python.
"""


import redis

r = redis.Redis(host='localhost', port=6379, db=0)


def get_all_products():
    product_keys = r.keys("product:*")
    all_products = []
    for key in product_keys:
        product = r.hgetall(key)
        # Assuming the product has 'name', 'description', 'price', 'supplier_id'
        product_details = {
            'product_id': key.decode('utf-8').split(":")[1],
            'name': product[b'name'].decode('utf-8'),
            'description': product[b'description'].decode('utf-8'),
            'price': product[b'price'].decode('utf-8'),
            'supplier_id': product[b'supplier_id'].decode('utf-8')
        }
        all_products.append(product_details)
    return all_products


def get_all_suppliers():
    supplier_keys = r.keys("supplier:*")
    all_suppliers = []
    for key in supplier_keys:
        supplier = r.hgetall(key)
        # Assuming the supplier has 'name', 'location', 'contact_info'
        supplier_details = {
            'supplier_id': key.decode('utf-8').split(":")[1],
            'name': supplier[b'name'].decode('utf-8'),
            'location': supplier[b'location'].decode('utf-8'),
            'contact_info': supplier[b'contact_info'].decode('utf-8')
        }
        all_suppliers.append(supplier_details)
    return all_suppliers


# SUPPLIER #
def create_supplier(supplier_id, name, location, contact_info):
    key = f'supplier:{supplier_id}'
    if r.exists(key):
        return False, "Supplier already exists."
    else:
        r.hmset(key, {
            'name': name,
            'location': location,
            'contact_info': contact_info
        })
        return True, "Supplier added to Redis."


# PRODUCT #
def create_product(product_id, name, description, price, supplier_id):
    if not r.exists(f'supplier:{supplier_id}'):
        return False, "Supplier does not exist. Add the supplier first."

    key = f'product:{product_id}'
    if r.exists(key):
        return False, "Product already exists."
    else:
        r.hmset(key, {
            'name': name,
            'description': description,
            'price': price,
            'supplier_id': supplier_id
        })
        return True, "Product added to Redis."


def check_product_exists_in_redis(product_id):
    return r.exists(f"product:{product_id}")


def retrieve_supplier(supplier_id):
    key = f'supplier:{supplier_id}'
    if r.exists(key):
        supplier = r.hgetall(key)
        supplier_details = {k.decode('utf-8'): v.decode('utf-8') for k, v in supplier.items()}
        return True, supplier_details
    else:
        return False, "Supplier not found."


def retrieve_product(product_id):
    key = f'product:{product_id}'
    if r.exists(key):
        product = r.hgetall(key)
        product_details = {k.decode('utf-8'): v.decode('utf-8') for k, v in product.items()}
        return True, product_details
    else:
        return False, "Product not found."


def update_supplier(supplier_id, **kwargs):
    key = f'supplier:{supplier_id}'
    if not r.exists(key):
        return False, "Supplier not found."

    updates = {k: v for k, v in kwargs.items() if v is not None}
    if updates:
        r.hmset(key, updates)
        return True, "Supplier updated successfully."
    else:
        return False, "No updates provided."


def update_product(product_id, **kwargs):
    key = f'product:{product_id}'
    if not r.exists(key):
        return False, "Product not found."

    updates = {k: v for k, v in kwargs.items() if v is not None}
    if updates:
        r.hmset(key, updates)
        return True, "Product updated successfully."
    else:
        return False, "No updates provided."


def delete_supplier(supplier_id):
    key = f'supplier:{supplier_id}'
    if r.delete(key):
        return True, f"Supplier {supplier_id} deleted successfully."
    else:
        return False, f"Supplier {supplier_id} not found or already deleted."


def delete_product(product_id):
    key = f'product:{product_id}'
    if r.delete(key):
        return True, f"Product {product_id} deleted successfully."
    else:
        return False, f"Product {product_id} not found or already deleted."
