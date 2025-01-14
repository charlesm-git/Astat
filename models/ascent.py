from sqlalchemy import ForeignKey, Integer, String, DateTime, Date, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime, date

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
        ForeignKey("area.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    ascent_date: Mapped[date] = mapped_column(Date)
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
    area: Mapped["models.area.Area"] = relationship(
        "Area", back_populates="ascents"
    )
