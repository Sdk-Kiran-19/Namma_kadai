from kadai import db
from datetime import datetime

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    cash_balance = db.Column(db.Float,nullable = False,default=1000.0)

class Item(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    item_price = db.Column(db.Float, nullable=False)
    qty = db.Column(db.Integer, default=0) 

class Purchase(db.Model):
    purchase_id = db.Column(db.Integer, primary_key = True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.item_id'),nullable = False)
    item_name =   db.Column(db.String(100), nullable = False)
    qty = db.Column(db.Integer, nullable = False)
    rate = db.Column(db.Float, nullable = False)
    amount = db.Column(db.Float, nullable = False)
    timestamp = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    item = db.relationship('Item', backref = db.backref('purchases', lazy = True))

class StoredPurchase(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    item_name = db.Column(db.String(100), nullable = False)
    qty = db.Column(db.Integer, nullable = False)
    price = db.Column(db.Float, nullable = False)
    timestamp = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

class Sales(db.Model):
    sales_id = db.Column(db.Integer, primary_key = True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.item_id'),nullable = False)
    qty = db.Column(db.Integer, nullable = False)
    rate = db.Column(db.Float, nullable = False)
    amount = db.Column(db.Float , nullable = False)
    timestamp = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    item = db.relationship('Item', backref = db.backref('sales', lazy = True))


class StoredSale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class ItemPurchased(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

