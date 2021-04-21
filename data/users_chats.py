import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm


class User_Chat(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'users_chats'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, index=True)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer)
