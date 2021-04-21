import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm


class Chat_Message(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'chats_messages'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, index=True)
    message_id = sqlalchemy.Column(sqlalchemy.Integer)