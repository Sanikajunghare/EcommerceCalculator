from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from models import db, Category, SubCategory, Marketplace, CommissionRule, CourierCharge
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# ---------- Database Setup ----------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, 'data', 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ---------- Admin Home ----------
@app.route('/admin')
def admin_home():
    rules = CommissionRule.query.all()
    categories = Category.query.all()
    subcategories = SubCategory.query.all()
    marketplaces = Marketplace.query.all()
    courier_charges = CourierCharge.query.all()
    return render_template(
        'admin_panel.html',
        rules=rules,
        categories=categories,
        subcategories=subcategories,
        marketplaces=marketplaces,
        courier_charges=courier_charges
    )

# ---------- Add Courier Charge ----------
@app.route('/admin/add_courier_charge', methods=['POST'])
def add_courier_charge():
    weight = float(request.form['weight_slab'])
    charge = float(request.form['charge'])
    db.session.add(CourierCharge(weight_slab=weight, charge=charge))
    db.session.commit()
    flash("✅ Courier charge added successfully!", "success")
    return redirect(url_for('admin_home'))

# ---------- Delete Courier Charge ----------
@app.route('/admin/delete_courier_charge/<int:charge_id>')
def delete_courier_charge(charge_id):
    charge = CourierCharge.query.get(charge_id)
    if charge:
        db.session.delete(charge)
        db.session.commit()
        flash("🗑️ Courier charge deleted.", "success")
    return redirect(url_for('admin_home'))

# ---------- Insert Standard Courier Charges ----------
@app.route('/admin/insert_standard_charges')
def insert_standard_charges():
    # Standard STEP Level courier rates (Amazon-based)
    slabs = [
        (0.5, 63),                           # First 500g
        (1, 83),                             # 500g – 1kg
        (2, 120),                            # 1kg – 2kg
        (3, 120 + 34),                       # 2kg – 3kg
        (4, 120 + 34*2),                     # 2kg – 4kg
        (5, 120 + 34*3),                     # 2kg – 5kg
        (6, 120 + 34*3 + 18),                # After 5kg: +₹18/kg
        (7, 120 + 34*3 + 18*2),
        (8, 120 + 34*3 + 18*3),
    ]

    added = 0
    for weight, charge in slabs:
        if not CourierCharge.query.filter_by(weight_slab=weight).first():
            db.session.add(CourierCharge(weight_slab=weight, charge=charge))
            added += 1

    db.session.commit()
    flash(f"✅ {added} standard courier charges inserted successfully!", "success")
    return redirect(url_for('admin_home'))


# ---------- Add Commission Rule ----------
@app.route('/admin/add_rule', methods=['POST'])
def add_rule():
    category_id = request.form['category_id']
    subcategory_id = request.form['subcategory_id']
    marketplace_id = request.form['marketplace_id']
    min_price = float(request.form['min_price'])
    max_price = float(request.form['max_price'])
    commission_percent = float(request.form['commission_percent'])

    rule = CommissionRule(
        category_id=category_id,
        subcategory_id=subcategory_id,
        marketplace_id=marketplace_id,
        min_price=min_price,
        max_price=max_price,
        commission_percent=commission_percent
    )
    db.session.add(rule)
    db.session.commit()
    flash("✅ Commission rule added!", "success")
    return redirect(url_for('admin_home'))

# ---------- Edit Commission Rule ----------
@app.route('/admin/edit_rule/<int:rule_id>', methods=['GET', 'POST'])
def edit_rule(rule_id):
    rule = CommissionRule.query.get_or_404(rule_id)
    categories = Category.query.all()
    subcategories = SubCategory.query.all()
    marketplaces = Marketplace.query.all()

    if request.method == 'POST':
        rule.category_id = request.form['category_id']
        rule.subcategory_id = request.form['subcategory_id']
        rule.marketplace_id = request.form['marketplace_id']
        rule.min_price = float(request.form['min_price'])
        rule.max_price = float(request.form['max_price'])
        rule.commission_percent = float(request.form['commission_percent'])
        db.session.commit()
        flash("✏️ Rule updated!", "success")
        return redirect(url_for('admin_home'))

    return render_template('edit_rule.html', rule=rule, categories=categories, subcategories=subcategories, marketplaces=marketplaces)

# ---------- Delete Commission Rule ----------
@app.route('/admin/delete_rule/<int:rule_id>')
def delete_rule(rule_id):
    rule = CommissionRule.query.get(rule_id)
    if rule:
        db.session.delete(rule)
        db.session.commit()
        flash("🗑️ Commission rule deleted.", "success")
    return redirect(url_for('admin_home'))

# ---------- Add Category ----------
@app.route('/admin/add_category', methods=['POST'])
def add_category():
    name = request.form['category_name']
    db.session.add(Category(name=name))
    db.session.commit()
    flash("✅ Category added!", "success")
    return redirect(url_for('admin_home'))

# ---------- Delete Category ----------
@app.route('/admin/delete_category/<int:category_id>')
def delete_category(category_id):
    category = Category.query.get(category_id)
    if category:
        db.session.delete(category)
        db.session.commit()
        flash("🗑️ Category deleted!", "success")
    return redirect(url_for('admin_home'))

# ---------- Add SubCategory ----------
@app.route('/admin/add_subcategory', methods=['POST'])
def add_subcategory():
    name = request.form['subcategory_name']
    category_id = request.form['subcategory_category']
    db.session.add(SubCategory(name=name, category_id=category_id))
    db.session.commit()
    flash("✅ Subcategory added!", "success")
    return redirect(url_for('admin_home'))

# ---------- Delete SubCategory ----------
@app.route('/admin/delete_subcategory/<int:subcategory_id>')
def delete_subcategory(subcategory_id):
    sub = SubCategory.query.get(subcategory_id)
    if sub:
        db.session.delete(sub)
        db.session.commit()
        flash("🗑️ Subcategory deleted!", "success")
    return redirect(url_for('admin_home'))

# ---------- Add Marketplace ----------
@app.route('/admin/add_marketplace', methods=['POST'])
def add_marketplace():
    name = request.form['marketplace_name']
    db.session.add(Marketplace(name=name))
    db.session.commit()
    flash("✅ Marketplace added!", "success")
    return redirect(url_for('admin_home'))

# ---------- Delete Marketplace ----------
@app.route('/admin/delete_marketplace/<int:marketplace_id>')
def delete_marketplace(marketplace_id):
    mp = Marketplace.query.get(marketplace_id)
    if mp:
        db.session.delete(mp)
        db.session.commit()
        flash("🗑️ Marketplace deleted!", "success")
    return redirect(url_for('admin_home'))

# ---------- Filter SubCategories by Category ----------
@app.route('/admin/subcategories/<int:category_id>')
def get_subcategories(category_id):
    subcategories = SubCategory.query.filter_by(category_id=category_id).all()
    sub_list = [{'id': sub.id, 'name': sub.name} for sub in subcategories]
    return jsonify(sub_list)

# ----- One-time DB creation -----
with app.app_context():
    if not os.path.exists(db_path):
        db.create_all()
        print("✅ New database created at", db_path)

# ---------- Run App ----------
if __name__ == '__main__':
    app.run(debug=True, port=5001)
