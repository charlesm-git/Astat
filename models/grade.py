from typing import Optional, List
from sqlalchemy import Integer, SmallInteger, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from database.database import Session
import models.ascent


class Grade(Base):
    __tablename__ = "grade"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    grade_value: Mapped[str] = mapped_column(String(3))
    correspondence: Mapped[int] = mapped_column(SmallInteger)

    # relationship
    ascents: Mapped[Optional[List["models.ascent.Ascent"]]] = relationship(
        back_populates="grade"
    )

    def __repr__(self):
        return f"<Grade : {self.grade_value}, {self.correspondence}>"

    @classmethod
    def get_grade_value_from_correspondence(cls, grade_correspondence):
        with Session() as session:
            grade = session.scalar(
                select(Grade.grade_value).where(
                    Grade.correspondence == grade_correspondence
                )
            )
        return grade
