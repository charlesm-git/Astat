from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.widget import Widget
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogIcon,
    MDDialogButtonContainer,
    MDDialogSupportingText,
)
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.clock import Clock

from sqlalchemy import select

from models.area import Area
from models.sector import Sector
from views.snackbar import CustomSnackbar


class LocationScreen(MDScreen):
    """Screen class for adding ascents"""

    model_class = ObjectProperty()
    todolist_id = NumericProperty(None, allownone=True)
    list_refresh = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(lambda x: self.binds())

    def on_pre_enter(self):
        self.list_refresh()

    def on_leave(self):
        self.todolist_id = None

    def binds(self):
        self.list_refresh = self.ids.location_list.location_list_creation
        self.ids.location_form.list_refresh = self.list_refresh


class LocationForm(MDBoxLayout):
    """Form to add an Area to the database"""

    # Defines the function called when an Area is added to the database
    # Initialized in the Adding Screen
    list_refresh = ObjectProperty(None, allownone=True)
    model_class = ObjectProperty()
    todolist_id = NumericProperty(None, allownone=True)
    location_to_update = ObjectProperty(None, allownone=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clear_field(self):
        self.ids.location_form_name.text = ""
        self.location_to_update = None

    def submit(self):
        """Configure the actions performed when the form is submitted"""
        location_name = self.ids.location_form_name.text
        # If no name is provided, notify the user and return
        if location_name == "":
            self.show_snackbar(text="Form Incomplete")
            return
        # Check if an Area with this name already exist
        with MDApp.get_running_app().get_db_session() as session:
            if self.model_class == Area:
                if session.scalar(
                    select(self.model_class).filter_by(name=location_name)
                ):
                    self.show_snackbar(text="Area already exists")
                    return
            else:
                if session.scalar(
                    select(self.model_class).filter_by(
                        name=location_name,
                        todolist_id=self.todolist_id,
                    )
                ):
                    self.show_snackbar(text="Sector already exists")
                    return

        if not self.location_to_update:
            # Create Area
            if self.model_class == Area:
                Area.create(name=location_name)
                self.show_snackbar(text="Area created successfully")
            # Create Sector
            else:
                Sector.create(
                    name=location_name,
                    todolist_id=self.todolist_id,
                )
                self.show_snackbar(text="Sector created successfully")
            self.list_refresh()

        else:
            # Update Area
            if self.model_class == Area:
                self.location_to_update.update(name=location_name)
                self.show_snackbar(text="Area renamed successfully")
            # Update Sector
            else:
                self.location_to_update.update(
                    name=location_name,
                )
                self.show_snackbar(text="Sector renamed successfully")
            self.list_refresh()

        self.clear_field()

    def show_snackbar(self, text):
        snackbar = CustomSnackbar(text=text)
        snackbar.open()


class LocationList(MDBoxLayout):
    """List of areas in order to be able to delete areas"""

    model_class = ObjectProperty()
    todolist_id = NumericProperty(None, allownone=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def location_list_creation(self):
        """Creates the list of AreaItem with a callback function"""
        with MDApp.get_running_app().get_db_session() as session:
            if self.model_class == Area:
                locations = session.scalars(
                    select(Area).order_by(Area.name)
                ).all()
            else:
                locations = session.scalars(
                    select(Sector)
                    .where(Sector.todolist_id == self.todolist_id)
                    .order_by(Sector.name)
                ).all()

            self.clear_widgets()
            for location in locations:
                self.add_widget(
                    LocationItem(
                        location=location,
                        model_class=self.model_class,
                        refresh_callback=(
                            self.refresh_area_list_after_delete_callback
                        ),
                    )
                )

    def refresh_area_list_after_delete_callback(self, location_name):
        """Callback function called when a AreaItem is delete to remove it from
        the list"""
        for widget in self.children:
            if widget.location_name == location_name:
                self.remove_widget(widget)
                break

    def refresh_area_list_after_adding_callback(self, location):
        """Callback function called when an Area is added to the database to
        add is to the list"""
        self.add_widget(
            LocationItem(
                location=location,
                model_class=self.model_class,
                refresh_callback=self.refresh_area_list_after_delete_callback,
            )
        )


class LocationItem(MDBoxLayout):
    """Represent an Area Item in for the delete list"""

    location = ObjectProperty()
    location_name = StringProperty()
    model_class = ObjectProperty()
    form = ObjectProperty()

    def __init__(self, refresh_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.refresh_callback = refresh_callback
        self.location_name = self.location.name
        Clock.schedule_once(lambda *args: self.form_init())

    def form_init(self):
        screen_manager = MDApp.get_running_app().root.ids.screen_manager
        location_screen = screen_manager.get_screen("location")
        self.form = location_screen.ids.location_form

    def update_location(self):
        self.form.ids.location_form_name.text = self.location.name
        self.form.location_to_update = self.location

    def show_delete_dialog(self):
        dialog = MDDialog(
            MDDialogIcon(icon="delete"),
            MDDialogHeadlineText(
                text=f"You are about to delete this location: "
                f"{self.location.name}"
            ),
            MDDialogSupportingText(
                text=(
                    "This action can NOT be reverted and will delete ALL "
                    "associated climbs."
                ),
                bold=True,
                font_style="Title",
                role="medium",
            ),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda *args: dialog.dismiss(),
                ),
                MDButton(
                    MDButtonText(text="Confirm"),
                    style="text",
                    on_release=lambda x: [
                        self.delete_location(),
                        dialog.dismiss(),
                    ],
                ),
            ),
            size_hint_x=0.8,
        )
        dialog.open()

    def delete_location(self):
        """Delete the area from the database and from the area delete list in
        the app"""
        self.model_class.delete(id=self.location.id)
        self.refresh_callback(self.location.name)
