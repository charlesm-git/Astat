from sqlalchemy import select, desc

from kivymd.app import MDApp
from kivy.properties import StringProperty
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class AscentManager(MDScreen):
    sort_by = "date"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_by_date()

    def load_ascents(self, ordered_query, group_label_getter):
        with Session() as session:
            # Query the ascents with the right ordering requirement
            ascents = session.scalars(ordered_query).all()

            # Clear the scrolling list
            self.ids.ascent_list.clear_widgets()

            for i, ascent in enumerate(ascents):
                # Get the group of the current ascent
                group_i = group_label_getter(ascent)
                # Display a label with the right groupe name if it's the first
                # ascent logged or if the group changed (ie change of year, of
                # grade, etc.)
                if i == 0 or group_label_getter(ascents[i - 1]) != group_i:
                    group_label = MDLabel(
                        text=str(group_i),
                        adaptive_height=True,
                        bold=True,
                        font_size="20sp",
                        padding=[0, 10, 0, 0],
                    )
                    self.ids.ascent_list.add_widget(group_label)
                    
                # Add current ascent to the list
                ascent_item = AscentItem(
                    name=ascent.name,
                    grade=ascent.grade.grade_value,
                    area=ascent.area.name,
                    date=str(ascent.ascent_date),
                )
                self.ids.ascent_list.add_widget(ascent_item)

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
