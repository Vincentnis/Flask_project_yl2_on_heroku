from sqlalchemy import String, Integer, ForeignKey, Column, Table, DateTime, orm
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
import datetime


class Message(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True,  # id
                autoincrement=True)
    sender = Column(Integer, ForeignKey('users.id'), nullable=False)  # id отправителя
    receiver = Column(Integer, nullable=False)  # id получателя
    text = Column(String, nullable=False)  # текст сообщения
    date = Column(DateTime, default=datetime.datetime.now())  # время создания
    user = orm.relation("User")  # чвязь с таблицей users
