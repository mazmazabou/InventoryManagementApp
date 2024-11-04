"""
Database Operations Module for MongoDB

This module defines functions to interact with MongoDB for an Inventory Management System. It encapsulates all CRUD operations for various entities such as inventory, orders, retailers, and order details. It also includes functions to retrieve all records from the database.

Functions:
- create_inventory: Adds a new inventory record.
- create_retailer: Adds a new retailer record.
- create_order: Adds a new order record.
- create_order_detail: Adds a new order detail record linked to an order and product.
- retrieve_inventory: Retrieves a specific inventory record.
- retrieve_order: Retrieves a specific order record.
- retrieve_retailer: Retrieves a specific retailer record.
- retrieve_order_detail: Retrieves specific order detail records.
- update_order: Updates an existing order record.
- update_retailer: Updates an existing retailer record.
- update_order_detail: Updates an existing order detail record.
- update_inventory_quantity: Updates the quantity of an existing inventory record.
- delete_inventory: Deletes an inventory record.
- delete_order: Deletes an order record.
- delete_retailer: Deletes a retailer record.
- delete_order_detail: Deletes an order detail record.
- get_all_inventory: Retrieves all inventory records.
- get_all_orders: Retrieves all order records.
- get_all_retailers: Retrieves all retailer records.
- get_all_order_details: Retrieves all order detail records.

Usage:
These functions are used within the Inventory Management GUI or can be utilized in automated scripts for batch processing or maintenance.

Dependencies:
- mongoengine: ORM library for working with MongoDB from Python.
"""

from mongoengine import DoesNotExist 
from models import Retailer, Order, Inventory, OrderDetails, Product
from redis_db import check_product_exists_in_redis
from datetime import datetime
import redis

r = redis.Redis(host='localhost', port=6379, db=0)


def get_all_inventory():
    return [(inv.inventory_id, inv.product_id, inv.quantity, inv.location) for inv in Inventory.objects]


def get_all_orders():
    return [(ord.order_id, ord.retailer.retailer_id, ord.order_date.strftime("%Y-%m-%d")) for ord in Order.objects]


def get_all_retailers():
    return [(ret.retailer_id, ret.name, ret.location, ret.contact_info) for ret in Retailer.objects]

def get_all_order_details():
    order_details_list = []
    for od in OrderDetails.objects:
        try:
            # Make sure to check if the order reference exists before dereferencing
            if od.order:
                order = Order.objects.with_id(od.order.id)  # A safer way to fetch by ID
                order_id = order.order_id if order else 'Unknown'
            else:
                order_id = 'Unknown'
        except DoesNotExist as e:
            print(f"Failed to fetch order: {str(e)}")
            order_id = 'Unknown'  # Ensures the loop continues even if an order doesn't exist
        product_id = od.product_id if od.product_id else 'Unknown'
        quantity = od.quantity
        order_details_list.append((order_id, product_id, quantity))
    return order_details_list



# INVENTORY #
def create_inventory(inventory_id, product_id, quantity, warehouse_location):
    # Check if the product exists in Redis
    if check_product_exists_in_redis(product_id):  # true
        # Product found in Redis, proceed with adding the inventory in MongoDB
        try:
            new_inventory = Inventory(
                inventory_id=inventory_id,
                product_id=product_id,
                quantity=quantity,
                location=warehouse_location
            )
            new_inventory.save()
            return True, f"Inventory item {inventory_id} created with product {product_id}."
        except Exception as e:
            return False, f"Failed to create inventory: {str(e)}"
    else:
        return False, "Unable to locate the product in the database. Please add the product entry first by using the " \
                      "Create Product option."


# ORDER #
def create_order(order_id, retailer_id):
    try:
        order_date = datetime.now()
        retailer = Retailer.objects(retailer_id=retailer_id).first()
        if not retailer:
            return False, "Retailer does not exist."
        new_order = Order(order_id=order_id, retailer=retailer, order_date=order_date)
        new_order.save()
        return True, f"Order {order_id} created successfully."
    except Exception as e:
        return False, f"Failed to create order: {e}"


# ORDER_DETAILS #
def create_order_detail(order_id, product_id, quantity):
    try:
        # Convert quantity to an integer
        quantity = int(quantity)
    except ValueError:
        return False, "Quantity must be an integer."

    # Check if the order exists
    order = Order.objects(order_id=order_id).first()
    if not order:
        return False, "Order does not exist."

    # Check if the product exists in the inventory and if sufficient quantity is available
    inventory_item = Inventory.objects(product_id=product_id).first()
    if not inventory_item or inventory_item.quantity < quantity:
        return False, "Not enough inventory or product does not exist."

    # If sufficient inventory is available, reduce the inventory and create the order detail
    try:
        inventory_item.update(dec__quantity=quantity)
        order_detail = OrderDetails(order=order, product_id=product_id, quantity=quantity)
        order_detail.save()
        return True, "Order detail added successfully."
    except Exception as e:
        # Roll back the inventory deduction if order detail save fails
        inventory_item.update(inc__quantity=quantity)
        return False, f"Failed to create order detail: {e}"


# RETAILER #
def create_retailer(retailer_id, name, location, contact_info):
    try:
        new_retailer = Retailer(
            retailer_id=retailer_id,
            name=name,
            location=location,
            contact_info=contact_info
        )
        new_retailer.save()
        return True, f"Retailer {name} created successfully."
    except Exception as e:
        return False, f"Failed to create retailer: {e}"


# RETRIEVE #

# INVENTORY #
def retrieve_inventory(inventory_id):
    inventory = Inventory.objects(inventory_id=inventory_id).first()
    if inventory:
        inventory_data = {
            'Inventory ID': inventory.inventory_id,
            'Product ID': inventory.product_id,
            'Quantity': inventory.quantity,
            'Location': inventory.location
        }
        return True, inventory_data
    else:
        return False, "Inventory item not found."


# ORDER #
def retrieve_order(order_id):
    order = Order.objects(order_id=order_id).first()
    if order:
        order_data = {
            'Order ID': order.order_id,
            'Retailer ID': order.retailer.retailer_id,
            'Order Date': order.order_date.strftime("%Y-%m-%d")
        }
        return True, order_data
    else:
        return False, "Order not found."


# ORDER_DETAILS #
def retrieve_order_detail(order_id, product_id):
    order_detail = OrderDetails.objects(order=order_id, product_id=product_id).first()
    if order_detail:
        order_detail_data = {
            'Order ID': order_detail.order.order_id,
            'Product ID': order_detail.product_id,
            'Quantity': order_detail.quantity
        }
        return True, order_detail_data
    else:
        return False, "Order detail not found."


# RETAILER #
def retrieve_retailer(retailer_id):
    retailer = Retailer.objects(retailer_id=retailer_id).first()
    if retailer:
        retailer_data = {
            'Retailer ID': retailer.retailer_id,
            'Name': retailer.name,
            'Location': retailer.location,
            'Contact Info': retailer.contact_info
        }
        return True, retailer_data
    else:
        return False, "Retailer not found."


# UPDATE #

# INVENTORY #
def update_inventory_quantity(inventory_id, new_quantity):
    inventory = Inventory.objects(inventory_id=inventory_id).first()
    if inventory:
        inventory.quantity = new_quantity
        inventory.save()
        return True, f"Inventory item {inventory_id} updated successfully."
    else:
        return False, "Inventory item not found."


# ORDER #
def update_order(order_id, new_retailer_id=None):
    order = Order.objects(order_id=order_id).first()
    if not order:
        return False, "Order not found."
    # Update the retailer if a new retailer ID is provided
    if new_retailer_id:
        new_retailer = Retailer.objects(retailer_id=new_retailer_id).first()
        if new_retailer:
            order.retailer = new_retailer
        else:
            return False, "New retailer not found. Order's retailer not updated."

    order.save()
    return True, f"Order {order_id} updated."


# ORDER_DETAILS #
# ORDER_DETAILS #
def update_order_detail(order_id, product_id, new_quantity):
    try:
        new_quantity = int(new_quantity)  # Ensure new_quantity is an integer
    except ValueError:
        return False, "Quantity must be an integer."

    order_detail = OrderDetails.objects(order=order_id, product_id=product_id).first()
    if not order_detail:
        return False, "Order detail not found."

    inventory_item = Inventory.objects(product_id=product_id).first()
    if not inventory_item:
        return False, "Inventory item not found."

    # Calculate the difference
    quantity_difference = new_quantity - order_detail.quantity

    if quantity_difference > 0 and quantity_difference > inventory_item.quantity:
        # If we need more items than available in inventory
        return False, "Insufficient inventory to fulfill the updated quantity."

    try:
        # Update the inventory
        inventory_item.modify(inc__quantity=-quantity_difference)
        # Update the order detail
        order_detail.modify(set__quantity=new_quantity)
        return True, "Order detail and inventory updated successfully."
    except Exception as e:
        return False, f"Failed to update order detail: {e}"


# RETAILER #
def update_retailer(retailer_id, new_name=None, new_location=None, new_contact_info=None):
    retailer = Retailer.objects(retailer_id=retailer_id).first()
    if retailer:
        updates = {}
        if new_name is not None:
            updates['name'] = new_name
        if new_location is not None:
            updates['location'] = new_location
        if new_contact_info is not None:
            updates['contact_info'] = new_contact_info
        if updates:
            Retailer.objects(id=retailer.id).update(**updates)
            return True, f"Retailer {retailer_id} updated successfully."
        else:
            return False, "No updates provided."
    else:
        return False, "Retailer not found."


# DELETE #

# INVENTORY #
def delete_inventory(inventory_id):
    inventory = Inventory.objects(inventory_id=inventory_id).first()
    if inventory:
        inventory.delete()
        return True, f"Inventory item {inventory_id} deleted successfully."
    else:
        return False, "Inventory item not found."


# ORDER #
def delete_order(order_id):
    order = Order.objects(order_id=order_id).first()
    if order:
        order.delete()
        return True, f"Order {order_id} deleted successfully."
    else:
        return False, "Order not found."


# ORDER_DETAILS #
def delete_order_detail(order_id, product_id):
    order_detail = OrderDetails.objects(order=order_id, product_id=product_id).first()
    if not order_detail:
        return False, "Order detail not found."

    inventory_item = Inventory.objects(product_id=product_id).first()
    if not inventory_item:
        return False, "Inventory item not found for this product."

    try:
        # Add back the order detail quantity to the inventory
        inventory_item.update(inc__quantity=order_detail.quantity)
        order_detail.delete()
        return True, f"Order detail deleted successfully and inventory updated."
    except Exception as e:
        return False, f"Failed to delete order detail: {e}"



# RETAILER #
def delete_retailer(retailer_id):
    retailer = Retailer.objects(retailer_id=retailer_id).first()
    if retailer:
        retailer.delete()
        return True, f"Retailer {retailer_id} deleted successfully."
    else:
        return False, "Retailer not found."
