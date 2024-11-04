from mongoengine import Document, StringField, IntField, ReferenceField, DateTimeField, connect

connect('InventoryManagementApplication')  # Connects to MongoDB


class Retailer(Document):
    retailer_id = StringField(primary_key=True)
    name = StringField(required=True)
    location = StringField()
    contact_info = StringField()


class Order(Document):
    order_id = StringField(primary_key=True)
    retailer = ReferenceField(Retailer)
    order_date = DateTimeField()


class Inventory(Document):
    inventory_id = StringField(primary_key=True)
    product_id = StringField(required=True)  # Would ideally reference a Product collection
    quantity = IntField()
    location = StringField()


class OrderDetails(Document):
    order = ReferenceField(Order, required=True)
    product_id = StringField(required=True)  # Reference to Product
    quantity = IntField()


class Product(Document):
    product_id = StringField(primary_key=True)
    name = StringField(required=True)
    description = StringField()
    price = IntField()
