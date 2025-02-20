from kivymd.app import MDApp

from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    @classmethod
    def get_from_id(cls, id):
        with MDApp.get_running_app().get_db_session() as session:
            obj = session.get(cls, id)
        return obj
