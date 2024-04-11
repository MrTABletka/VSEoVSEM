from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired


class RevForm(FlaskForm):
    content = TextAreaField("Содержание")
    raiting1 = IntegerField('Сколько баллов?')
    raiting2 = IntegerField('Из скольки?')
    submit = SubmitField('Опубликовать')