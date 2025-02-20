from typing import Optional, List
from sqlalchemy import Integer, String, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kivymd.app import MDApp

from models.base import Base
import models.todoclimb
import models.todolist


class Sector(Base):
    __tablename__ = "sector"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(32))
    todolist_id: Mapped[int] = mapped_column(
        ForeignKey("todolist.id", ondelete="CASCADE", onupdate="CASCADE"),
    )

    # relationship

    todolist: Mapped["models.todolist.ToDoList"] = relationship(
        "ToDoList", back_populates="sectors"
    )
    todoclimbs: Mapped[Optional[List["models.todoclimb.ToDoClimb"]]] = (
        relationship(back_populates="sector")
    )

    def __repr__(self):
        return f"<Area : name={self.name}>"

    @classmethod
    def create(cls, name, todolist_id):
        with MDApp.get_running_app().get_db_session() as session:
            sector_created = Sector(name=name, todolist_id=todolist_id)
            session.add(sector_created)
            session.commit()
            session.refresh(sector_created)
        return sector_created

    @classmethod
    def delete(cls, id):
        """Delete an Area and all associated ascents"""
        with MDApp.get_running_app().get_db_session() as session:
            sector_to_delete = session.get(Sector, id)
            if sector_to_delete:
                # Manual delete of all associated climbs because not handled
                # by SQLite
                ascents_to_delete = session.scalars(
                    select(models.todoclimb.ToDoClimb).where(
                        models.todoclimb.ToDoClimb.sector_id
                        == sector_to_delete.id
                    )
                ).all()

                for ascent in ascents_to_delete:
                    session.delete(ascent)

                session.delete(sector_to_delete)
                session.commit()
