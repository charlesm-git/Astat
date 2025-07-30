import os

from kivy.lang import Builder
from kivymd.app import MDApp

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from views.screenmanager import MainScreenManager

from models.base import Base
from database import get_db_path, get_grades_as_object

# Window.size = (400, 720)


class AStatApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Darkred"

        db_path = get_db_path()

        self.Session = self.init_db(db_path)

        Builder.load_file("kv/selector.kv")
        Builder.load_file("kv/barchart.kv")
        Builder.load_file("kv/ascent-list-screen.kv")
        Builder.load_file("kv/ascent-screen.kv")
        Builder.load_file("kv/settings-screen.kv")
        Builder.load_file("kv/location-screen.kv")
        Builder.load_file("kv/statistic-screen.kv")
        Builder.load_file("kv/statistic-filter-screen.kv")
        Builder.load_file("kv/todoclimb-screen.kv")
        Builder.load_file("kv/todolist-screen.kv")
        Builder.load_file("kv/todolist-detail-screen.kv")
        Builder.load_file("kv/todolist-add-screen.kv")
        Builder.load_file("kv/screenmanager.kv")
        return MainScreenManager()

    def get_db_session(self):
        return self.Session()

    def init_db(self, db_path):
        DATABASE_URL = f"sqlite:///{db_path}"
        engine = create_engine(DATABASE_URL, echo=False)
        session_factory = sessionmaker(bind=engine)
        Session = scoped_session(session_factory)

        if not os.path.exists(db_path):
            grades = get_grades_as_object()
            with Session() as session:
                Base.metadata.create_all(engine)
                session.add_all(grades)
                session.commit()

        return Session
