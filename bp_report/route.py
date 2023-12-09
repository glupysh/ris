from flask import Blueprint, render_template, current_app, request, redirect, session
from database.sql_provider import SQLProvider
from database.operations import select, call_procedure
from access import group_required


bp_report = Blueprint('bp_report', __name__, template_folder='templates')
sql_provider = SQLProvider('bp_report/sql')


report_list = [
    {"rep_name": "Отчёт по товарам", "sql_name": "rep_product.sql", "proc_name": "rep_product"},
    {"rep_name": "Отчёт по покупателям", "sql_name": "rep_external.sql", "proc_name": "rep_external"},
]


@bp_report.route('/', methods=['GET', 'POST'])
@group_required
def report_menu():
    if request.method == 'GET':
        return render_template('report.html', report_list=report_list, group=session.get('user_group'))
    else:
        month = request.form.get('month')
        year = request.form.get('year')
        if not month or not year:
            return render_template('report.html', report_list=report_list, msg="Заполните пустые поля", group=session.get('user_group'))
        if not month.isdigit() or not year.isdigit():
            return render_template('report.html', report_list=report_list, msg="Некорректный ввод", group=session.get('user_group'))
        else:
            sql_name = request.form.get('sql_name')
            sql_statement = sql_provider.get(sql_name, {'month': month, 'year': year})
            data = select(current_app.config['DB_CONFIG'], sql_statement)
            if request.form.get('send') == 'Посмотреть':
                title = f"{request.form.get('rep_name')} за {month}.{year}"
                if data:
                    return render_template('report_result.html', data=data, title=title)
                return render_template("report_error.html", msg="Нет данных за этот отчётный период")
            else:
                if not data:
                    proc_name = request.form.get('proc_name')
                    call_procedure(current_app.config['DB_CONFIG'], proc_name, year, month)
                    return render_template('report_error.html', msg="Отчёт создан")
                return render_template("report_error.html", msg="Такой отчёт уже есть")

