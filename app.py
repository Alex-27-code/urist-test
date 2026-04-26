import datetime
import os
from flask import Flask, render_template, redirect, request, flash, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField, SelectField, FileField
from wtforms.validators import DataRequired, Email, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from backend.database import global_init, create_session, SqlAlchemyBase
from backend.database.models.users_model import UserModel
from backend.database.models.booking_model import BookingModel
from backend.database.models.settings_model import SettingsModel
import backend.database.default_data as dd
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.unauthorized_handler
def unauthorized():
    from flask import redirect, flash
    flash('Войдите для доступа', 'warning')
    return redirect('/login')


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    user = db_sess.get(UserModel, int(user_id))
    if not user:
        return None
    return user


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
    photo = FileField('Фото профиля', validators=[Optional()])
    submit = SubmitField('Зарегистрироваться')


class ProfileForm(FlaskForm):
    name = StringField('ФИО', validators=[DataRequired()])
    specialty = StringField('Специализация', validators=[Optional()])
    about = TextAreaField('О себе', validators=[Optional()])
    experience = StringField('Опыт работы', validators=[Optional()])
    price = StringField('Стоимость консультации', validators=[Optional()])
    schedule = StringField('Удобное время', validators=[Optional()])
    photo = FileField('Фото профиля', validators=[Optional()])
    submit = SubmitField('Сохранить')


@app.route('/')
def index():
    db_sess = create_session()
    lawyers = []
    settings = db_sess.get(SettingsModel, 1)
    if current_user.is_authenticated:
        lawyers = db_sess.query(UserModel).filter(UserModel.role == 'lawyer').all()
    return render_template('index.html', lawyers=lawyers, settings=settings)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = create_session()
        user = db_sess.query(UserModel).filter(UserModel.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', form=form, message='Неправильный логин или пароль')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', form=form, message='Пароли не совпадают')
        db_sess = create_session()
        if db_sess.query(UserModel).filter(UserModel.email == form.email.data).first():
            return render_template('register.html', form=form, message='Пользователь с такой почтой уже существует')
        user = UserModel(
            name=form.name.data,
            email=form.email.data,
            role=form.role.data,
            specialty=form.specialty.data or '',
            experience=form.experience.data or '',
            price=form.price.data or '',
            schedule=form.schedule.data or '',
            about=form.about.data or '',
        )
        if form.photo.data:
            f = form.photo.data
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user.photo = filename
        user.set_password(form.password.data)
        db_sess.add(user)
        try:
            db_sess.commit()
        except IntegrityError:
            db_sess.rollback()
            return render_template('register.html', form=form, message='Пользователь с такой почтой уже существует')
        return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/lawyer/<int:lawyer_id>', methods=['GET', 'POST'])
@login_required
def lawyer_profile(lawyer_id):
    db_sess = create_session()
    lawyer = db_sess.get(UserModel, lawyer_id)
    if not lawyer or lawyer.role != 'lawyer':
        return redirect('/')
    slots = [f"{str(h).zfill(2)}:{str(m).zfill(2)}" for h in range(9, 19) for m in (0, 30) if not (h == 18 and m == 30)]
    bookings = db_sess.query(BookingModel).filter(BookingModel.lawyer_id == lawyer_id).all()
    booked_slots = {}  # {date: [times]}
    for b in bookings:
        if b.status != 'rejected' and b.date:
            if b.date not in booked_slots:
                booked_slots[b.date] = []
            booked_slots[b.date].append(b.time)
    message = None
    if request.method == 'POST' and current_user.role == 'client':
        time = request.form.get('time')
        problem = request.form.get('problem')
        date = request.form.get('date')
        if time and problem and time not in booked_slots.get(date, []):
            booking = BookingModel(client_id=current_user.id, lawyer_id=lawyer.id, date=date or '', time=time, problem=problem, status='pending')
            db_sess.add(booking)
            db_sess.commit()
            if date not in booked_slots:
                booked_slots[date] = []
            booked_slots[date].append(time)
            message = 'Заявка отправлена! Ожидайте подтверждения.'
        elif time in booked_slots.get(date, []):
            message = 'Это время уже занято.'
    selected_date = request.form.get('date', '') or datetime.date.today().isoformat()
    return render_template('lawyer_profile.html', lawyer=lawyer, slots=slots, booked_slots=booked_slots, selected_date=selected_date, message=message, can_book=(current_user.role == 'client'), min_date=datetime.date.today().isoformat())


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.role != 'lawyer':
        return redirect('/')
    form = ProfileForm()
    if form.validate_on_submit():
        db_sess = create_session()
        user = db_sess.get(UserModel, current_user.id)
        user.name = form.name.data
        user.specialty = form.specialty.data or ''
        user.about = form.about.data or ''
        user.experience = form.experience.data or ''
        user.price = form.price.data or ''
        user.schedule = form.schedule.data or ''
        if form.photo.data:
            filename = secure_filename(form.photo.data.filename)
            form.photo.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user.photo = filename
        db_sess.commit()
        flash('Профиль обновлён', 'success')
        return redirect('/')
    form.name.data = current_user.name
    form.specialty.data = current_user.specialty or ''
    form.about.data = current_user.about or ''
    form.experience.data = current_user.experience or ''
    form.price.data = current_user.price or ''
    form.schedule.data = current_user.schedule or ''
    return render_template('profile.html', form=form)


@app.route('/clients_department', methods=['GET', 'POST'])
@login_required
def clients_department():
    if current_user.role != 'admin':
        return redirect('/')
    db_sess = create_session()
    bookings = db_sess.query(BookingModel).order_by(BookingModel.id.desc()).all()
    return render_template('clients_department.html', bookings=bookings)


@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    if current_user.role != 'admin':
        return redirect('/')
    db_sess = create_session()
    users = db_sess.query(UserModel).all()
    return render_template('admin_users.html', users=users)


@app.route('/booking_action/<int:booking_id>/<action>', methods=['GET', 'POST'])
@login_required
def booking_action(booking_id, action):
    if current_user.role != 'admin':
        return redirect('/')
    db_sess = create_session()
    booking = db_sess.get(BookingModel, booking_id)
    if booking and action in ('accept', 'reject'):
        booking.status = action
        db_sess.commit()
    return redirect('/clients_department')


@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if current_user.role != 'admin':
        return redirect('/')
    db_sess = create_session()
    settings = db_sess.get(SettingsModel, 1)
    if not settings:
        settings = SettingsModel(id=1)
        db_sess.add(settings)
        db_sess.commit()
    if request.method == 'POST':
        settings.about_text = request.form.get('about_text', '')
        settings.contact_text = request.form.get('contact_text', '')
        settings.phone = request.form.get('phone', '')
        settings.address = request.form.get('address', '')
        db_sess.commit()
        flash('Настройки сохранены!', 'success')
        return redirect('/admin/settings')
    return render_template('admin_settings.html', settings=settings)


@app.route('/admin/user/<int:user_id>/delete', methods=['GET'])
@login_required
def admin_delete_user(user_id):
    if current_user.role != 'admin':
        return redirect('/')
    db_sess = create_session()
    user = db_sess.get(UserModel, user_id)
    if user and user.id != current_user.id:
        db_sess.delete(user)
        db_sess.commit()
    return redirect('/users')


@app.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    if current_user.role != 'admin':
        return redirect('/')
    db_sess = create_session()
    user = db_sess.get(UserModel, user_id)
    if not user:
        return redirect('/users')
    if request.method == 'POST':
        user.name = request.form.get('name', '')
        user.specialty = request.form.get('specialty', '')
        user.experience = request.form.get('experience', '')
        user.price = request.form.get('price', '')
        user.schedule = request.form.get('schedule', '')
        user.about = request.form.get('about', '')
        db_sess.commit()
        flash('Профиль обновлён!', 'success')
        return redirect('/users')
    return render_template('admin_edit_user.html', user=user)


@app.route('/admin/booking/<int:booking_id>/delete', methods=['GET'])
@login_required
def admin_delete_booking(booking_id):
    if current_user.role != 'admin':
        return redirect('/')
    db_sess = create_session()
    booking = db_sess.get(BookingModel, booking_id)
    if booking:
        db_sess.delete(booking)
        db_sess.commit()
    return redirect('/clients_department')


def main():
    global_init('data/urist.db')
    default_data.default_data()
    port = int(os.getenv('FLASK_PORT', 80))
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    app.run(port=port, host=host, debug=False)


if __name__ == '__main__':
    main()