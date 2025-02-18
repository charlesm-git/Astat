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
from kivy.properties import ObjectProperty, StringProperty
from kivy.clock import Clock

from sqlalchemy import select

from models.area import Area
from views.snackbar import CustomSnackbar


class AreaScreen(MDScreen):
    """Screen class for adding ascents"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(lambda x: self.binds())

    def binds(self):
        self.ids.adding_area_form.on_area_adding = (
            self.ids.delete_area_list.refresh_area_list_after_adding_callback
        )


class AreaForm(MDBoxLayout):
    """Form to add an Area to the database"""

    # Defines the function called when an Area is added to the database
    # Initialized in the Adding Screen
    on_area_adding = ObjectProperty(None, allownone=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clear_field(self):
        self.ids.area_form_name.text = ""

    def submit(self):
        """Configure the actions performed when the form is submitted"""
        area_name = self.ids.area_form_name.text
        # If no name is provided, notify the user and return
        if area_name == "":
            self.show_snackbar(text="Form Incomplete")
            return
        # Check if an Area with this name already exist
        with MDApp.get_running_app().get_db_session() as session:
            if session.scalar(select(Area).where(Area.name == area_name)):
                self.show_snackbar(text="Area already exists")
                return
        Area.create(name=area_name)
        self.show_snackbar(text="Area created successfully")
        self.clear_field()

        if callable(self.on_area_adding):
            self.on_area_adding(area_name)

    def show_snackbar(self, text):
        snackbar = CustomSnackbar(text=text)
        snackbar.open()


class AreaList(MDBoxLayout):
    """List of areas in order to be able to delete areas"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(lambda x: self.area_list_creation())

    def area_list_creation(self):
        """Creates the list of AreaItem with a callback function"""
        with MDApp.get_running_app().get_db_session() as session:
            areas = session.scalars(select(Area)).all()
            for area in areas:
                self.add_widget(
                    AreaItem(
                        area_name=area.name,
                        refresh_callback=(
                            self.refresh_area_list_after_delete_callback
                        ),
                    )
                )

    def refresh_area_list_after_delete_callback(self, area_name):
        """Callback function called when a AreaItem is delete to remove it from
        the list"""
        for widget in self.children:
            if widget.area_name == area_name:
                self.remove_widget(widget)
                break

    def refresh_area_list_after_adding_callback(self, area_name):
        """Callback function called when an Area is added to the database to
        add is to the list"""
        self.add_widget(
            AreaItem(
                area_name=area_name,
                refresh_callback=self.refresh_area_list_after_delete_callback,
            )
        )


class AreaItem(MDBoxLayout):
    """Represent an Area Item in for the delete list"""

    area_name = StringProperty()

    def __init__(self, refresh_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.refresh_callback = refresh_callback

    def show_delete_dialog(self):
        dialog = MDDialog(
            MDDialogIcon(icon="delete"),
            MDDialogHeadlineText(
                text=f"You are about to delete this area : {self.area_name}"
            ),
            MDDialogSupportingText(
                text=(
                    "This action is IRREVERSIBLE and will delete ALL "
                    "associated ascents."
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
                        self.delete_area(),
                        dialog.dismiss(),
                    ],
                ),
            ),
            size_hint_x=0.8,
        )
        dialog.open()

    def delete_area(self):
        """Delete the area from the database and from the area delete list in
        the app"""
        Area.delete(area_name=self.area_name)
        self.refresh_callback(self.area_name)
