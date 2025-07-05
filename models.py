from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    subcategories = db.relationship('SubCategory', backref='category', lazy=True)

class SubCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

class Marketplace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
class CommissionRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    subcategory_id = db.Column(db.Integer, db.ForeignKey('sub_category.id'))
    marketplace_id = db.Column(db.Integer, db.ForeignKey('marketplace.id'))
    min_price = db.Column(db.Float)
    max_price = db.Column(db.Float)
    commission_percent = db.Column(db.Float)

    # ✅ These lines fix the error
    category = db.relationship('Category', backref='rules')
    subcategory = db.relationship('SubCategory', backref='rules')
    marketplace = db.relationship('Marketplace', backref='rules')




class CourierCharge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight_slab = db.Column(db.Float, nullable=False)
    charge = db.Column(db.Float, nullable=False)






