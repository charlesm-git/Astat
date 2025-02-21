from datetime import datetime

from kivymd.app import MDApp

from typing import Optional
from sqlalchemy import ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from models.base import Base
import models.grade
import models.sector
import models.todolist


class ToDoClimb(Base):
    __tablename__ = "todoclimb"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(64))
    tag: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    grade_id: Mapped[int] = mapped_column(
        ForeignKey("grade.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    sector_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("sector.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    todolist_id: Mapped[int] = mapped_column(
        ForeignKey("todolist.id", ondelete="CASCADE", onupdate="CASCADE")
    )

    note: Mapped[str] = mapped_column(String(3000), default="")

    date_created: Mapped[datetime] = mapped_column(
        DateTime, default=func.now()
    )
    date_updated: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    # Relationship
    grade: Mapped["models.grade.Grade"] = relationship(
        "Grade", back_populates="todoclimbs"
    )
    sector: Mapped[Optional["models.sector.Sector"]] = relationship(
        "Sector", back_populates="todoclimbs"
    )
    todolist: Mapped["models.to_do_list.ToDoList"] = relationship(
        "ToDoList", back_populates="todoclimbs"
    )

    def __repr__(self):
        return f"<{self.name}>"

    @classmethod
    def delete(cls, id):
        with MDApp.get_running_app().get_db_session() as session:
            climb_to_delete = session.get(cls, id)
            session.delete(climb_to_delete)
            session.commit()

    @classmethod
    def create(
        cls, name, grade_id, todolist_id, note, sector_id=None, tag=None
    ):
        with MDApp.get_running_app().get_db_session() as session:
            session.add(
                ToDoClimb(
                    name=name,
                    grade_id=grade_id,
                    todolist_id=todolist_id,
                    note=note,
                    sector_id=sector_id,
                    tag=tag,
                )
            )
            session.commit()

    def update(self, name, grade_id, sector_id, note, tag):
        with MDApp.get_running_app().get_db_session() as session:
            updated_ascent = session.merge(self)
            updated_ascent.name = name
            updated_ascent.grade_id = grade_id
            updated_ascent.sector_id = sector_id
            updated_ascent.note = note
            updated_ascent.tag = tag
            session.commit()
