from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDModalDatePicker
from kivymd.uix.snackbar import (
    MDSnackbar,
    MDSnackbarText,
    MDSnackbarCloseButton,
    MDSnackbarButtonContainer,
)
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogButtonContainer,
    MDDialogHeadlineText,
    MDDialogIcon,
    MDDialogSupportingText,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty
from kivy.metrics import dp
from sqlalchemy import select

from database.database import Session
from models.area import Area
from models.grade import Grade
from models.ascent import Ascent


class AddingScreen(MDScreen):
    """Screen class for adding ascents"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(lambda x: self.binds())

    def binds(self):
        self.ids.adding_area_form.on_area_adding = (
            self.ids.delete_area_list.refresh_area_list_after_adding_callback
        )


class AddingAscentForm(MDBoxLayout):
    """Form for adding ascents.
    Contains :
    - TextField for name input
    - Dropdown menu for grade selection
    - Dropdown menu for area selection
    - Date picker for date selection
    """

    form = {
        "name": "",
        "grade_id": "",
        "area_id": "",
        "date": "",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def open_grade_menu(self, item):
        """Function for grade dropdown menu configuration and opening"""
        with Session() as session:
            grades = session.scalars(select(Grade)).all()

        menu_items = [
            {
                "text": f"{grade.grade_value}",
                "on_release": lambda g=grade: self.grade_menu_callback(
                    g.id,
                    g.grade_value,
                ),
            }
            for grade in grades
        ]
        # Setup of the dropdown menu
        self.grade_menu = MDDropdownMenu(
            caller=item,
            items=menu_items,
            max_height=dp(200),
            width=dp(100),
            position="bottom",
            hor_growth="right",
        )
        self.grade_menu.open()

    def grade_menu_callback(self, grade_id, grade_name):
        """
        Function called when a grade is selected.
        Updated the grade displayed on the label and the content of the form
        """
        self.ids.ascent_form_grade.text = grade_name
        self.form["grade_id"] = int(grade_id)
        self.grade_menu.dismiss()

    def open_area_menu(self, item):
        """Function for grade dropdown menu configuration and opening"""
        with Session() as session:
            areas = session.scalars(select(Area).order_by(Area.name)).all()

        menu_items = [
            {
                "text": f"{area.name}",
                "on_release": lambda a=area: self.area_menu_callback(
                    a.id,
                    a.name,
                ),
            }
            for area in areas
        ]
        # Setup of the dropdown menu
        self.area_menu = MDDropdownMenu(
            caller=item,
            items=menu_items,
            max_height=dp(200),
            width=dp(180),
            position="bottom",
            hor_growth="right",
        )
        self.area_menu.open()

    def area_menu_callback(self, area_id, area_name):
        """
        Function called when an area is selected.
        Updated the area displayed on the label and the content of the form
        """
        self.ids.ascent_form_area.text = area_name
        self.form["area_id"] = int(area_id)
        self.area_menu.dismiss()

    def show_date_picker(self):
        """Setup the date picker and open it"""
        date_dialog = MDModalDatePicker()
        date_dialog.bind(on_ok=self.picker_on_ok)
        date_dialog.bind(on_cancel=date_dialog.dismiss)
        date_dialog.open()

    def picker_on_ok(self, date_picker_instance):
        """
        Configure the actions performed when the ok button is pressed in the
        date picker.
        Update the date displayed on the label and the content of the form.
        """
        self.ids.ascent_form_date_picker.text = str(
            date_picker_instance.get_date()[0]
        )
        self.form["date"] = date_picker_instance.get_date()[0]
        date_picker_instance.dismiss()

    def submit(self):
        """Configure the actions performed when the form is submitted"""
        # Update the form with the name input
        typed_name = self.ids.ascent_form_name.text
        self.form["name"] = typed_name
        incomplete = False
        # Check if the form is complete
        for value in self.form.values():
            if value == "":
                incomplete = True
                break
        # If incomplete, notify the user
        if incomplete:
            self.show_snackbar(
                text="Form Incomplete",
            )
            return

        with Session() as session:
            ascent_existence_check = session.scalar(
                select(Ascent).where(
                    Ascent.name == self.form["name"],
                    Ascent.grade_id == self.form["grade_id"],
                    Ascent.area_id == self.form["area_id"],
                )
            )
            # If the ascent is already logged in the database, notify the user
            # and return
            if ascent_existence_check:
                self.show_snackbar(
                    text=f"This climb was logged on {ascent_existence_check.ascent_date}"
                )
                return

        Ascent.create(
            name=self.form["name"],
            grade_id=self.form["grade_id"],
            area_id=self.form["area_id"],
            ascent_date=self.form["date"],
        )
        self.show_snackbar(text="Ascent added successfully")
        # Reset all fields
        self.submit_clear_fields()

    def show_snackbar(self, text):
        """Function displaying a snackbar for user feedback"""
        snackbar = MDSnackbar(
            MDSnackbarText(
                text=text,
                adaptive_size=True,
            ),
            MDSnackbarButtonContainer(
                MDSnackbarCloseButton(
                    icon="close", on_release=lambda x: snackbar.dismiss()
                ),
                pos_hint={"center_y": 0.5},
            ),
            y=dp(100),
            orientation="horizontal",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            duration=5,
        )
        snackbar.open()

    def submit_clear_fields(self):
        self.ids.ascent_form_name.text = ""
        self.ids.ascent_form_grade.text = "Grade"

    def clear_all_fields(self):
        self.ids.ascent_form_name.text = ""
        self.ids.ascent_form_area.text = "Area"
        self.ids.ascent_form_grade.text = "Grade"
        self.ids.ascent_form_date_picker.text = "Date"


class AddingAreaForm(MDBoxLayout):
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
        with Session() as session:
            if session.scalar(select(Area).where(Area.name == area_name)):
                self.show_snackbar(text="Area already exists")
                return
        Area.create(name=area_name)
        self.show_snackbar(text="Area created successfully")
        self.clear_field()
        
        if callable(self.on_area_adding):
            self.on_area_adding(area_name)

    def show_snackbar(self, text):
        snackbar = MDSnackbar(
            MDSnackbarText(
                text=text,
                adaptive_size=True,
            ),
            MDSnackbarButtonContainer(
                MDSnackbarCloseButton(
                    icon="close", on_release=lambda x: snackbar.dismiss()
                ),
                pos_hint={"center_y": 0.5},
            ),
            y=dp(100),
            orientation="horizontal",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            duration=5,
        )
        snackbar.open()


class DeleteAreaList(MDBoxLayout):
    """List of areas in order to be able to delete areas"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(lambda x: self.area_list_creation())

    def area_list_creation(self):
        """Creates the list of AreaItem with a callback function"""
        with Session() as session:
            areas = session.scalars(select(Area)).all()
            for area in areas:
                self.add_widget(
                    AreaItem(
                        area_name=area.name,
                        refresh_callback=self.refresh_area_list_after_delete_callback,
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
                text="This action is IRREVERSIBLE and will delete ALL associated ascent.",
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
        )
        dialog.open()

    def delete_area(self):
        """Delete the area from the database and from the area delete list in
        the app"""
        Area.delete(area_name=self.area_name)
        self.refresh_callback(self.area_name)


class DropDownMenuHeader(ButtonBehavior, MDBoxLayout):
    """Class declaration for header of Grade, Area and Date selection"""

    leading_icon = StringProperty()
    text = StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
