from views.astat import AStatApp

from statistic.queries import (
    get_ascents_per_area,
    get_ascents_per_grade,
    get_total_ascent,
    get_ascents_per_year,
)

from sqlalchemy import select
from models.grade import Grade
from database.database_setup import initialize_db
from database.database import Session

if __name__ == "__main__":
    # initialize_db()
    AStatApp().run()
    # print(get_total_ascent())
    # print(get_ascents_per_area(12,13))
    # print(get_ascents_per_grade())
    # print(get_ascents_per_year(12,13))
    # print(search_query())
