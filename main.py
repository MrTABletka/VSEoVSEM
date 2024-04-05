from flask import Flask, render_template, url_for, redirect, request, make_response, session, abort, jsonify
from flask_login import LoginManager, logout_user, login_required, current_user, login_user
import json
import ORM_models
from forms.loginform import LoginForm
from forms.user import RegisterForm
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = ORM_models.create_session()
    return db_sess.query(User).get(user_id)

@app.route('/')
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = ORM_models.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            password=form.password.data
        )
        db_sess.add(user)
        db_sess.commit()
        return redirect("login")
    return render_template('register.html', title='Регистрация', form=form, message='read')


@app.route('/login', methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = ORM_models.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)

#@app.route('/api/apikey123/create_obj/<string:dat>', methods=['POST'])
#def create_obj(dat):
#    data = json.loads(dat)
#    create_object(data["name"], data["des"])
#    return data["name"]



@app.route('/index')
def index():
    return "aaaaa"


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')
