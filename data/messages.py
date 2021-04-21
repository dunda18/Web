import sqlalchemy
import datetime
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm


class Message(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'messages'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    send_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                  default=datetime.datetime.now, nullable=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
    chat_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("chats.id"))
    chat = orm.relation('Chat')