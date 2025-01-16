from typing import Optional, List
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
import models.ascent

class Area(Base):
    __tablename__ = "area"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(64))

    # relationship
    ascents: Mapped[Optional[List["models.ascent.Ascent"]]] = relationship(back_populates="area")

    def __repr__(self):
        return f"<Area : name={self.name}>"