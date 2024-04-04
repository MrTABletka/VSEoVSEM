import sqlalchemy
import sqlalchemy.orm as orm
import datetime
import hashlib
import json
from sqlalchemy.orm import Session

SqlAlchemyBase = orm.declarative_base()

__factory = None

def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sqlalchemy.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)


    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()


def create_user(name, email, password):
    user = User()
    user.name = name
    salt = 'salt'.encode()
    user.hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 1000)
    user.email = email
    db_sess = create_session()
    db_sess.add(user)
    db_sess.commit()


def create_review(text, user_id, object_id, raiting):
    review = Review()
    review.text = text
    review.user_id = user_id
    review.object_id = object_id
    review.raiting = raiting
    db_sess = create_session()
    db_sess.add(review)
    user = db_sess.query(User).filter(User.id == user_id).first()
    user.reviews_raiting = (user.reviews_raiting * user.reviews_num + raiting) / (user.reviews_num + 1)
    user.reviews_num += 1
    db_sess.commit()


def create_object(name, description):
    object = Object()
    object.name = name
    object.description = description
    db_sess = create_session()
    db_sess.add(object)
    db_sess.commit()


def info_user(email):
    db_sess = create_session()
    user = db_sess.query(User).filter(User.email == email).first()
    answer = {"name": user.name,
              "email": user.email,
              "reviev_num": user.reviews_num,
              "reviews_raiting": user.reviews_raiting}
    return json.dumps(answer)


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    role = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    reviews_num = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    reviews_raiting = sqlalchemy.Column(sqlalchemy.Float, default=0)

class Review(SqlAlchemyBase):
    __tablename__ = 'reviews'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    object_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("objects.id"))
    raiting = sqlalchemy.Column(sqlalchemy.Float)
    user = orm.relationship('User')
    object = orm.relationship('Object')


class Object(SqlAlchemyBase):
    __tablename__ = 'objects'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    reviews_num = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    reviews_raiting = sqlalchemy.Column(sqlalchemy.Float, default=0)


global_init("data/base.sqlite3")
print(info_user('bimba'))