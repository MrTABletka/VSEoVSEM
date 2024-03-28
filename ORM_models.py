import sqlalchemy
import sqlalchemy.orm as orm
import datetime
import hashlib
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


def create_review(text, user_id, raiting):
    review = Review()
    review.text = text
    review.user_id = user_id
    review.raiting = raiting
    db_sess = create_session()
    db_sess.add(review)
    user = db_sess.query(User).filter(User.id == user_id).first()
    user.reviews_num += 1
    db_sess.commit()


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
    raiting = sqlalchemy.Column(sqlalchemy.Float)
    user = orm.relationship('User')

global_init("data/base.sqlite3")
create_user('Bob', 'bimba', '123')
create_user('Bob', 'bimba2', '123')
create_review('nice', 1, 0.2)
create_review('nice', 2, 0.7)
