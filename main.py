from views.astat import AStatApp

from statistic.queries import (
    get_ascent_per_area,
    get_ascent_per_grade,
    get_total_ascent,
    get_ascent_per_year,
)
from statistic.plotmaker import (
    graph_ascent_per_area,
    graph_ascent_per_grade,
    graph_ascent_per_year,
    graph_showing,
)

from database.database_setup import initialize_db


if __name__ == "__main__":
    # initialize_db()
    AStatApp().run()
    # print(get_total_ascent())
    # print(get_ascent_per_area())
    # print(get_ascent_per_grade())
    # print(get_ascent_per_year())
    # graph_ascent_per_area()
    # graph_ascent_per_grade()
    # graph_ascent_per_year()
    # graph_showing()
