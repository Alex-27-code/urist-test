from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Optional


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    name = StringField('ФИО', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    role = SelectField('Тип аккаунта', choices=[
        ('client', 'Клиент — ищу юриста'),
        ('lawyer', 'Юрист — предоставляю услуги'),
    ], validators=[DataRequired()])
    specialty = StringField('Специализация', validators=[Optional()])
    experience = StringField('Опыт работы', validators=[Optional()])
    price = StringField('Стоимость', validators=[Optional()])
    schedule = StringField('График работы', validators=[Optional()])
    about = TextAreaField('О себе', validators=[Optional()])
    photo = FileField('Фото профиля', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], '')])
    submit = SubmitField('Зарегистрироваться')


class LawyerProfileForm(FlaskForm):
    name = StringField('ФИО', validators=[DataRequired()])
    specialty = StringField('Специализация', validators=[Optional()])
    about = TextAreaField('О себе', validators=[Optional()])
    experience = StringField('Опыт работы', validators=[Optional()])
    price = StringField('Стоимость консультации', validators=[Optional()])
    schedule = StringField('Удобное время', validators=[Optional()])
    photo = FileField('Фото профиля', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], '')])
    submit = SubmitField('Сохранить изменения')