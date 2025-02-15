import os
import shutil

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.utils import platform

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from views.list import ListScreen
from views.adding_ascent import AddingAscentScreen
from views.adding_area import AddingAreaScreen
from views.statistics import StatisticScreen
from views.settings import SettingsScreen
from views.statistics_filter import StatisticFilterScreen
from views.selector import AreaSelector
from views.screenmanager import MainScreenManager

Window.size = (400, 720)


class AStatApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Darkred"

        db_path = self.get_db_path()
        self.Session = self.init_db(db_path)

        Builder.load_file("kv/selector.kv")
        Builder.load_file("kv/list-screen.kv")
        Builder.load_file("kv/adding-ascent-screen.kv")
        Builder.load_file("kv/settings-screen.kv")
        Builder.load_file("kv/adding-area-screen.kv")
        Builder.load_file("kv/statistic-screen.kv")
        Builder.load_file("kv/statistic-filter-screen.kv")
        Builder.load_file("kv/screenmanager.kv")
        return MainScreenManager()

    def get_db_path(self):
        db_filename = "astat.db"
        if platform == "win":
            data_dir = os.path.join(os.environ["APPDATA"], self.name)
        elif platform == "android":
            # Get Android context
            from jnius import autoclass, cast

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            context = cast("android.content.Context", PythonActivity.mActivity)

            # Get external storage path for your app
            file_p = cast("java.io.File", context.getExternalFilesDir(None))
            data_dir = file_p.getAbsolutePath()

        writable_db_path = os.path.join(data_dir, db_filename)

        if not os.path.exists(writable_db_path):
            bundled_db_path = os.path.join(
                os.path.dirname(__file__), db_filename
            )
            if os.path.exists(bundled_db_path):
                shutil.copyfile(bundled_db_path, writable_db_path)

        return writable_db_path

    def get_db_session(self):
        return self.Session()

    def init_db(self, db_path):
        DATABASE_URL = f"sqlite:///{db_path}"
        engine = create_engine(DATABASE_URL, echo=False)

        session_factory = sessionmaker(bind=engine)

        Session = scoped_session(session_factory)
        return Session
