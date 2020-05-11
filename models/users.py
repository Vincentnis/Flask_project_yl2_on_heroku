import datetime
from data.db_session import SqlAlchemyBase
from sqlalchemy import orm, String, Integer, DateTime, Column
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)  # id
    surname = Column(String, nullable=False)  # фамилия
    name = Column(String, nullable=False)  # имя
    age = Column(Integer, nullable=False)  # возраст
    speciality = Column(String, nullable=False)  # специализация, отрасль
    about = Column(String, nullable=True)  # описание
    email = Column(String, index=True, unique=True)  # почта - уникальна
    hashed_password = Column(String, nullable=False)  # захешированный пароль(кодируется sha256)
    avatar_url = Column(String, nullable=True)  # url к аватарке пользователя
    created_date = Column(DateTime, default=datetime.datetime.now())  # время создания аккаунта
    job = orm.relation("Jobs", back_populates='user')  # связь с таблицой jobs
    message = orm.relation("Message", back_populates='user')  # связь с таблицой messages
    """Чаты. Парсер чатов = ';', парсер элементов представления чата = ', ' 
    --> 'receiver_id, message_id;receiver1_id, message1_id'. Пример: '2, 6; 1, 5' 
    значит что, у данного пользователя есть чаты с пользователями 2 и 1(по id), последние сообщения в них 6 и 5(по id)"""
    chats = Column(String, default='')

    def set_password(self, password):  # захешировать пароль
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):  # сверить пароль
        return check_password_hash(self.hashed_password, password)
