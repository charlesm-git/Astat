from sqlalchemy import select, desc, asc, case

from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.properties import (
    StringProperty,
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
)
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.widget import Widget
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogContentContainer,
    MDDialogButtonContainer,
)
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.divider import MDDivider
from kivy.uix.behaviors import ButtonBehavior
from kivy.metrics import dp

from models.sector import Sector
from models.todolist import ToDoList
from views.ascent_list import DialogItem
from models.todoclimb import ToDoClimb
from models.grade import Grade


class ToDoListDetailScreen(MDScreen):
    """Screen for the list of ascents"""

    todolist = ObjectProperty()
    todolist_id = NumericProperty(None)
    todolist_name = StringProperty("This is a very long list name")
    climbs_data = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.load_by_grade())

    def on_pre_enter(self):
        Clock.schedule_once(lambda *args: self.init_attributes())
        Clock.schedule_once(lambda *args: self.refresh_data())

    def init_attributes(self):
        self.todolist_id = self.todolist.id
        self.todolist_name = self.todolist.name

    def load_climbs(self, ordered_query, group_label_getter):
        """
        Load all of the ascents into a list (RecycleView)

        Parameters:
        ordered_query: Query for the database, already ordered.
        group_label_getter: Lambda function used to get the category label
        values
        """
        with MDApp.get_running_app().get_db_session() as session:
            # Query the ascents with the right ordering requirement
            climbs = session.scalars(ordered_query).all()
            previous_group = None
            self.climbs_data = []

            for climb in climbs:
                # Get the group of the new index of ascent.
                current_group = group_label_getter(climb)
                # If it is a new group, add the group to the ascent_data for
                # display
                if previous_group != current_group:
                    self.climbs_data.append(
                        {
                            "id": 0,
                            "name": str(current_group),
                            "grade": "",
                            "sector": "",
                            "note": "",
                            "tag": "",
                            "is_group": True,
                        }
                    )
                    previous_group = current_group
                # Add the ascent to the ascent_data for display in RecycleView
                sector = climb.sector.name if climb.sector else ""
                tag = climb.tag if climb.tag else ""
                self.climbs_data.append(
                    {
                        "id": climb.id,
                        "name": climb.name,
                        "grade": climb.grade.grade_value,
                        "sector": sector,
                        "tag": tag,
                        "note": climb.note,
                        "is_group": False,
                        "refresh_callback": self.refresh_recycleview,
                    }
                )

            self.ids.climb_list.data = self.climbs_data

    def refresh_recycleview(self, popped_id):
        """Refresh the RecycleView when an ascent is deleted."""
        # Pop the deleted ascent from the ascent_data list
        self.climbs_data = [
            ascent for ascent in self.climbs_data if ascent["id"] != popped_id
        ]
        # Update the data of the RecycleView with the ascent_data
        self.ids.climb_list.data = self.climbs_data
        self.ids.climb_list.refresh_from_data()

    def refresh_data(self):
        if self.ids.sort_by_sector.active:
            self.load_by_sector()
        elif self.ids.sort_by_grade.active:
            self.load_by_grade()
        else:
            self.load_by_tag()

    def load_by_sector(self):
        """Load data in the RecycleView ordered by dates"""
        query = self.get_filtered_query()
        # Adding ordering to the query
        query = query.order_by(
            Sector.name.asc().nulls_last(),
            desc(Grade.correspondence),
        )
        # Call of load_ascent with the right lambda function
        self.load_climbs(
            ordered_query=query,
            group_label_getter=lambda climb: (
                climb.sector.name if climb.sector else "Unassigned"
            ),
        )

    def load_by_grade(self):
        """Load data in the RecycleView ordered by grades"""
        query = self.get_filtered_query()
        # Adding of the ordering to the query
        query = query.order_by(
            desc(Grade.correspondence),
            asc(ToDoClimb.name),
        )
        # Call of load_ascent with the right lambda function
        self.load_climbs(
            ordered_query=query,
            group_label_getter=lambda climb: climb.grade.grade_value,
        )

    def load_by_tag(self):
        """Load data in the RecycleView ordered by grades"""
        query = self.get_filtered_query()
        # Adding of the ordering to the query
        tag_order = case(
                (ToDoClimb.tag == "Project", 1),
                (ToDoClimb.tag == "To Try", 2),
                (ToDoClimb.tag == "To Check", 3),
            else_=4,
        )
        query = query.order_by(
            tag_order.nulls_last(),
            desc(Grade.correspondence),
        )
        # Call of load_ascent with the right lambda function
        self.load_climbs(
            ordered_query=query,
            group_label_getter=lambda climb: (
                climb.tag if climb.tag else "Untagged"
            ),
        )

    def get_filtered_query(self):
        """Get the base area filtered query for the database"""
        query = (
            select(ToDoClimb)
            .where(ToDoClimb.todolist_id == self.todolist_id)
            .join(ToDoClimb.grade)
            .outerjoin(ToDoClimb.sector)
        )
        return query

    def delete_todolist(self):
        ToDoList.delete(self.todolist_id)
        self.manager.current = "todolist"

    def update_todolist_name(self):
        todolist_add_screen = self.manager.get_screen("todolist-add")
        todolist_add_screen.todolist_to_update_id = self.todolist_id
        self.manager.current = "todolist-add"

    def show_delete_dialog(self):
        self.delete_dialog = MDDialog(
            MDDialogIcon(icon="delete"),
            MDDialogHeadlineText(text="Delete this list ?"),
            MDDialogSupportingText(
                text=("This action can NOT be reverted"),
                bold=True,
                font_style="Title",
                role="medium",
            ),
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
                        self.delete_todolist(),
                        self.delete_dialog.dismiss(),
                    ],
                ),
                Widget(),
            ),
            size_hint_x=0.7,
        )
        self.delete_dialog.open()

    def get_sector_screen(self):
        location_screen = self.manager.get_screen("area")
        location_screen.model_class = Sector
        location_screen.todolist_id = self.todolist_id
        self.manager.current = "area"

    def get_todoclimb_screen(self):
        todoclimb_screen = self.manager.get_screen("todoclimb")
        todoclimb_screen.todolist_id = self.todolist_id
        self.manager.current = "todoclimb"


class ClimbItem(MDBoxLayout):
    """Item to display one individual ascent (one row in the RecycleView)"""

    id = NumericProperty()
    name = StringProperty()
    grade = StringProperty()
    sector = StringProperty()
    note = StringProperty()
    tag = StringProperty()
    is_group = BooleanProperty()

    def __init__(self, refresh_callback=None, **kwargs):
        super().__init__(**kwargs)
        # refresh_callback is the update of the list when an item is deleted
        self.refresh_callback = refresh_callback

    def delete_item(self):
        """Function to delete an Ascent from the list and from the database"""
        ToDoClimb.delete(self.id)
        self.refresh_callback(self.id)

    def show_info_dialog(self):
        """Show a dialog window with full details of an ascent when the name of
        the ascent is clicked"""
        if self.is_group:
            return

        app = MDApp.get_running_app()

        self.note = self.note if self.note else " "
        self.tag = self.tag if self.tag else " "
        self.sector = self.sector if self.sector else " "

        self.info_dialog = MDDialog(
            MDDialogHeadlineText(text="Climb Details"),
            MDDialogContentContainer(
                MDDivider(),
                DialogItem(icon="terrain", label=self.name),
                DialogItem(icon="chart-bar", label=self.grade),
                DialogItem(icon="map-marker", label=self.sector),
                DialogItem(icon="tag", label=self.tag),
                DialogItem(icon="note", label=self.note),
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
            MDDialogHeadlineText(text="Delete this climb ?"),
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

    def get_update_screen(self, climb_to_update_id):
        screen_manager = MDApp.get_running_app().root.ids.screen_manager
        add_ascent_screen = screen_manager.get_screen("todoclimb")
        add_ascent_screen.climb_to_update_id = climb_to_update_id
        screen_manager.current = "todoclimb"
