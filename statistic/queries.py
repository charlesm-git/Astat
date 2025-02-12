from sqlalchemy import func, extract, desc, select

from database.database import Session
from models.area import Area
from models.ascent import Ascent
from models.grade import Grade


def get_total_ascent(
    min_grade_correspondence=1, max_grade_correpondence=19, area="All"
):
    """
    Get the total number of logged ascents
    :return: the total number as an int
    """
    with Session() as session:
        query = (
            session.query(func.count(Ascent.id))
            .join(Grade, Grade.id == Ascent.grade_id)
            .join(Area, Area.id == Ascent.area_id)
            .filter(
                Grade.correspondence >= min_grade_correspondence,
                Grade.correspondence <= max_grade_correpondence,
            )
        )

        if area != "All":
            query = query.filter(Area.name == area)

        result = query.first()

    return result[0]


def get_ascents_per_area(
    min_grade_correspondence=1, max_grade_correpondence=19, area="All"
):
    """
    Get the number of ascent per area
    :return: a list of tuple with format : (number_of_ascent, area)
    """
    with Session() as session:
        query = (
            session.query(Area.name, func.count(Ascent.id))
            .join(Ascent, Area.id == Ascent.area_id)
            .join(Grade, Grade.id == Ascent.grade_id)
            .filter(
                Grade.correspondence >= min_grade_correspondence,
                Grade.correspondence <= max_grade_correpondence,
            )
        )

        if area != "All":
            query = query.filter(Area.name == area)

        result = (
            query.group_by(Area.name)
            .order_by(func.count(Ascent.id).desc())
            .all()
        )
    return result


def get_ascents_per_grade(
    min_grade_correspondence=1, max_grade_correpondence=19, area="All"
):
    """
    Get the number of ascent per grade
    :return: a list of tuple with format : (number_of_ascent, grade)
    """
    with Session() as session:
        query = (
            session.query(Grade.grade_value, func.count(Ascent.id))
            .join(Ascent, Grade.id == Ascent.grade_id)
            .join(Area, Area.id == Ascent.area_id)
            .filter(
                Grade.correspondence >= min_grade_correspondence,
                Grade.correspondence <= max_grade_correpondence,
            )
        )

        if area != "All":
            query = query.filter(Area.name == area)

        result = (
            query.group_by(Grade.grade_value)
            .order_by(desc(Grade.correspondence))
            .all()
        )
    return result


def get_ascents_per_year(
    min_grade_correspondence=1, max_grade_correpondence=19, area="All"
):
    """
    Get the number of ascent per year
    :return: a list of tuple with format : (number_of_ascent, year)
    """
    with Session() as session:
        query = (
            session.query(
                extract("year", Ascent.ascent_date).label("year"),
                func.count(Ascent.id),
            )
            .join(Grade, Grade.id == Ascent.grade_id)
            .join(Area, Area.id == Ascent.area_id)
            .filter(
                Grade.correspondence >= min_grade_correspondence,
                Grade.correspondence <= max_grade_correpondence,
            )
        )

        if area != "All":
            query = query.filter(Area.name == area)

        result = query.group_by("year").order_by(desc("year")).all()

    return result


def get_average_grade(
    min_grade_correspondence=1, max_grade_correpondence=19, area="All"
):
    with Session() as session:
        query = (
            session.query(func.avg(Grade.correspondence))
            .join(Ascent, Grade.id == Ascent.grade_id)
            .join(Area, Area.id == Ascent.area_id)
            .filter(
                Grade.correspondence >= min_grade_correspondence,
                Grade.correspondence <= max_grade_correpondence,
            )
        )

        if area != "All":
            query = query.filter(Area.name == area)

        average_grade_correspondence = round(query.first()[0])

        average_grade = session.scalar(
            select(Grade.grade_value).where(
                Grade.correspondence == average_grade_correspondence
            )
        )
    return average_grade
