from flask import Blueprint, render_template, current_app, request, redirect, session
from database.sql_provider import SQLProvider
from database.operations import select


bp_auth = Blueprint('bp_auth', __name__, template_folder='templates')
sql_provider = SQLProvider('bp_auth/sql')


@bp_auth.route('/', methods=['GET', 'POST'])
def auth_login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        login = request.form.get('login')
        password = request.form.get('password')
        if not login or not password:
            return render_template('login.html', error="Заполните пустые поля")
        if not login.isalnum() or not password.isalnum():
            return render_template('login.html', error="Некорректный ввод")
        sql_statement = sql_provider.get('iuser.sql', {'login': login, 'password': password})
        data = select(current_app.config['DB_CONFIG'], sql_statement)
        if data:
            session['user_id'] = data[0]['id_internal']
            session['user_group'] = data[0]['group_name']
        else:
            sql_statement = sql_provider.get('euser.sql', {'login': login, 'password': password})
            data = select(current_app.config['DB_CONFIG'], sql_statement)
            if data:
                session['user_id'] = data[0]['id_external']
                session['user_group'] = 'buyer'
            else:
                return render_template('login.html', error="Проверьте логин и пароль")
        return redirect('/')


@bp_auth.route('/logout')
def auth_logout():
    session.clear()
    return redirect('/auth')

