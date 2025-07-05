# ✅ Final updated app.py
from flask import Flask, render_template, request, jsonify
from models import db, Category, SubCategory, Marketplace, CommissionRule
from models import CourierCharge

import os

app = Flask(__name__)

# Database setup
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, 'data', 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create DB and seed values once
with app.app_context():
    db.create_all()
    if not Category.query.first():
        db.session.add_all([
            Category(name='Electronics'),
            SubCategory(name='Mobile', category_id=1),
            SubCategory(name='T-Shirts', category_id=2),
            Marketplace(name='Amazon'),
            Marketplace(name='Flipkart')
        ])
        db.session.commit()

@app.route('/')
def index():
    categories = Category.query.all()
    subcategories = SubCategory.query.all()
    marketplaces = Marketplace.query.all()
    return render_template('index.html', categories=categories, subcategories=subcategories, marketplaces=marketplaces)

@app.route('/calculate', methods=['POST'])
def calculate():
    mrp = float(request.form['mrp'])
    discount = float(request.form['discount'])
    cost = float(request.form['cost'])
    weight = float(request.form['weight'])
    vol_weight = float(request.form.get('volumetric_weight') or 0)
    commission_input = request.form.get('commission_rate')

    commission_rate = float(commission_input) if commission_input else 10
    fixed_fee = 30
    shipping_weight = max(weight, vol_weight)

    # ✅ Get courier charge from database based on slab
    slab = CourierCharge.query.filter(
        CourierCharge.weight_slab >= shipping_weight
    ).order_by(CourierCharge.weight_slab.asc()).first()
    shipping_charge = slab.charge if slab else 0

    # ✅ Selling price after discount
    selling_price = round(mrp * (1 - discount / 100))

    # ✅ Get dynamic commission from DB
    commission_rule = CommissionRule.query.filter(
        CommissionRule.category_id == int(request.form['category']),
        CommissionRule.subcategory_id == int(request.form['subcategory']),
        CommissionRule.marketplace_id == int(request.form['marketplace']),
        CommissionRule.min_price <= selling_price,
        CommissionRule.max_price >= selling_price
    ).first()
    if commission_rule:
        commission_rate = commission_rule.commission_percent

    # ✅ Deductions & GST
    commission = selling_price * commission_rate / 100
    commission_gst = commission * 0.18
    fixed_fee_gst = fixed_fee * 0.18
    courier_gst = shipping_charge * 0.18

    total_deductions = commission + fixed_fee + shipping_charge
    total_gst = commission_gst + fixed_fee_gst + courier_gst
    receivable = selling_price - (total_deductions + total_gst)
    profit = receivable - cost

    # ✅ Final result to frontend
    result = {
        'mrp': round(mrp, 2),
        'discount': round(discount, 2),
        'selling_price': round(selling_price),
        'commission': round(commission, 2),
        'commission_gst': round(commission_gst, 2),
        'fixed_fee': round(fixed_fee, 2),
        'fixed_fee_gst': round(fixed_fee_gst, 2),
        'shipping_weight': round(shipping_weight, 2),
        'shipping_charge': round(shipping_charge, 2),
        'courier_gst': round(courier_gst, 2),
        'total_deductions': round(total_deductions + total_gst, 2),
        'receivable': round(receivable, 2),
        'profit': round(profit, 2)
    }

    # Reload dropdowns
    categories = Category.query.all()
    subcategories = SubCategory.query.all()
    marketplaces = Marketplace.query.all()

    return render_template('index.html', result=result, categories=categories, subcategories=subcategories, marketplaces=marketplaces)



    commission_rule = CommissionRule.query.filter(
        CommissionRule.category_id == int(request.form['category']),
        CommissionRule.subcategory_id == int(request.form['subcategory']),
        CommissionRule.marketplace_id == int(request.form['marketplace']),
        CommissionRule.min_price <= selling_price,
        CommissionRule.max_price >= selling_price
    ).first()

    if commission_rule:
        commission_rate = commission_rule.commission_percent

    commission = selling_price * commission_rate / 100
    commission_gst = commission * 0.18
    fixed_fee_gst = fixed_fee * 0.18
    shipping_weight = max(weight, vol_weight)
    shipping_charge = shipping_rate_per_kg * shipping_weight
    courier_gst = shipping_charge * 0.18

    total_deductions = commission + fixed_fee + shipping_charge
    total_gst = commission_gst + fixed_fee_gst + courier_gst
    receivable = selling_price - (total_deductions + total_gst)
    profit = receivable - cost

    result = {
        'mrp': round(mrp, 2),
        'discount': round(discount, 2),
        'selling_price': round(selling_price),
        'commission': round(commission, 2),
        'commission_gst': round(commission_gst, 2),
        'fixed_fee': round(fixed_fee, 2),
        'fixed_fee_gst': round(fixed_fee_gst, 2),
        'shipping_weight': round(shipping_weight, 2),
        'shipping_charge': round(shipping_charge, 2),
        'courier_gst': round(courier_gst, 2),
        'total_deductions': round(total_deductions + total_gst, 2),
        'receivable': round(receivable, 2),
        'profit': round(profit, 2)
    }

    categories = Category.query.all()
    subcategories = SubCategory.query.all()
    marketplaces = Marketplace.query.all()

    return render_template('index.html', result=result, categories=categories, subcategories=subcategories, marketplaces=marketplaces)

@app.route('/admin/subcategories/<int:category_id>')
def get_subcategories(category_id):
    subcategories = SubCategory.query.filter_by(category_id=category_id).all()
    return jsonify([{'id': s.id, 'name': s.name} for s in subcategories])

if __name__ == '__main__':
    app.run(debug=True)
