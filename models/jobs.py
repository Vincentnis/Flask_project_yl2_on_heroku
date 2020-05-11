import datetime
from data.db_session import SqlAlchemyBase
from sqlalchemy import orm, String, Integer, ForeignKey, Column, DateTime
from sqlalchemy_serializer import SerializerMixin


class Jobs(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)  # id
    author = Column(Integer, ForeignKey("users.id"))  # id автора
    header = Column(String, nullable=False)  # заголовок
    requirements = Column(String, nullable=False)  # требования
    description = Column(String, nullable=False)  # описание
    creation_date = Column(DateTime, default=datetime.datetime.now())  # время создания
    user = orm.relation("User")  # связь с таблицой users
    categories = orm.relation("Category",  # ассоциативная связь с таблицой category
                              secondary="association",
                              backref="jobs")
