from typing import Optional, List
from sqlalchemy import Integer, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Session
from models.base import Base
from models.ascent import Ascent
import models.ascent


class Area(Base):
    __tablename__ = "area"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(64))

    # relationship
    ascents: Mapped[Optional[List["models.ascent.Ascent"]]] = relationship(
        back_populates="area"
    )

    def __repr__(self):
        return f"<Area : name={self.name}>"

    @classmethod
    def create(cls, name):
        with Session() as session:
            session.add(Area(name=name))
            session.commit()

    @classmethod
    def delete(cls, area_name):
        """Delete an Area and all associated ascents"""
        with Session() as session:
            area_to_delete = session.scalar(
                select(Area).where(Area.name == area_name)
            )
            if area_to_delete:
                # Manual delete of all associated ascents because not handled
                # by SQLite
                ascents_to_delete = session.scalars(
                    select(Ascent).where(Ascent.area_id == area_to_delete.id)
                ).all()

                for ascent in ascents_to_delete:
                    session.delete(ascent)

                session.delete(area_to_delete)
                session.commit()
