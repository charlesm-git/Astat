import csv
from datetime import date
from sqlalchemy import select

from models.base import Base
from models.area import Area
from models.grade import Grade
from models.ascent import Ascent
from .database import Session, engine

GRADE_ASSOCIATION_DICT = {
    "6a": 1,
    "6b": 2,
    "6b+": 3,
    "6c": 4,
    "6c+": 5,
    "7a": 6,
    "7a+": 7,
    "7b": 8,
    "7b+": 9,
    "7c": 10,
    "7c+": 11,
    "8a": 12,
    "8a+": 13,
    "8b": 14,
    "8b+": 15,
    "8c": 16,
    "8c+": 17,
}


def load_ascents_from_csv():
    """Load ascents as a list of dictionaries"""
    with open("./boulders_input.csv", "r", encoding="utf-8") as boulders_file:
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
        grade = ascent["grade"]
        grade_id = session.scalar(
            select(Grade).where(Grade.grade_value == grade)
        ).id
        area = ascent["area"]
        area_id = session.scalar(select(Area).where(Area.name == area)).id
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
