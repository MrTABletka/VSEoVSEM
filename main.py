from flask import Flask, render_template, url_for, redirect, request, make_response, session, abort, jsonify
from flask_login import LoginManager, logout_user, login_required, current_user, login_user
import json
from ORM_models import create_session, User, create_user, Object, create_object, Review, create_review
from forms.loginform import LoginForm
from forms.user import RegisterForm
from forms.obj import ObjForm
from forms.reviev import RevForm
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    return db_sess.query(User).filter(User.id == user_id).first()


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/index")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/index')
@login_required
def index():
    db_sess = create_session()
    objs = db_sess.query(Object).all()
    return render_template("index.html", news=objs)


@app.route('/watch_revievs/<string:name>', methods=['GET', 'POST'])
@login_required
def watch_revievs(name):
    db_sess = create_session()
    id_obj = db_sess.query(Object).filter(Object.name == name).first().id
    objs = db_sess.query(Review).filter(Review.object_id == id_obj).all()
    return render_template("reviev_watch.html", objs=objs, id_obj=id_obj)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")

        create_user(form.name.data, form.email.data, form.password.data)
        return redirect("/login")
    return render_template('register.html', title='Регистрация', form=form)


# @app.route('/api/apikey123/create_obj/<string:dat>', methods=['POST'])
# def create_obj(dat):
#    data = json.loads(dat)
#    create_object(data["name"], data["des"])
#    return data["name"]

@app.route('/objects', methods=['GET', 'POST'])
@login_required
def add_obj():
    form = ObjForm()
    if form.validate_on_submit():
        create_object(form.title.data, form.content.data)
        return redirect('/index')
    return render_template('obj.html', title='Добавление новости',
                           form=form)


@app.route('/add_reviev/<int:id_obj>', methods=['GET', 'POST'])
@login_required
def add_reviev(id_obj):
    form = RevForm()
    db_sess = create_session()
    if form.validate_on_submit():
        if form.raiting2 != 0:
            if form.raiting1.data / form.raiting2.data < 1 and form.raiting1.data / form.raiting2.data > 0:
                if db_sess.query(Review).filter(Review.user_id == current_user.id, Review.object_id == id_obj).first() == None:
                    create_review(form.content.data, current_user.get_id(), id_obj,
                                  round(form.raiting1.data / form.raiting2.data, 2))
                else:
                    return render_template('reviev.html', title='Добавление отзыва',
                                           form=form, message="Вы уже написали отзыв на это")
            else:
                return render_template('reviev.html', title='Добавление отзыва',
                                       form=form, message="Выставленный балл некорректен")
        return redirect('/index')
    return render_template('reviev.html', title='Добавление отзыва',
                           form=form)


@app.route('/profile/<int:id_user>')
@login_required
def profile(id_user):
    db_sess = create_session()
    user = db_sess.query(User).filter(User.id == id_user).first()
    return render_template('profile.html', title='Профиль', user=user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/news_delete/<int:id>&<int:id_obj>', methods=['GET', 'POST'])
@login_required
def news_delete(id, id_obj):
    db_sess = create_session()
    obj = db_sess.query(Object).filter(Object.id == id_obj).first()
    if obj.reviews_num != 1:
        db_sess.query(Object).filter(Object.id == id_obj).first().reviews_raiting = \
            (obj.reviews_raiting * obj.reviews_num - db_sess.query(Review).filter(
                Review.id == id).first().raiting) / obj.reviews_num
    else:
        db_sess.query(Object).filter(Object.id == id_obj).first().reviews_raiting = 0
    db_sess.query(Review).filter(Review.id == id).delete()
    db_sess.query(Object).filter(Object.id == id_obj).first().reviews_num -= 1
    name = db_sess.query(Object).filter(Object.id == id_obj).first().name
    db_sess.commit()
    return redirect(f'/watch_revievs/{name}')


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')
