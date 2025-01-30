from sqlalchemy import select, desc

from kivy.clock import Clock
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
    """Screen for the list of ascents"""

    ascents_data = []
    _initialized = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Adding of a delay. Loading of the list after setup of the layout
        Clock.schedule_once(lambda dt: self.load_by_date())
        self._initialized = True

    def load_ascents(self, ordered_query, group_label_getter):
        """
        Load all of the ascents into a list (RecycleView)

        Parameters:
        ordered_query: Query for the database, already ordered.
        group_label_getter: Lambda function used to get the category label
        values
        """
        with Session() as session:
            # Query the ascents with the right ordering requirement
            ascents = session.scalars(ordered_query).all()

            previous_group = None
            self.ascents_data = []

            for ascent in ascents:
                # Get the group of the new index of ascent.
                current_group = group_label_getter(ascent)
                # If it is a new group, add the group to the ascent_data for display
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
                # Add the ascent to the ascent_data for display in RecycleView
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
        """Refresh the RecycleView when an ascent is deleted."""
        # Pop the deleted ascent from the ascent_data list
        self.ascents_data = [
            ascent for ascent in self.ascents_data if ascent["id"] != popped_id
        ]
        # Update the data of the RecycleView with the ascent_data
        self.ids.ascent_list.data = self.ascents_data
        self.ids.ascent_list.refresh_from_data()

    def on_enter(self):
        if self._initialized:
            Clock.schedule_once(lambda dt: self.refresh_data())

    def refresh_data(self):
        if self.ids.sort_by_date.style == "filled":
            self.load_by_date()
        else:
            self.load_by_grade()

    def load_by_date(self):
        """Load data in the RecycleView ordered by dates"""
        # if self.ids.sort_by_date.style == "filled":
        #     return
        # Query for the database
        query = select(Ascent).order_by(desc(Ascent.ascent_date))
        # Call of load_ascent with the right lambda function
        self.load_ascents(
            ordered_query=query,
            group_label_getter=lambda ascent: ascent.ascent_date.year,
        )
        # Change button style
        self.ids.sort_by_date.style = "filled"
        self.ids.sort_by_grade.style = "elevated"

    def load_by_grade(self):
        """Load data in the RecycleView ordered by grades"""
        # if self.ids.sort_by_grade.style == "filled":
        #     return
        # Query for the database
        query = (
            select(Ascent)
            .join(Ascent.grade)
            .order_by(
                desc(Grade.correspondence),
                desc(Ascent.ascent_date),
            )
        )
        # Call of load_ascent with the right lambda function
        self.load_ascents(
            ordered_query=query,
            group_label_getter=lambda ascent: ascent.grade.grade_value,
        )
        # Change button style
        self.ids.sort_by_grade.style = "filled"
        self.ids.sort_by_date.style = "elevated"


class AscentItem(MDBoxLayout):
    """Item to display one individual ascent (one row in the RecycleView)"""

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
        """Function to delete an Ascent from the list and from the database"""
        Ascent.delete(self.id)
        self.refresh_callback(self.id)

    def show_info_bubble(self):
        """Show a dialog window with full details of an ascent when the name of 
        the ascent is clicked"""
        if self.is_group:
            return
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
    """Creates a Label with Button properties (clickable)"""
    pass


class DialogItem(MDBoxLayout):
    icon = StringProperty()
    label = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
