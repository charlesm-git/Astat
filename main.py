from datetime import date
from database import Session, engine
from models.base import Base
from models.ascent import Ascent
from models.area import Area
from models.grade import Grade


if __name__ == "__main__":
    with Session() as session:
        Base.metadata.create_all(engine)
        session.add(Area(name="Fontainebleau"))
        session.add(Grade(grade_value="8a", correspondance=11))
        session.add(
            Ascent(
                name="Furtif",
                grade_id=1,
                area_id=1,
                ascent_date=date(2022, 2, 25),
            )
        )
        session.commit()
