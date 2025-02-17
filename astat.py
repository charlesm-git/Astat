from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from views.ascent_list import AscentListScreen
from views.ascent import AscentScreen
from views.area import AreaScreen
from views.statistics import StatisticScreen
from views.settings import SettingsScreen
# from views.to_do_list import ToDoListScreen
from views.statistics_filter import StatisticFilterScreen
from views.selector import AreaSelector
from views.screenmanager import MainScreenManager

from database import get_db_path, run_migrations

# Window.size = (400, 720)


class AStatApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Darkred"

        db_path = get_db_path()
        run_migrations()
        self.Session = self.init_db(db_path)

        Builder.load_file("kv/selector.kv")
        Builder.load_file("kv/ascent-list-screen.kv")
        Builder.load_file("kv/ascent-screen.kv")
        Builder.load_file("kv/settings-screen.kv")
        Builder.load_file("kv/area-screen.kv")
        Builder.load_file("kv/statistic-screen.kv")
        Builder.load_file("kv/statistic-filter-screen.kv")
        # Builder.load_file("kv/to-do-list-screen.kv")
        Builder.load_file("kv/screenmanager.kv")
        return MainScreenManager()

    def get_db_session(self):
        return self.Session()

    def init_db(self, db_path):
        DATABASE_URL = f"sqlite:///{db_path}"
        engine = create_engine(DATABASE_URL, echo=False)
        session_factory = sessionmaker(bind=engine)
        Session = scoped_session(session_factory)
        return Session
