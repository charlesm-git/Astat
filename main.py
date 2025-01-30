from views.astat import AStatApp

# from utils.calculation import get_ascent_per_area, get_ascent_per_grade, get_total_ascent, get_ascent_per_year

# from database.database_setup import initialize_db


if __name__ == "__main__":
    # initialize_db()
    AStatApp().run()
    # print(get_total_ascent())
    # print(get_ascent_per_area())
    # print(get_ascent_per_grade())
    # print(get_ascent_per_year())
