from sqlalchemy import func, extract, desc, select, case

from kivymd.app import MDApp

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
    with MDApp.get_running_app().get_db_session() as session:
        query = (
            session.query(
                func.count(Ascent.id),
                func.sum(case((Ascent.flash == True, 1), else_=0)),
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

        result = query.first()

    return result


def get_area_data(
    min_grade_correspondence=1, max_grade_correpondence=19, area="All"
):
    """
    Get the number of ascent per area
    :return: a list of tuple with format : (number_of_ascent, area)
    """
    with MDApp.get_running_app().get_db_session() as session:
        query = (
            session.query(
                Area.name,
                func.count(Ascent.id),
                func.sum(case((Ascent.flash == True, 1), else_=0)),
            )
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


def get_grade_data(
    min_grade_correspondence=1, max_grade_correpondence=19, area="All"
):
    """
    Get the number of ascent per grade
    :return: a list of tuple with format : (number_of_ascent, grade)
    """
    with MDApp.get_running_app().get_db_session() as session:
        query = (
            session.query(
                Grade.grade_value,
                func.count(Ascent.id),
                func.sum(case((Ascent.flash == True, 1), else_=0)),
            )
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


def get_year_data(
    min_grade_correspondence=1, max_grade_correpondence=19, area="All"
):
    """
    Get the number of ascent per year
    :return: a list of tuple with format : (number_of_ascent, year)
    """
    with MDApp.get_running_app().get_db_session() as session:
        query = (
            session.query(
                extract("year", Ascent.ascent_date).label("year"),
                func.count(Ascent.id),
                func.sum(case((Ascent.flash == True, 1), else_=0)),
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
    with MDApp.get_running_app().get_db_session() as session:
        query = (
            session.query(
                func.avg(Grade.correspondence),
                func.avg(
                    case(
                        (Ascent.flash == True, Grade.correspondence),
                        else_=None,
                    )
                ),
            )
            .join(Ascent, Grade.id == Ascent.grade_id)
            .join(Area, Area.id == Ascent.area_id)
            .filter(
                Grade.correspondence >= min_grade_correspondence,
                Grade.correspondence <= max_grade_correpondence,
            )
        )

        if area != "All":
            query = query.filter(Area.name == area)

        average_grade, average_flash_grade = query.first()

        # If the average grade returned by the query is not (No ascent with
        # those filters), return None
        average_grade = get_avg_grade_from_corresp(average_grade, session)
        average_flash_grade = get_avg_grade_from_corresp(
            average_flash_grade, session
        )

    return average_grade, average_flash_grade


def get_avg_grade_from_corresp(average_correspondence, session):
    if not average_correspondence:
        return None
    average_grade = round(average_correspondence)
    average_grade = session.scalar(
        select(Grade.grade_value).where(Grade.correspondence == average_grade)
    )
    return average_grade
