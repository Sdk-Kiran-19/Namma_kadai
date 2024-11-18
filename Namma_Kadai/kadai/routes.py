from kadai import app, db
from flask import render_template, request, redirect, url_for, flash, jsonify
from kadai.models import Item, Purchase, StoredPurchase, Sales, Company, StoredSale 
from datetime import datetime

def get_items_from_stock():
    return Item.query.all()

def get_stored_purchase():
    return StoredPurchase.query.all()
    
def get_stored_sale():
    return StoredSale.query.all()

def get_company():
    return Company.query.first()

def get_all_purchased_items():
    return Purchase.query.all()

@app.route('/')
@app.route('/home')
def home():
    items = get_items_from_stock()
    company = Company.query.first()
    StoredPurchase.query.delete()
    StoredSale.query.delete()
    db.session.commit()
    return render_template('home.html', items=items, company=company)

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    StoredSale.query.delete()
    db.session.commit()
    if request.method == 'POST':
        item_id = request.form['item_id']
        if item_id == "new":
            item_name = request.form['new_item_name'].capitalize()
            if Item.query.filter_by(item_name=item_name).first():
                flash('Item already exists! Check in the stock', 'danger')
                return redirect(url_for('purchase'))
            price = request.form['price']
        else:
            item = Item.query.filter_by(item_id=item_id).first()
            item_name = item.item_name
            price = item.item_price
        quantity = request.form['qty']
        if StoredPurchase.query.filter_by(item_name=item_name).first():
            flash('Item already added to purchase list! You can edit below', 'danger')
            return redirect(url_for('purchase'))
        new_item = StoredPurchase(item_name=item_name, qty=quantity, price=price)
        db.session.add(new_item)    
        db.session.commit()
        flash('Item added to purchase list successfully!', 'success')
        return redirect(url_for('purchase'))
    purchased_items = StoredPurchase.query.all()
    items = get_items_from_stock()
    company = get_company()
    return render_template('purchase.html', purchased_items=purchased_items, items=items, company = company)

@app.route('/purchase/get/<int:item_id>')
def get_purchase_item(item_id):
    item = StoredPurchase.query.get_or_404(item_id)
    return jsonify({
        'item_name': item.item_name,
        'qty': item.qty,
        'price': item.price
    })

@app.route('/purchase/edit/<int:item_id>', methods=['POST'])
def edit_purchase(item_id):
    try:
        data = request.get_json()
        purchase_item = StoredPurchase.query.get_or_404(item_id)
        purchase_item.item_name = data['item_name']
        purchase_item.qty = data['qty']
        purchase_item.price = data['price']
        
        db.session.commit()
        
        flash('Item updated successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/purchase/delete/<int:item_id>')
def delete_purchase(item_id):
    item = StoredPurchase.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('purchase'))

@app.route('/confirm_purchase', methods=['POST'])
def confirm_purchase():
    item_names = request.form.getlist('item_name[]')
    quantities = request.form.getlist('qty[]')
    prices = request.form.getlist('price[]')

    total_purchase_amount = 0
    purchase_items = []

    for item_name, qty, price in zip(item_names, quantities, prices):
        qty = int(qty)
        price = float(price)
        total_purchase_amount += qty * price

        item = Item.query.filter_by(item_name=item_name.capitalize()).first()
        if not item:
            item = Item(item_name=item_name.capitalize(), qty=0, item_price=price)
            db.session.add(item)
            db.session.flush()

        item.qty += qty
        db.session.add(item)

        purchase_entry = Purchase(
            item_id=item.item_id,
            item_name=item_name,
            qty=qty,
            rate=price,
            amount=qty * price,
            timestamp=datetime.now()
        )
        purchase_items.append(purchase_entry)
    
    company = Company.query.first()
    if company.cash_balance < total_purchase_amount:
        flash('Insufficient funds!', 'danger')
        return redirect(url_for('purchase'))
    
    company.cash_balance -= total_purchase_amount
    db.session.add(company)
    db.session.add_all(purchase_items)
    StoredPurchase.query.delete()
    db.session.commit()
    flash('Purchase successful!', 'success')
    return redirect(url_for('home')) 

   

@app.route('/purchase_report')
def purchase_report():
    purchases = Purchase.query.order_by(Purchase.timestamp.desc()).all()
    return render_template('purchase_report.html', purchases=purchases)


@app.route('/sales', methods=['GET', 'POST'])
def sales():
    StoredPurchase.query.delete()
    db.session.commit()
    if request.method == 'POST':
        item_id = request.form['item_id']
        item = Item.query.filter_by(item_id=item_id).first()
        item_name = item.item_name
        if StoredSale.query.filter_by(item_name = item_name).first():
            flash("Item exist in sale list!! You can modify if required", "danger")
            return redirect(url_for("sales"))
        quantity = int(request.form['qty'])
        stock = item.qty
        if quantity > stock:
            flash('Selected quantity is more than stock!', 'danger')
            return redirect(url_for('sales'))
        price = item.item_price
        new_sale = StoredSale(item_name=item_name, qty=quantity, price=price, total = quantity * price)
        db.session.add(new_sale)
        db.session.commit()
        flash('Item added to sale list successfully!', 'success')
        return redirect(url_for('sales'))
    
    sale_items = get_stored_sale()
    items = get_items_from_stock()  
    return render_template('sales.html', sale_items=sale_items, items=items)

@app.route('/sales/get/<int:item_id>')
def get_sale_item(item_id):
    item = StoredSale.query.get_or_404(item_id)
    return jsonify({
        'item_name': item.item_name,
        'qty': item.qty,
        'price': item.price
    })

@app.route('/sales/edit/<int:item_id>', methods=['POST'])
def edit_sales(item_id):
    try:
        # Get the sales item
        item = StoredSale.query.get_or_404(item_id)
        
        # Get data from JSON request
        data = request.get_json()
        new_qty = int(data['qty'])
        price = float(data['price'])

        # Get the original item from inventory
        stock_item = Item.query.filter_by(item_name=item.item_name).first()
        
        # Calculate available stock
        # Add back the current quantity in the sale before checking
        current_sale_qty = item.qty
        total_available = stock_item.qty + current_sale_qty
        
        # Check if new quantity exceeds available stock
        if new_qty > total_available:
            return jsonify({
                'error': f'Selected quantity ({new_qty}) exceeds available stock ({total_available})'
            }), 400

        # Update the sale item
        item.qty = new_qty
        item.price = price
        item.total = new_qty * price
        
        db.session.commit()
        
        flash('Item updated successfully!', 'success')
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': str(e)
        }), 400


@app.route('/sales/delete/<int:item_id>')
def delete_sales(item_id):
    item = StoredSale.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('sales'))

@app.route('/confirm_sales', methods=['POST'])
def confirm_sales():
    item_names = request.form.getlist('item_name[]')
    quantities = request.form.getlist('qty[]')
    prices = request.form.getlist('price[]')

    total_sale_amount = 0
    sale_items = []

    for item_name, qty, price in zip(item_names, quantities, prices):
        qty = int(qty)
        price = float(price)
        total_sale_amount += qty * price 
        item = Item.query.filter_by(item_name=item_name.capitalize()).first()
        
        if not item or item.qty < qty:
            flash(f'Insufficient stock for {item_name}!', 'danger')
            return redirect(url_for('sales'))
            
        item.qty -= qty
        db.session.add(item)
        
        sale_entry = Sales(
            item_id=item.item_id,
            qty=qty,
            rate=price,
            amount=qty * price,
            timestamp=datetime.now()
        )
        sale_items.append(sale_entry)
        
    company = Company.query.first()
    company.cash_balance += total_sale_amount
    db.session.add(company)
    db.session.add_all(sale_items)
    StoredSale.query.delete()
    db.session.commit()
    flash('Sale successful!', 'success')
    return redirect(url_for('home'))


