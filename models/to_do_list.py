from datetime import datetime, date

from kivymd.app import MDApp

from typing import Optional, List
from sqlalchemy import ForeignKey, Integer, String, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from models.base import Base
import models.grade
import models.climb_to_do
import models.sector


class ToDoList(Base):
    __tablename__ = "todolist"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(32))

    # Relationship
    climbs_to_do: Mapped[List["models.climb_to_do.ClimbToDo"]] = (
        relationship(back_populates="todolist")
    )
    sectors: Mapped[List["models.sector.Sector"]] = relationship(
        back_populates="todolist"
    )

    def __repr__(self):
        return f"<{self.name}>"

    @classmethod
    def delete(cls, id):
        with MDApp.get_running_app().get_db_session() as session:
            ascent_to_delete = session.get(cls, id)
            session.delete(ascent_to_delete)
            session.commit()

    @classmethod
    def create(cls, name):
        with MDApp.get_running_app().get_db_session() as session:
            session.add(
                ToDoList(
                    name=name,
                )
            )
            session.commit()

    def update(self, name):
        with MDApp.get_running_app().get_db_session() as session:
            updated_ascent = session.merge(self)
            session.commit()
