from datetime import datetime, date

from kivymd.app import MDApp

from sqlalchemy import Boolean, ForeignKey, Integer, String, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from models.base import Base
import models.area
import models.grade


class Ascent(Base):
    __tablename__ = "ascent"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(64))
    grade_id: Mapped[int] = mapped_column(
        ForeignKey("grade.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    area_id: Mapped[int] = mapped_column(
        ForeignKey("area.id", ondelete="CASCADE", onupdate="CASCADE")
    )
    ascent_date: Mapped[date] = mapped_column(Date)
    flash: Mapped[bool] = mapped_column(Boolean, default=False)
    note: Mapped[str] = mapped_column(String(3000), default="")
    date_created: Mapped[datetime] = mapped_column(
        DateTime, default=func.now()
    )
    date_updated: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    # Relationship
    grade: Mapped["models.grade.Grade"] = relationship(
        "Grade", back_populates="ascents"
    )
    area: Mapped["models.area.Sector"] = relationship(
        "Area", back_populates="ascents"
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
    def create(cls, name, grade_id, area_id, ascent_date, flash, note):
        with MDApp.get_running_app().get_db_session() as session:
            session.add(
                Ascent(
                    name=name,
                    grade_id=grade_id,
                    area_id=area_id,
                    ascent_date=ascent_date,
                    note=note,
                    flash=flash,
                )
            )
            session.commit()

    def update(self, name, grade_id, area_id, ascent_date, flash, note):
        with MDApp.get_running_app().get_db_session() as session:
            updated_ascent = session.merge(self)
            updated_ascent.name = name
            updated_ascent.grade_id = grade_id
            updated_ascent.area_id = area_id
            updated_ascent.ascent_date = ascent_date
            updated_ascent.flash = flash
            updated_ascent.note = note
            session.commit()
