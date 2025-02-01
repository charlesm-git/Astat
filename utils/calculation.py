from sqlalchemy import func, extract

from database.database import Session
from models.area import Area
from models.ascent import Ascent
from models.grade import Grade


def get_total_ascent():
    """
    Get the total number of logged ascents
    :return: the total number as an int
    """
    with Session() as session:
        result = session.query(func.count(Ascent.id)).first()
    return result[0]


def get_ascent_per_area():
    """
    Get the number of ascent per area
    :return: a list of tuple with format : (number_of_ascent, area)
    """
    with Session() as session:
        result = (
            session.query(Area.name, func.count(Ascent.id))
            .join(Ascent, Area.id == Ascent.area_id)
            .group_by(Area.name)
            .order_by(func.count(Ascent.id).desc())
            .all()
        )
    return result


def get_ascent_per_grade():
    """
    Get the number of ascent per grade
    :return: a list of tuple with format : (number_of_ascent, grade)
    """
    with Session() as session:
        result = (
            session.query(Grade.grade_value, func.count(Ascent.id))
            .join(Ascent, Grade.id == Ascent.grade_id)
            .group_by(Grade.grade_value)
            .order_by(Grade.correspondence)
            .all()
        )
    return result


def get_ascent_per_year():
    """
    Get the number of ascent per year
    :return: a list of tuple with format : (number_of_ascent, year)
    """
    with Session() as session:
        result = (
            session.query(
                extract("year", Ascent.ascent_date).label("year"),
                func.count(Ascent.id),
            )
            .group_by("year")
            .order_by("year")
            .all()
        )
    return result
