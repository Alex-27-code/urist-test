from backend.database import create_session
from backend.database.models.users_model import UserModel


def default_data():
    db_sess = create_session()
    if not db_sess.query(UserModel).filter(UserModel.email == "admin@mail.ru").first():
        admin = UserModel()
        admin.email = "admin@mail.ru"
        admin.name = "Администратор"
        admin.set_password("admin")
        admin.role = "admin"
        db_sess.add(admin)

    if not db_sess.query(UserModel).filter(UserModel.email == "smirnov@lawyer.ru").first():
        u = UserModel()
        u.email = "smirnov@lawyer.ru"
        u.name = "Алексей Смирнов"
        u.set_password("123")
        u.role = "lawyer"
        u.specialty = "Гражданское право"
        u.experience = "8 лет"
        u.price = "2500 р/час"
        u.schedule = "Пн-Пт 9:00-18:00"
        u.about = "Опытный юрист по гражданским делам"
        db_sess.add(u)

    if not db_sess.query(UserModel).filter(UserModel.email == "vasilyeva@lawyer.ru").first():
        u = UserModel()
        u.email = "vasilyeva@lawyer.ru"
        u.name = "Елена Васильева"
        u.set_password("123")
        u.role = "lawyer"
        u.specialty = "Семейное право"
        u.experience = "5 лет"
        u.price = "2000 р/час"
        u.schedule = "Пн-Сб 10:00-17:00"
        u.about = "Специалист по семейному праву"
        db_sess.add(u)

    db_sess.commit()