from flask import Blueprint, render_template, current_app, request
from database.sql_provider import SQLProvider
from database.operations import select
from access import group_required


bp_query = Blueprint('bp_query', __name__, template_folder='templates')
sql_provider = SQLProvider('bp_query/sql')


@bp_query.route('/')
@group_required
def query_menu():
    return render_template('query.html')


@bp_query.route('/country', methods=['GET', 'POST'])
@group_required
def country():
    params = {'category': 1, 'country': 1, 'price': 0}
    if request.method == 'GET':
        return render_template('input.html', params=params)
    else:
        country = request.form.get('country')
        category = request.form.get('category')
        if not country or not category:
            return render_template('input.html', error="Заполните пустые поля", params=params)
        if not country.isalpha() or not category.isalpha():
            return render_template('input.html', error="Некорректный ввод", params=params)
        else:
            sql_statement = sql_provider.get('country.sql', {'country': country, 'category': category})
        data = select(current_app.config['DB_CONFIG'], sql_statement)
        return render_template('result.html', data=data, flag=len(data), title='Товары по категории и стране')


@bp_query.route('/price', methods=['GET', 'POST'])
@group_required
def price():
    params = {'category': 1, 'country': 0, 'price': 1}
    if request.method == 'GET':
        return render_template('input.html', params=params)
    else:
        price = request.form.get('price')
        category = request.form.get('category')
        if not price or not category:
            return render_template('input.html', error="Заполните пустые поля", params=params)
        if not price.isdigit() or not category.isalpha():
            return render_template('input.html', error="Некорректный ввод", params=params)
        else:
            sql_statement = sql_provider.get('price.sql', {'price': price, 'category': category})
        data = select(current_app.config['DB_CONFIG'], sql_statement)
        return render_template('result.html', data=data, flag=len(data), title='Товары по категории и цене')



