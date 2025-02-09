from views.astat import AStatApp

from statistic.queries import (
    get_ascents_per_area,
    get_ascents_per_grade,
    get_total_ascent,
    get_ascents_per_year,
)

from database.database_setup import initialize_db


if __name__ == "__main__":
    # initialize_db()
    AStatApp().run()
    # print(get_total_ascent())
    # print(get_ascents_per_area())
    # print(get_ascents_per_grade())
    # print(get_ascents_per_year())
    # print(search_query())
