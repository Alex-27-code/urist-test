import sqlalchemy
from backend.database.db_session import SqlAlchemyBase


class BookingModel(SqlAlchemyBase):
    __tablename__ = 'bookings'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    client_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    lawyer_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    date = sqlalchemy.Column(sqlalchemy.String)
    time = sqlalchemy.Column(sqlalchemy.String)
    problem = sqlalchemy.Column(sqlalchemy.String)
    status = sqlalchemy.Column(sqlalchemy.String, default='pending')

    client = sqlalchemy.orm.relationship('UserModel', foreign_keys=[client_id])
    lawyer = sqlalchemy.orm.relationship('UserModel', foreign_keys=[lawyer_id])
