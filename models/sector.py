from typing import Optional, List
from sqlalchemy import Integer, String, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kivymd.app import MDApp

from models.base import Base
import models.climb_to_do
import models.to_do_list


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

    todolist: Mapped["models.to_do_list.ToDoList"] = relationship(
        "ToDoList", back_populates="sectors"
    )
    climbs_to_do: Mapped[Optional[List["models.climb_to_do.ClimbToDo"]]] = (
        relationship(back_populates="sector")
    )

    def __repr__(self):
        return f"<Area : name={self.name}>"

    @classmethod
    def create(cls, name):
        with MDApp.get_running_app().get_db_session() as session:
            session.add(Sector(name=name))
            session.commit()

    # @classmethod
    # def delete(cls, area_name):
    #     """Delete an Area and all associated ascents"""
    #     with MDApp.get_running_app().get_db_session() as session:
    #         area_to_delete = session.scalar(
    #             select(Sector).where(Sector.name == area_name)
    #         )
    #         if area_to_delete:
    #             # Manual delete of all associated ascents because not handled
    #             # by SQLite
    #             ascents_to_delete = session.scalars(
    #                 select(models.ascent.Ascent).where(
    #                     models.ascent.Ascent.area_id == area_to_delete.id
    #                 )
    #             ).all()

    #             for ascent in ascents_to_delete:
    #                 session.delete(ascent)

    #             session.delete(area_to_delete)
    #             session.commit()
