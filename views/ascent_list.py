from sqlalchemy import select, desc

from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.widget import Widget
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogContentContainer,
    MDDialogButtonContainer,
)
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.divider import MDDivider
from kivy.uix.behaviors import ButtonBehavior
from kivy.metrics import dp

from kivymd.uix.segmentedbutton import MDSegmentedButton

from models.area import Area
from models.ascent import Ascent
from models.grade import Grade


class AscentListScreen(MDScreen):
    """Screen for the list of ascents"""

    ascents_data = []
    _initialized = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Adding of a delay: Loading of the list after setup of the layout
        Clock.schedule_once(lambda dt: self.binds())
        Clock.schedule_once(lambda dt: self.load_by_date())
        self._initialized = True

    def binds(self, *args):
        self.ids.area_selector.on_area_selected = self.refresh_data

    def on_pre_enter(self):
        if self._initialized:

            def get_selected_area():
                self.ids.area_selector.selected_area = (
                    MDApp.get_running_app().root.selected_area
                )

            Clock.schedule_once(lambda dt: get_selected_area())
            Clock.schedule_once(lambda dt: self.refresh_data())

    def load_ascents(self, ordered_query, group_label_getter):
        """
        Load all of the ascents into a list (RecycleView)

        Parameters:
        ordered_query: Query for the database, already ordered.
        group_label_getter: Lambda function used to get the category label
        values
        """
        with MDApp.get_running_app().get_db_session() as session:
            # Query the ascents with the right ordering requirement
            ascents = session.scalars(ordered_query).all()

            previous_group = None
            self.ascents_data = []

            for ascent in ascents:
                # Get the group of the new index of ascent.
                current_group = group_label_getter(ascent)
                # If it is a new group, add the group to the ascent_data for
                # display
                if previous_group != current_group:
                    self.ascents_data.append(
                        {
                            "id": 0,
                            "name": str(current_group),
                            "grade": "",
                            "area": "",
                            "date": "",
                            "flash": False,
                            "note": "",
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
                        "flash": ascent.flash,
                        "note": ascent.note,
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

    def refresh_data(self):
        if self.ids.sort_by_date.active:
            self.load_by_date()
        else:
            self.load_by_grade()

    def load_by_date(self):
        """Load data in the RecycleView ordered by dates"""
        query = self.get_filtered_query()
        # Adding ordering to the query
        query = query.order_by(desc(Ascent.ascent_date))
        # Call of load_ascent with the right lambda function
        self.load_ascents(
            ordered_query=query,
            group_label_getter=lambda ascent: ascent.ascent_date.year,
        )

    def load_by_grade(self):
        """Load data in the RecycleView ordered by grades"""
        query = self.get_filtered_query()
        # Adding of the ordering to the query
        query = query.join(Ascent.grade).order_by(
            desc(Grade.correspondence),
            desc(Ascent.ascent_date),
        )
        # Call of load_ascent with the right lambda function
        self.load_ascents(
            ordered_query=query,
            group_label_getter=lambda ascent: ascent.grade.grade_value,
        )

    def get_filtered_query(self):
        """Get the base area filtered query for the database"""
        # Area filter
        area = self.ids.area_selector.ids.selected_area.text
        if area == "All":
            query = select(Ascent)
        else:
            query = select(Ascent).where(Area.name == area).join(Ascent.area)

        # Search filter
        search_input = self.ids.search_field.text
        query = query.where(Ascent.name.like(f"%{search_input}%"))

        return query


class AscentItem(MDBoxLayout):
    """Item to display one individual ascent (one row in the RecycleView)"""

    id = NumericProperty()
    name = StringProperty()
    grade = StringProperty()
    area = StringProperty()
    date = StringProperty()
    flash = BooleanProperty()
    note = StringProperty()
    is_group = BooleanProperty()

    def __init__(self, refresh_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.refresh_callback = refresh_callback  # Store the callback

    def delete_item(self):
        """Function to delete an Ascent from the list and from the database"""
        Ascent.delete(self.id)
        self.refresh_callback(self.id)

    def show_info_dialog(self):
        """Show a dialog window with full details of an ascent when the name of
        the ascent is clicked"""
        if self.is_group:
            return

        app = MDApp.get_running_app()

        self.note = self.note if self.note else " "

        self.info_dialog = MDDialog(
            MDDialogHeadlineText(text="Ascent Details"),
            MDDialogContentContainer(
                MDDivider(),
                DialogItem(icon="calendar", label=self.date),
                DialogItem(icon="terrain", label=self.name),
                DialogItem(icon="chart-bar", label=self.grade),
                DialogItem(icon="map-marker", label=self.area),
                DialogScrollableItem(icon="note", label=self.note),
                MDDivider(),
                orientation="vertical",
                spacing="10dp",
            ),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(
                        text="Delete",
                        theme_text_color="Custom",
                        text_color=app.theme_cls.onErrorColor,
                    ),
                    style="elevated",
                    theme_bg_color="Custom",
                    md_bg_color=app.theme_cls.errorColor,
                    on_release=lambda *args: self.show_delete_dialog(),
                ),
                MDButton(
                    MDButtonText(
                        text="Update",
                        theme_text_color="Custom",
                        text_color=app.theme_cls.onTertiaryColor,
                    ),
                    style="elevated",
                    theme_bg_color="Custom",
                    md_bg_color=app.theme_cls.tertiaryColor,
                    on_release=lambda *args: [
                        self.get_update_screen(self.id),
                        self.info_dialog.dismiss(),
                    ],
                ),
                spacing=dp(10),
            ),
            size_hint_x=0.8,
        )
        self.info_dialog.open()

    def show_delete_dialog(self):
        self.delete_dialog = MDDialog(
            MDDialogIcon(icon="delete"),
            MDDialogHeadlineText(text="Delete this ascent ?"),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="No"),
                    style="text",
                    on_release=lambda *args: self.delete_dialog.dismiss(),
                ),
                MDButton(
                    MDButtonText(text="Yes"),
                    style="text",
                    on_release=lambda x: [
                        self.delete_item(),
                        self.delete_dialog.dismiss(),
                        self.info_dialog.dismiss(),
                    ],
                ),
                Widget(),
            ),
            size_hint_x=0.7,
        )
        self.delete_dialog.open()

    def get_update_screen(self, ascent_to_update_id):
        screen_manager = MDApp.get_running_app().root.ids.screen_manager
        add_ascent_screen = screen_manager.get_screen("ascent")
        add_ascent_screen.ascent_to_update_id = ascent_to_update_id
        screen_manager.current = "ascent"


class CustomMDSegmentedButton(MDSegmentedButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(self._adjust_radius_after_build)

    def _adjust_radius_after_build(self, *args):
        """Ensure the radius is set after all widgets are added."""
        Clock.schedule_once(lambda dt: self.adjust_segment_radius(), 0)


class ClickableMDLabel(ButtonBehavior, MDLabel):
    """Creates a Label with Button properties (clickable)"""

    pass


class DialogItem(MDBoxLayout):
    icon = StringProperty()
    label = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class DialogScrollableItem(MDBoxLayout):
    icon = StringProperty()
    label = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
