from sqlalchemy import select, desc

from kivymd.app import MDApp
from kivy.properties import StringProperty, BooleanProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

from database.database import Session
from models.ascent import Ascent
from models.grade import Grade


class AscentItem(MDBoxLayout):
    name = StringProperty()
    grade = StringProperty()
    area = StringProperty()
    date = StringProperty()
    is_group = BooleanProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class AscentManager(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_by_date()

    def load_ascents(self, ordered_query, group_label_getter):
        with Session() as session:
            # Query the ascents with the right ordering requirement
            ascents = session.scalars(ordered_query).all()

            previous_group = None
            ascent_data = []

            for ascent in ascents:
                current_group = group_label_getter(ascent)
                if previous_group != current_group:
                    ascent_data.append(
                        {
                            "name": str(current_group),
                            "grade": "",
                            "area": "",
                            "date": "",
                            "is_group": True,
                        }
                    )
                    previous_group = current_group

                ascent_data.append(
                    {
                        "name": ascent.name,
                        "grade": ascent.grade.grade_value,
                        "area": ascent.area.name,
                        "date": str(ascent.ascent_date),
                        "is_group": False,
                    }
                )

                self.ids.ascent_list.data = ascent_data

    def load_by_date(self):
        if self.ids.sort_by_date.style == "filled":
            return
        query = select(Ascent).order_by(desc(Ascent.ascent_date))
        self.load_ascents(
            ordered_query=query,
            group_label_getter=lambda ascent: ascent.ascent_date.year,
        )
        self.ids.sort_by_date.style = "filled"
        self.ids.sort_by_grade.style = "elevated"

    def load_by_grade(self):
        if self.ids.sort_by_grade.style == "filled":
            return
        query = (
            select(Ascent)
            .join(Ascent.grade)
            .order_by(desc(Grade.correspondence), desc(Ascent.ascent_date))
        )
        self.load_ascents(
            ordered_query=query,
            group_label_getter=lambda ascent: ascent.grade.grade_value,
        )
        self.ids.sort_by_grade.style = "filled"
        self.ids.sort_by_date.style = "elevated"


class ListApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Darkred"
        return AscentManager()
