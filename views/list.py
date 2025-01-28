from sqlalchemy import select, desc

from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.widget import Widget
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogContentContainer,
    MDDialogButtonContainer,
    MDDialogHeadlineText,
)
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.divider import MDDivider
from kivy.uix.behaviors import ButtonBehavior

from database.database import Session
from models.ascent import Ascent
from models.grade import Grade


class ListScreen(MDScreen):
    ascents_data = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_by_date()

    def load_ascents(self, ordered_query, group_label_getter):
        with Session() as session:
            # Query the ascents with the right ordering requirement
            ascents = session.scalars(ordered_query).all()

            previous_group = None
            self.ascents_data = []

            for ascent in ascents:
                current_group = group_label_getter(ascent)
                if previous_group != current_group:
                    self.ascents_data.append(
                        {
                            "id": 0,
                            "name": str(current_group),
                            "grade": "",
                            "area": "",
                            "date": "",
                            "is_group": True,
                        }
                    )
                    previous_group = current_group

                self.ascents_data.append(
                    {
                        "id": ascent.id,
                        "name": ascent.name,
                        "grade": ascent.grade.grade_value,
                        "area": ascent.area.name,
                        "date": str(ascent.ascent_date),
                        "is_group": False,
                        "refresh_callback": self.refresh_recycleview,
                    }
                )

            self.ids.ascent_list.data = self.ascents_data

    def refresh_recycleview(self, popped_id):
        """Refresh the RecycleView."""
        self.ascents_data = [
            ascent for ascent in self.ascents_data if ascent["id"] != popped_id
        ]
        self.ids.ascent_list.data = self.ascents_data
        self.ids.ascent_list.refresh_from_data()

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


class AscentItem(MDBoxLayout):
    id = NumericProperty()
    name = StringProperty()
    grade = StringProperty()
    area = StringProperty()
    date = StringProperty()
    is_group = BooleanProperty()

    def __init__(self, refresh_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.refresh_callback = refresh_callback  # Store the callback

    def delete_item(self):
        Ascent.delete(self.id)
        self.refresh_callback(
            self.id
        )  # Call the callback to refresh the RecycleView

    def show_info_bubble(self):
        """Show a dialog with the full name and additional details."""
        dialog = MDDialog(
            MDDialogHeadlineText(text="Ascent Details"),
            MDDialogContentContainer(
                MDDivider(),
                DialogItem(icon="calendar", label=self.date),
                DialogItem(icon="terrain", label=self.name),
                DialogItem(icon="chart-bar", label=self.grade),
                DialogItem(icon="map-marker", label=self.area),
                MDDivider(),
                orientation="vertical",
                spacing="10dp",
            ),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="Close"),
                    style="text",
                    on_release=lambda *args: dialog.dismiss(),
                ),
            ),
        )
        dialog.open()


class ClickableMDLabel(ButtonBehavior, MDLabel):
    pass


class DialogItem(MDBoxLayout):
    icon = StringProperty()
    label = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
