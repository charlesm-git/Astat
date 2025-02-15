import csv
from datetime import date
from sqlalchemy import select, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from models.base import Base
from models.area import Area
from models.grade import Grade
from models.ascent import Ascent

GRADE_ASSOCIATION_DICT = {
    "6a": 1,
    "6a+": 2,
    "6b": 3,
    "6b+": 4,
    "6c": 5,
    "6c+": 6,
    "7a": 7,
    "7a+": 8,
    "7b": 9,
    "7b+": 10,
    "7c": 11,
    "7c+": 12,
    "8a": 13,
    "8a+": 14,
    "8b": 15,
    "8b+": 16,
    "8c": 17,
    "8c+": 18,
    "9a": 19,
}

db_path = "astat.db"

DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(DATABASE_URL, echo=False)

session_factory = sessionmaker(bind=engine)

Session = scoped_session(session_factory)


def load_ascents_to_csv():
    with Session() as session:
        ascents = session.execute(
            select(
                Ascent.name,
                Grade.grade_value,
                Ascent.ascent_date,
                Area.name,
            )
            .join(Area, Area.id == Ascent.area_id)
            .join(Grade, Grade.id == Ascent.grade_id)
        ).all()
        print(ascents)

    with open(
        "./ascents_export.csv", "w", encoding="utf-8", newline=""
    ) as export_file:
        writer = csv.writer(
            export_file,
            delimiter=";",
        )
        writer.writerows(ascents)


def load_ascents_from_csv():
    """Load ascents as a list of dictionaries"""
    with open("./ascents_import.csv", "r", encoding="utf-8") as boulders_file:
        ascents = csv.reader(boulders_file, delimiter=";")
        ascents_data = []
        for ascent in ascents:
            ascents_data.append(
                {
                    "name": ascent[0],
                    "grade": ascent[1],
                    "date": ascent[2],
                    "area": ascent[3],
                }
            )
    return ascents_data


def get_grades_as_object():
    """
    Create and return a list of Grade Objects to initialize the 'grade' table
    in the database
    """
    grades = []
    for grade_value, correspondence in GRADE_ASSOCIATION_DICT.items():
        grades.append(
            Grade(grade_value=grade_value, correspondence=correspondence)
        )
    return grades


def get_areas_as_objects(ascents):
    """
    Create and return a list of Area Objects to initialize the 'area' table
    in the database. The list is based on the .csv given as input.
    """
    areas = []
    for ascent in ascents:
        if ascent["area"] not in areas:
            areas.append(ascent["area"])
    areas_objects = []
    for area in areas:
        areas_objects.append(Area(name=area))
    return areas_objects


def get_ascents_as_object(ascents, session):
    """
    Create and return a list of Area Objects to initialize the 'ascent' table
    in the database. The list is based on the .csv given as input.
    """
    ascents_object_list = []
    for ascent in ascents:
        grade_id = session.scalar(
            select(Grade.id).where(Grade.grade_value == ascent["grade"])
        )
        area = ascent["area"]
        area_id = session.scalar(select(Area.id).where(Area.name == area))
        full_date = ascent["date"]
        day, month, year = full_date.split("/")
        ascents_object_list.append(
            Ascent(
                name=ascent["name"],
                grade_id=grade_id,
                area_id=area_id,
                ascent_date=date(int(year), int(month), int(day)),
            )
        )
    return ascents_object_list


def initialize_db():
    """Initialize the database from a .csv given as input"""
    ascents = load_ascents_from_csv()
    areas = get_areas_as_objects(ascents)
    grades = get_grades_as_object()

    with Session() as session:
        # Create all the tables
        Base.metadata.create_all(engine)
        # Initialize the 'area' and 'grade' tables
        session.add_all(areas)
        session.add_all(grades)
        session.commit()
        # Initialize the 'ascent' table based. Has to be done after the
        # initialisation of 'area' and 'grade' for foreign key references
        ascents = get_ascents_as_object(ascents, session)
        session.add_all(ascents)
        session.commit()


def initialize_empty_db():
    grades = get_grades_as_object()
    with Session() as session:
        Base.metadata.create_all(engine)

        session.add_all(grades)
        session.commit()


if __name__ == "__main__":
    # load_ascents_to_csv()
    initialize_db()
