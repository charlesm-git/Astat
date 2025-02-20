from typing import Optional, List

from kivymd.app import MDApp

from sqlalchemy import Integer, SmallInteger, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
import models.ascent
import models.todoclimb


class Grade(Base):
    __tablename__ = "grade"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    grade_value: Mapped[str] = mapped_column(String(3))
    correspondence: Mapped[int] = mapped_column(SmallInteger)

    # relationship
    ascents: Mapped[List["models.ascent.Ascent"]] = relationship(
        back_populates="grade"
    )

    todoclimbs: Mapped[List["models.todoclimb.ToDoClimb"]] = relationship(
        back_populates="grade"
    )

    def __repr__(self):
        return f"<Grade : {self.grade_value}, {self.correspondence}>"

    @classmethod
    def get_grade_value_from_correspondence(cls, grade_correspondence):
        with MDApp.get_running_app().get_db_session() as session:
            grade = session.scalar(
                select(Grade.grade_value).where(
                    Grade.correspondence == grade_correspondence
                )
            )
        return grade
