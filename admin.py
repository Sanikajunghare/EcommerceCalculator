from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, Category, SubCategory, Marketplace, CommissionRule, CourierCharge  # ✅ Import added
import os

app = Flask(__name__)


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
    courier_charges = CourierCharge.query.all()  # ✅ Include courier charges
    return render_template(
        'admin_panel.html',
        rules=rules,
        categories=categories,
        subcategories=subcategories,
        marketplaces=marketplaces,
        courier_charges=courier_charges  # ✅ Pass to template
    )

# ---------- Add Courier Charge ----------
@app.route('/admin/add_courier_charge', methods=['POST'])
def add_courier_charge():
    weight = float(request.form['weight'])
    charge = float(request.form['charge'])
    db.session.add(CourierCharge(weight=weight, charge=charge))
    db.session.commit()
    return redirect(url_for('admin_home'))

# ---------- Delete Courier Charge ----------
@app.route('/admin/delete_courier_charge/<int:charge_id>')
def delete_courier_charge(charge_id):
    charge = CourierCharge.query.get(charge_id)
    if charge:
        db.session.delete(charge)
        db.session.commit()
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
        return redirect(url_for('admin_home'))

    return render_template('edit_rule.html', rule=rule, categories=categories, subcategories=subcategories, marketplaces=marketplaces)

# ---------- Delete Commission Rule ----------
@app.route('/admin/delete_rule/<int:rule_id>')
def delete_rule(rule_id):
    rule = CommissionRule.query.get(rule_id)
    if rule:
        db.session.delete(rule)
        db.session.commit()
    return redirect(url_for('admin_home'))

# ---------- Add Category ----------
@app.route('/admin/add_category', methods=['POST'])
def add_category():
    name = request.form['category_name']
    db.session.add(Category(name=name))
    db.session.commit()
    return redirect(url_for('admin_home'))

# ---------- Edit Category ----------
@app.route('/admin/edit_category/<int:category_id>', methods=['POST'])
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    category.name = request.form['edit_category_name']
    db.session.commit()
    return redirect(url_for('admin_home'))

# ---------- Delete Category ----------
@app.route('/admin/delete_category/<int:category_id>')
def delete_category(category_id):
    category = Category.query.get(category_id)
    if category:
        db.session.delete(category)
        db.session.commit()
    return redirect(url_for('admin_home'))

# ---------- Add SubCategory ----------
@app.route('/admin/add_subcategory', methods=['POST'])
def add_subcategory():
    name = request.form['subcategory_name']
    category_id = request.form['subcategory_category']
    db.session.add(SubCategory(name=name, category_id=category_id))
    db.session.commit()
    return redirect(url_for('admin_home'))

# ---------- Edit SubCategory ----------
@app.route('/admin/edit_subcategory/<int:subcategory_id>', methods=['POST'])
def edit_subcategory(subcategory_id):
    sub = SubCategory.query.get_or_404(subcategory_id)
    sub.name = request.form['edit_subcategory_name']
    sub.category_id = request.form['edit_subcategory_category']
    db.session.commit()
    return redirect(url_for('admin_home'))

# ---------- Delete SubCategory ----------
@app.route('/admin/delete_subcategory/<int:subcategory_id>')
def delete_subcategory(subcategory_id):
    sub = SubCategory.query.get(subcategory_id)
    if sub:
        db.session.delete(sub)
        db.session.commit()
    return redirect(url_for('admin_home'))

# ---------- Add Marketplace ----------
@app.route('/admin/add_marketplace', methods=['POST'])
def add_marketplace():
    name = request.form['marketplace_name']
    db.session.add(Marketplace(name=name))
    db.session.commit()
    return redirect(url_for('admin_home'))

# ---------- Edit Marketplace ----------
@app.route('/admin/edit_marketplace/<int:marketplace_id>', methods=['POST'])
def edit_marketplace(marketplace_id):
    mp = Marketplace.query.get_or_404(marketplace_id)
    mp.name = request.form['edit_marketplace_name']
    db.session.commit()
    return redirect(url_for('admin_home'))

# ---------- Delete Marketplace ----------
@app.route('/admin/delete_marketplace/<int:marketplace_id>')
def delete_marketplace(marketplace_id):
    mp = Marketplace.query.get(marketplace_id)
    if mp:
        db.session.delete(mp)
        db.session.commit()
    return redirect(url_for('admin_home'))

# ---------- Filter SubCategories by Category (for JS) ----------
@app.route('/admin/subcategories/<int:category_id>')
def get_subcategories(category_id):
    subcategories = SubCategory.query.filter_by(category_id=category_id).all()
    sub_list = [{'id': sub.id, 'name': sub.name} for sub in subcategories]
    return jsonify(sub_list)

# ---------- Run App ----------
if __name__ == '__main__':
    app.run(debug=True, port=5001)