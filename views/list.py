from sqlalchemy import select

from kivymd.app import MDApp
from kivy.properties import StringProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout

from database.database import Session
from models.ascent import Ascent


class AscentItem(MDBoxLayout):
    name = StringProperty()
    grade = StringProperty()
    area = StringProperty()
    date = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class AscentManager(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_ascents()

    def load_ascents(self):
        with Session() as session:
            ascents = session.scalars(select(Ascent)).all()
            for ascent in ascents:
                ascent_item = AscentItem(
                    name=ascent.name,
                    grade=ascent.grade.grade_value,
                    area=ascent.area.name,
                    date=str(ascent.ascent_date),
                )
                self.ids.ascent_list.add_widget(ascent_item)


class ListApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Darkred"
        return AscentManager()
