from flask import Blueprint, render_template, request, current_app, session, redirect, url_for
from database.connection import DBContextManager
from database.sql_provider import SQLProvider
from database.operations import select
from cashe.wrapper import fetch_from_cache, fetch_from_cache_force
from access import group_required


bp_order = Blueprint('bp_order', __name__, template_folder='templates')
sql_provider = SQLProvider('bp_order/sql')


@bp_order.route('/', methods=['GET', 'POST'])
@group_required
def basket_index():
    cached_select = fetch_from_cache('all_items_cached', current_app.config['CASHE_CONFIG'])(select)
    if request.method == 'GET':
        sql = sql_provider.get('all_items.sql', {})
        items = cached_select(current_app.config['DB_CONFIG'], sql)
        basket = session.get('basket', {})
        return render_template('basket_index.html', items=items, basket=basket)
    else:
        id_product = request.form['id_product']
        sql = sql_provider.get('all_items.sql', {})
        items = select(current_app.config['DB_CONFIG'], sql)
        add_to_basket(id_product, items)
        return redirect(url_for('bp_order.basket_index'))


def add_to_basket(id_product: str, items: dict):
    item_description = [item for item in items if str(item['id_product']) == str(id_product)]
    item_description = item_description[0]
    current_basket = session.get('basket', {})
    if id_product in current_basket:
        current_basket[id_product]['amount'] = current_basket[id_product]['amount'] + 1
    else:
        current_basket[id_product] = {
            'id_product': id_product,
            'product_name': item_description['product_name'],
            'category': item_description['category'],
            'country': item_description['country'],
            'price': item_description['price'],
            'available_quantity': item_description['available_quantity'],
            'amount': 1
        }
        session['basket'] = current_basket
        session.permanent = True


@bp_order.route('/delete', methods=['GET', 'POST'])
@group_required
def delete_from_basket():
    current_basket = session.get('basket', {})
    current_basket.pop(request.args['id_product'])
    session['basket'] = current_basket
    session.permanent = True
    return redirect(url_for('bp_order.basket_index'))


@bp_order.route('/amount', methods=['GET', 'POST'])
@group_required
def edit_amount_basket():
    current_basket = session.get('basket', {})
    if 'value' in request.args:
        id_product = request.args['id_product']
        amount = current_basket[id_product]['amount'] + int(request.args['value'])
    else:
        id_product = request.form['product']
        amount = int(request.form['amount'])
    max_amount = int(current_basket[id_product]['available_quantity'])
    amount = 1 if amount < 1 else amount
    amount = max_amount if amount > max_amount else amount
    current_basket[id_product]['amount'] = amount
    session['basket'] = current_basket
    session.permanent = True
    return redirect(url_for('bp_order.basket_index'))


@bp_order.route('/clear')
@group_required
def clear_basket():
    if 'basket' in session:
        session.pop('basket')
    return redirect(url_for('bp_order.basket_index'))


@bp_order.route('/save_order', methods=['GET', 'POST'])
@group_required
def save_order():
    user_id = session.get('user_id')
    current_basket = session.get('basket', {})
    if len(current_basket) == 0:
        return render_template('error.html', error='Невозможно оформить пустой заказ')
    id_purchase = save_order_with_detail(current_app.config['DB_CONFIG'], user_id, current_basket)
    if id_purchase:
        items = [item for item in current_basket.values()]
        total_price = sum([item['amount'] * item['price'] for item in items])
        session.pop('basket')
        sql = sql_provider.get('all_items.sql', {})
        fetch_from_cache_force('all_items_cached', current_app.config['CASHE_CONFIG'])(select)(current_app.config['DB_CONFIG'], sql)
        return render_template('order_created.html', id_purchase=id_purchase, items=items, total_price=total_price)
    else:
        return render_template('error.html')


def save_order_with_detail(dbconfig: dict, user_id: int, current_basket: dict):
    with DBContextManager(dbconfig) as cursor:
        items = [item for item in current_basket.values()]
        total_price = sum([item['amount'] * item['price'] for item in items])
        sql = sql_provider.get('insert_purchase.sql', {'user_id': user_id, 'total_price': total_price})
        cursor.execute(sql)
        id_purchase = cursor.lastrowid
        for key in current_basket:
            amount = current_basket[key]['amount']
            sql = sql_provider.get('insert_purchase_detail.sql', {'id_purchase': id_purchase, 'id_product': key, 'amount': amount})
            cursor.execute(sql)
            sql = sql_provider.get('update_amount.sql', {'id_product': key, 'amount': amount})
            cursor.execute(sql)
        return id_purchase
