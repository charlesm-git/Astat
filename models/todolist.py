from kivymd.app import MDApp

from typing import List
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
import models.grade
import models.todoclimb
import models.sector


class ToDoList(Base):
    __tablename__ = "todolist"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(32))

    # Relationship
    todoclimbs: Mapped[List["models.todoclimb.ToDoClimb"]] = relationship(
        back_populates="todolist"
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
            todolist = ToDoList(name=name)
            session.add(todolist)
            session.commit()
            session.refresh(todolist)
        return todolist

    def update(self, name):
        with MDApp.get_running_app().get_db_session() as session:
            updated_todolist = session.merge(self)
            updated_todolist.name = name
            session.commit()
            session.refresh(updated_todolist)
            self.name = updated_todolist.name
