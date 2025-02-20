from typing import Optional, List
from sqlalchemy import Integer, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kivymd.app import MDApp

from models.base import Base
import models.ascent


class Area(Base):
    __tablename__ = "area"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(32))

    # relationship
    ascents: Mapped[Optional[List["models.ascent.Ascent"]]] = relationship(
        back_populates="area"
    )

    def __repr__(self):
        return f"<Area : name={self.name}>"

    @classmethod
    def create(cls, name):
        with MDApp.get_running_app().get_db_session() as session:
            area_created = Area(name=name)
            session.add(area_created)
            session.commit()
            session.refresh(area_created)
        return area_created

    @classmethod
    def delete(cls, id):
        """Delete an Area and all associated ascents"""
        with MDApp.get_running_app().get_db_session() as session:
            area_to_delete = session.get(Area, id)
            if area_to_delete:
                # Manual delete of all associated ascents because not handled
                # by SQLite
                ascents_to_delete = session.scalars(
                    select(models.ascent.Ascent).where(
                        models.ascent.Ascent.area_id == area_to_delete.id
                    )
                ).all()

                for ascent in ascents_to_delete:
                    session.delete(ascent)

                session.delete(area_to_delete)
                session.commit()
