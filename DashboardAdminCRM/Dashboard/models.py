from django.db import models
import mongoengine
from datetime import datetime

# Create your models here.
class Contact(mongoengine.Document):
    id = mongoengine.StringField(primary_key=True)  # Usando el campo _id como id
    name = mongoengine.StringField(required=True)
    email = mongoengine.EmailField(required=True)
    phone = mongoengine.StringField()
    address = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'contacts'}

class Product(mongoengine.Document):
    id = mongoengine.IntField(primary_key=True)  # Usando el campo _id como id
    description = mongoengine.StringField(required=True)

    meta = {'collection': 'products'}

class SaleDetail(mongoengine.Document):
    id = mongoengine.ObjectIdField(primary_key=True)  # Usando el campo _id como id
    invoiceNo = mongoengine.StringField(required=True)
    stockCode = mongoengine.StringField(required=True)
    description = mongoengine.StringField(required=True)
    quantity = mongoengine.IntField(required=True)
    invoiceDate = mongoengine.DateTimeField(required=True)
    unitPrice = mongoengine.FloatField(required=True)
    contactId = mongoengine.StringField(required=True)
    country = mongoengine.StringField(required=True)
    productId = mongoengine.IntField(required=True)

    meta = {'collection': 'sale_details'}

class User(mongoengine.Document):
    id = mongoengine.ObjectIdField(primary_key=True)  # Usando el campo _id como id
    name = mongoengine.StringField(required=True)
    password = mongoengine.StringField(required=True)
    class_field = mongoengine.StringField(db_field='_class')  # Mapeo del campo _class

    meta = {'collection': 'user'}


