from sqlalchemy import String, Integer, ForeignKey, Column, Table
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin

association_table = Table('association', SqlAlchemyBase.metadata,  # промежуточная таблица категорий работ
                          Column('jobs', Integer,
                                 ForeignKey('jobs.id')),
                          Column('category', Integer,
                                 ForeignKey('category.id'))
                          )


class Category(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True,  # id
                autoincrement=True)
    name = Column(String, nullable=False)  # наименование категории
