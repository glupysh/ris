from flask import Flask, render_template, session
from access import login_required
from bp_report.route import bp_report
from bp_order.route import bp_order
from bp_query.route import bp_query
from bp_auth.route import bp_auth
import json

app = Flask(__name__)
app.secret_key = "Super secret key"

app.register_blueprint(bp_report, url_prefix='/report')
app.register_blueprint(bp_order, url_prefix='/order')
app.register_blueprint(bp_query, url_prefix='/query')
app.register_blueprint(bp_auth, url_prefix='/auth')
app.config['DB_CONFIG'] = json.load(open('configs/db.json'))
app.config['CASHE_CONFIG'] = json.load(open('configs/cashe.json'))
app.config['ACCESS_CONFIG'] = json.load(open('configs/access.json'))


@app.route('/')
@login_required
def home():
    return render_template('home.html', group=session.get('user_group'))


@app.template_filter('translate')
def translate_filter(word):
    d = {'id_external': 'Номер покупателя',
         'id_product': 'Номер товара',
         'user_name': 'Имя покупателя',
         'product_name': 'Наименование товара',
         'id_period': 'Номер периода',
         'period_year': 'Год',
         'period_month': 'Месяц',
         'sales_number': 'Кол-во продаж',
         'sales_price': 'Сумма продаж',
         'purchases_number': 'Кол-во заказов',
         'purchases_price': 'Сумма заказов',
    }
    return d[word]


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)



