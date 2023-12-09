from functools import wraps
from flask import session, redirect, current_app, request, render_template

error = { 1: 'Недостаточно прав для посещения данной страницы',
          2: 'Данная страница доступна только персоналу',
          3: 'Необходимо войти в систему' }


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' in session:
            return func(*args, **kwargs)
        else:
            return redirect('/auth')
    return wrapper


# def group_required(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         if 'user_id' in session:
#             user_role = session.get('user_group')
#             if user_role:
#                 access = current_app.config['ACCESS_CONFIG']
#                 user_func = request.endpoint
#                 if user_role in access and user_func in access[user_role]:
#                     return func(*args, **kwargs)
#                 else:
#                     msg = (1, 'Недостаточно прав для посещения данной страницы')
#             else:
#                 msg = (1, 'Данная страница доступна только персоналу')
#         else:
#             msg = (0, 'Необходимо войти в систему')
#         return render_template('error.html', error=msg)
#     return wrapper


def group_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' in session:
            user_role = session.get('user_group')
            if user_role:
                access = current_app.config['ACCESS_CONFIG']
                user_func = request.endpoint
                if user_role in access and\
                        (user_func.split('.')[-1] in access[user_role] or user_func.split('.')[0] in access[user_role]):
                    return func(*args, **kwargs)
                else:
                    msg = (1, 'Недостаточно прав для посещения данной страницы')
            else:
                msg = (1, 'Данная страница доступна только персоналу')
        else:
            msg = (0, 'Необходимо войти в систему')
        return render_template('error.html', error=msg)
    return wrapper
