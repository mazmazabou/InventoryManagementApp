FinalInventoryManagementApp


Description:
FinalInventoryManagementApp is an inventory management system designed to streamline operations for warehousing businesses. This application facilitates efficient management of inventory, orders, products, suppliers, and retailers through a user-friendly graphical interface. It integrates both MongoDB for persistent storage and Redis for quick data retrieval and caching, ensuring that the application is both fast and reliable.

Installation Instructions:
Prerequisites
Python 3.7 or newer
MongoDB installed and running on localhost
Redis server installed and running on localhost

Libraries:
mongoengine
redis
tkinter
customtkinter

You can install the necessary Python libraries using pip:
pip install mongoengine redis tkinter customtkinter

Setup:
Clone the repository or download the source files to your local machine.
Ensure MongoDB and Redis services are running.
Navigate to the application directory.
Running the Application
Execute the main GUI application by running:

python3 gui.py

This command will launch the graphical user interface, allowing you to interact with the inventory system.

Usage Instructions:
Main Features:
Create, Retrieve, Update, Delete: Perform CRUD operations on inventory items, orders, products, suppliers, and retailers.
Display All: Easily view all records in a tabular format through the GUI.
Redis Integration: Use Redis for managing product and supplier information with quick access patterns.

GUI Navigation:
Select an action (Create, Retrieve, Update, Delete, Display All) from the dropdown menu.
Select an entity (Inventory, Order, Order Detail, Retailer, Product, Supplier) then press 'Confirm'to  apply the action and generate the input fields for the attributes.
Input the required information in the dynamically generated fields and submit.
