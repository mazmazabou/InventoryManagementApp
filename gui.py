"""
Inventory Management GUI Module

This module defines the graphical user interface for an Inventory Management System using tkinter and customtkinter libraries.
It provides a user-friendly environment to perform CRUD operations on inventory, orders, products, suppliers, and retailers.

Classes:
- InventoryManagementGUI: Main class that sets up the GUI, including dropdowns, buttons, and dynamic input fields for interacting with the inventory management system.

Functions within InventoryManagementGUI:
- __init__(self, root): Initializes the main window and its components.
- on_action_selected(self, event=None): Handles the selection of actions from the dropdown menu.
- get_display_function(self, entity): Retrieves the appropriate display function based on the entity selected.
- confirm_selection(self): Confirms the selected action and entity, and prepares the input fields accordingly.
- generate_input_fields(self): Dynamically generates input fields based on the selected action and entity.
- submit(self): Processes the input and performs the selected action on the entity.
- create_display_window(self, title, columns): Creates a new window for displaying all entities in a tabular format.
- show_all_inventory(self): Displays all inventory records.
- show_all_orders(self): Displays all order records.
- show_all_order_details(self): Displays all order detail records.
- show_all_retailers(self): Displays all retailer records.
- show_all_suppliers(self): Displays all supplier records.
- show_all_products(self): Displays all product records.

Usage:
Run this script directly to launch the Inventory Management GUI. 
Ensure that the necessary backend services (MongoDB and Redis) are running and properly configured to interact through the provided imports from db.py and redis_db.py.

Example:
python3 gui.py

Dependencies:
- tkinter and customtkinter for the GUI components.
- db.py and redis_db.py for interacting with MongoDB and Redis respectively.

Ensure that tkinter is updated to work with customtkinter if using Python versions earlier than 3.7.
"""


import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk

from db import create_inventory, create_retailer, create_order, create_order_detail, retrieve_inventory, \
    retrieve_order, retrieve_retailer, retrieve_order_detail, update_order, update_retailer, update_order_detail, \
    update_inventory_quantity, delete_inventory, delete_order, delete_retailer, delete_order_detail, get_all_inventory, \
    get_all_orders, get_all_retailers, get_all_order_details

from redis_db import create_product, create_supplier, retrieve_product, \
    retrieve_supplier, update_supplier, update_product, delete_supplier, delete_product, get_all_products, \
    get_all_suppliers

# Set the appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class InventoryManagementGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("800x600")

        # Define actions and entities
        self.actions = ["Create", "Retrieve", "Update", "Delete", "Display All"]
        self.entities = ["Inventory", "Order", "Order Detail", "Retailer", "Product", "Supplier"]

        # Action Dropdown
        self.action_var = ctk.StringVar(value="Select Action")
        self.action_dropdown = ctk.CTkComboBox(self.root, values=self.actions, variable=self.action_var
                                               , command=self.on_action_selected)
        self.action_dropdown.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.action_dropdown.bind("<<ComboboxSelected>>", self.on_action_selected)

        # Entity Dropdown
        self.entity_var = ctk.StringVar(value="Select Entity")
        self.entity_dropdown = ctk.CTkComboBox(self.root, values=self.entities, variable=self.entity_var)
        self.entity_dropdown.grid(row=0, column=2, padx=10, pady=10, sticky="e")

        # Dynamic Frame for Input Fields
        self.dynamic_frame = ctk.CTkFrame(self.root)
        self.dynamic_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

        # Information Label
        self.info_label = ctk.CTkLabel(self.root,
                                       text="Make selections and then press 'Confirm' to generate fields.",
                                       width=100)
        self.info_label.grid(row=0, column=0, columnspan=3, padx=10)

        # Confirm Button
        self.confirm_button = ctk.CTkButton(self.root, text="Confirm", command=self.generate_input_fields, width=20)
        self.confirm_button.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        # Submit Button
        self.submit_button = ctk.CTkButton(self.root, text="Submit", command=self.submit)
        self.submit_button.grid(row=4, column=2, padx=10, pady=10, sticky="e")

        # Exit Button
        self.exit_button = ctk.CTkButton(self.root, text="<Exit", command=root.quit)
        self.exit_button.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        # Grid configuration for resizing
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def on_action_selected(self, event=None):
        action = self.action_var.get()
        if action == "Display All":
            entity = self.entity_var.get()
            if entity != "Select Entity":  # Assuming 'Select Entity' is the default option in entity dropdown
                # Call the corresponding 'show_all_*' function directly
                display_function = self.get_display_function(entity)
                if display_function:
                    display_function()
                else:
                    messagebox.showerror("Error", f"No display function available for {entity}.")

    def get_display_function(self, entity):
        display_functions = {
            'Inventory': self.show_all_inventory,
            'Order': self.show_all_orders,
            'Order Detail': self.show_all_order_details,
            'Retailer': self.show_all_retailers,
            'Product': self.show_all_products,
            'Supplier': self.show_all_suppliers,
        }
        return display_functions.get(entity)

    def confirm_selection(self):
        action = self.action_var.get()
        entity = self.entity_var.get()
        if action == "Select Action" or entity == "Select Entity":
            messagebox.showinfo("Alert", "Please select both an action and an entity.")
        else:
            self.generate_input_fields()

    def generate_input_fields(self):
        # Clear the previous input fields first
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()

        # Get the selected action and entity
        action = self.action_var.get()
        entity = self.entity_var.get()

        # Define input requirements based on action and entity
        input_requirements = {
            'Create': {
                # For creating Inventory, the user must enter an Inventory ID, Product ID, Quantity, and Location
                'Inventory': [('Inventory ID', 'entry'), ('Product ID', 'entry'), ('Quantity', 'entry'),
                              ('Warehouse Location', 'entry')],
                'Order': [('Order ID', 'entry'), ('Retailer ID', 'entry')],
                'Product': [('Product ID', 'entry'), ('Name', 'entry'), ('Description', 'entry'), ('Price', 'entry'),
                            ('Supplier ID', 'entry')],
                'Retailer': [('Retailer ID', 'entry'), ('Name', 'entry'), ('Location', 'entry'),
                             ('Contact Info', 'entry')],
                'Supplier': [('Supplier ID', 'entry'), ('Name', 'entry'), ('Location', 'entry'),
                             ('Contact Info', 'entry')],
                'Order Detail': [('Order ID', 'entry'), ('Product ID', 'entry'), ('Quantity', 'entry')]
            },
            'Retrieve': {
                # For retrieving Inventory, the user only needs to enter the Inventory ID
                'Inventory': [('Inventory ID', 'entry')],
                'Order': [('Order ID', 'entry')],
                'Product': [('Product ID', 'entry')],
                'Retailer': [('Retailer ID', 'entry')],
                'Supplier': [('Supplier ID', 'entry')],
                'Order Detail': [('Order ID', 'entry'), ('Product ID', 'entry')]
            },
            'Update': {
                # For updating, similar fields as create but might only require IDs and new values for specific fields
                'Inventory': [('Inventory ID', 'entry'), ('New Quantity', 'entry')],
                'Order': [('Order ID', 'entry'), ('New Retailer ID', 'entry')],
                'Product': [('Product ID', 'entry'), ('New Price', 'entry')],
                'Retailer': [('Retailer ID', 'entry'), ('New Location', 'entry'), ('New Contact Info', 'entry')],
                'Supplier': [('Supplier ID', 'entry'), ('New Name', 'entry'), ('New Location', 'entry'),
                             ('New Contact Info', 'entry')],
                'Order Detail': [('Order ID', 'entry'), ('Product ID', 'entry'), ('New Quantity', 'entry')]
            },
            'Delete': {
                # For deleting, generally only the ID is required
                'Inventory': [('Inventory ID', 'entry')],
                'Order': [('Order ID', 'entry')],
                'Product': [('Product ID', 'entry')],
                'Retailer': [('Retailer ID', 'entry')],
                'Supplier': [('Supplier ID', 'entry')],
                'Order Detail': [('Order ID', 'entry'), ('Product ID', 'entry')]
            }
        }

        fields = input_requirements.get(action, {}).get(entity, [])

        # Create input widgets dynamically based on required fields
        for idx, (field_name, field_type) in enumerate(fields):
            label = ctk.CTkLabel(self.dynamic_frame, text=field_name)
            label.grid(row=idx, column=0, padx=10, pady=5, sticky="w")
            if field_type == 'entry':
                entry = ctk.CTkEntry(self.dynamic_frame)
                entry.grid(row=idx, column=1, padx=10, pady=5, sticky="ew")

        # Automatically update the frame layout
        self.dynamic_frame.grid()
   
    def submit(self):
        # Define integer fields here
        integer_fields = {'quantity', 'price'}  # Adjust this set according to your application's needs

        action = self.action_var.get()
        entity = self.entity_var.get()

        inputs = {}
        for widget in self.dynamic_frame.winfo_children():
            if isinstance(widget, ctk.CTkEntry):
                label = self.dynamic_frame.grid_slaves(row=widget.grid_info()['row'], column=0)[0]
                field_name = label.cget('text').replace(' ', '_').lower()
                input_value = widget.get()

                if field_name in integer_fields:
                    try:
                        input_value = int(input_value)
                    except ValueError:
                        messagebox.showerror("Error", f"Invalid input for {field_name}, must be an integer.")
                        return  # Exit the function as we have invalid input

                inputs[field_name] = input_value


        if action == "Display All":
            display_function = self.get_display_function(entity)
            if display_function:
                display_function()  # This will retrieve and display all records for the entity
            else:
                messagebox.showerror("Error", "Display function not found for this entity.")
        else:
            # Map actions and entities to functions
            function_map = {
                ('Create', 'Inventory'): create_inventory,
                ('Create', 'Retailer'): create_retailer,
                ('Create', 'Order'): create_order,
                ('Create', 'Order Detail'): create_order_detail,
                ('Create', 'Product'): create_product,
                ('Create', 'Supplier'): create_supplier,

                ('Retrieve', 'Inventory'): retrieve_inventory,
                ('Retrieve', 'Order'): retrieve_order,
                ('Retrieve', 'Retailer'): retrieve_retailer,
                ('Retrieve', 'Order Detail'): retrieve_order_detail,
                ('Retrieve', 'Product'): retrieve_product,
                ('Retrieve', 'Supplier'): retrieve_supplier,

                ('Update', 'Order'): update_order,
                ('Update', 'Retailer'): update_retailer,
                ('Update', 'Order Detail'): update_order_detail,
                ('Update', 'Inventory'): update_inventory_quantity,
                ('Update', 'Product'): update_product,
                ('Update', 'Supplier'): update_supplier,

                ('Delete', 'Inventory'): delete_inventory,
                ('Delete', 'Order'): delete_order,
                ('Delete', 'Retailer'): delete_retailer,
                ('Delete', 'Order Detail'): delete_order_detail,
                ('Delete', 'Product'): delete_product,
                ('Delete', 'Supplier'): delete_supplier,

                ('Display All', 'Inventory'): get_all_inventory,
                ('Display All', 'Order'): get_all_orders,
                ('Display All', 'Retailer'): get_all_retailers,
                ('Display All', 'Order Detail'): get_all_order_details,
                ('Display All', 'Product'): get_all_products,
                ('Display All', 'Supplier'): get_all_suppliers
            }

            # Attempt to call the corresponding function
            try:
                # Fetch the appropriate function from the map using action and entity
                func = function_map.get((action, entity))
                if func:
                    success, message = func(**inputs)
                    if success:
                        messagebox.showinfo("Success", message)
                    else:
                        messagebox.showerror("Error", message)
                else:
                    messagebox.showerror("Error", "Unsupported action or entity selected.")
            except Exception as e:
                messagebox.showerror("Exception", f"An error occurred: {str(e)}")

    # Show All helper function
    def create_display_window(self, title, columns):
        top_level = tk.Toplevel(self.root)
        top_level.title(title)
        tree = ttk.Treeview(top_level, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER)

        # Vertical scrollbar
        vsb = ttk.Scrollbar(top_level, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        tree.configure(yscrollcommand=vsb.set)

        # Horizontal scrollbar
        hsb = ttk.Scrollbar(top_level, orient="horizontal", command=tree.xview)
        hsb.pack(side='bottom', fill='x')
        tree.configure(xscrollcommand=hsb.set)

        tree.pack(expand=True, fill='both')
        return tree

    # Show All functions (one for each entity)
    def show_all_retailers(self):
        columns = ["Retailer ID", "Name", "Location", "Contact Info"]
        tree = self.create_display_window("All Retailers", columns)
        all_retailers_data = get_all_retailers()
        for retailer_id, name, location, contact_info in all_retailers_data:
            tree.insert("", 'end', values=(retailer_id, name, location, contact_info))

    def show_all_inventory(self):
        columns = ["Inventory ID", "Product ID", "Quantity", "Location"]
        tree = self.create_display_window("All Inventory", columns)
        all_inventory_data = get_all_inventory()
        for inventory_id, product_id, quantity, location in all_inventory_data:
            tree.insert("", 'end', values=(inventory_id, product_id, quantity, location))

    def show_all_orders(self):
        columns = ["Order ID", "Retailer ID", "Order Date"]
        tree = self.create_display_window("All Orders", columns)
        all_orders_data = get_all_orders()
        for order_id, retailer_id, order_date in all_orders_data:
            tree.insert("", 'end', values=(order_id, retailer_id, order_date))

    def show_all_order_details(self):
        columns = ["Order ID", "Product ID", "Quantity"]
        tree = self.create_display_window("All Order Details", columns)
        all_order_details_data = get_all_order_details()
        for order_id, product_id, quantity in all_order_details_data:
            tree.insert("", 'end', values=(order_id, product_id, quantity))

    def show_all_suppliers(self):
        columns = ["Supplier ID", "Name", "Location", "Contact Info"]
        tree = self.create_display_window("All Suppliers", columns)
        # Replace 'get_all_suppliers' with your actual function to retrieve supplier data from Redis
        all_suppliers_data = get_all_suppliers()
        for item in all_suppliers_data:
            tree.insert("", 'end', values=(item['supplier_id'], item['name'], item['location'], item['contact_info']))

    def show_all_products(self):
        columns = ["Product ID", "Name", "Description", "Price", "Supplier ID"]
        tree = self.create_display_window("All Products", columns)
        # Replace 'get_all_products' with your actual function to retrieve product data from Redis
        all_products_data = get_all_products()
        for item in all_products_data:
            tree.insert("", 'end', values=(item['product_id'], item['name'], item['description'], item['price'], item['supplier_id']))


if __name__ == "__main__":
    root = ctk.CTk()
    app = InventoryManagementGUI(root)
    root.mainloop()
