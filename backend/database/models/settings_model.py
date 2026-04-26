import sqlalchemy
from backend.database.db_session import SqlAlchemyBase


class SettingsModel(SqlAlchemyBase):
    __tablename__ = 'settings'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    about_text = sqlalchemy.Column(sqlalchemy.String, default='Мы предоставляем профессиональные юридические услуги.')
    contact_text = sqlalchemy.Column(sqlalchemy.String, default='Контакты')
    phone = sqlalchemy.Column(sqlalchemy.String, default='+7 (999) 123-45-67')
    address = sqlalchemy.Column(sqlalchemy.String, default='Москва, ул. Примерная, д.1')
