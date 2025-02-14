from datetime import datetime
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDModalDatePicker
from kivymd.uix.snackbar import (
    MDSnackbar,
    MDSnackbarText,
    MDSnackbarCloseButton,
    MDSnackbarButtonContainer,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.metrics import dp
from sqlalchemy import select

from models.area import Area
from models.grade import Grade
from models.ascent import Ascent


class AddingAscentScreen(MDScreen):
    """Screen class for adding ascents"""

    ascent_to_update_id = NumericProperty(None, allownone=True)
    ascent_to_update = ObjectProperty(None, allownone=True)

    form = {
        "name": "",
        "grade_id": "",
        "area_id": "",
        "date": "",
    }
    date_picker = ObjectProperty(MDModalDatePicker)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(lambda *args: self.init_date_picker())

    def on_pre_enter(self):
        # Pre filling of the form in case of an update
        if self.ascent_to_update_id:
            self.ascent_to_update = Ascent.get_from_id(
                self.ascent_to_update_id
            )
            area = Area.get_from_id(self.ascent_to_update.area_id)
            grade = Grade.get_from_id(self.ascent_to_update.grade_id)

            # Update UI
            self.ids.ascent_form_name.text = self.ascent_to_update.name
            self.ids.ascent_form_area.text = area.name
            self.ids.ascent_form_grade.text = grade.grade_value
            self.ids.ascent_form_date_picker.text = str(
                self.ascent_to_update.ascent_date
            )
            # Update form's backend
            self.form["grade_id"] = self.ascent_to_update.grade_id
            self.form["area_id"] = self.ascent_to_update.area_id
            self.form["date"] = self.ascent_to_update.ascent_date

            # Update datepicker
            self.date_picker.sel_day = self.ascent_to_update.ascent_date.day
            self.date_picker.sel_month = (
                self.ascent_to_update.ascent_date.month
            )
            self.date_picker.sel_year = self.ascent_to_update.ascent_date.year
            self.date_picker.update_calendar(
                self.date_picker.sel_year,
                self.date_picker.sel_month,
            )

    def on_leave(self):
        self.ascent_to_update_id = None
        self.clear_all_fields()

    def init_date_picker(self):
        self.date_picker = MDModalDatePicker()
        self.date_picker.bind(on_ok=self.picker_on_ok)
        self.date_picker.bind(on_cancel=self.date_picker.dismiss)

    def open_grade_menu(self, item):
        """Function for grade dropdown menu configuration and opening"""
        with MDApp.get_running_app().get_db_session() as session:
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
        with MDApp.get_running_app().get_db_session() as session:
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
        self.date_picker.open()

    def picker_on_ok(self, date_picker_instance):
        """
        Configure the actions performed when the ok button is pressed in the
        date picker.
        Update the date displayed on the label and the content of the form.
        """
        selected_date = date_picker_instance.get_date()[0]
        self.ids.ascent_form_date_picker.text = str(selected_date)
        self.form["date"] = selected_date
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

        # # Get the parent screen to check if if is an update or a creation
        # parent = self.parent
        # while parent:
        #     if isinstance(parent, MDScreen):
        #         screen = parent
        #         break
        #     parent = parent.parent

        if self.ascent_to_update:
            self.ascent_to_update.update(
                name=self.form["name"],
                grade_id=self.form["grade_id"],
                area_id=self.form["area_id"],
                ascent_date=self.form["date"],
            )
            self.show_snackbar(text="Ascent updated successfully")
            self.parent.current = "ascents-list"

        else:
            with MDApp.get_running_app().get_db_session() as session:
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
                        text=(
                            f"This climb was logged on "
                            f"{ascent_existence_check.ascent_date}"
                        )
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
        # Empty the text fields
        self.ids.ascent_form_name.text = ""
        self.ids.ascent_form_area.text = "Area"
        self.ids.ascent_form_grade.text = "Grade"
        self.ids.ascent_form_date_picker.text = "Date"
        # Reset the date_picker on today
        today = datetime.today()
        self.date_picker.sel_day = today.day
        self.date_picker.sel_month = today.month
        self.date_picker.sel_year = today.year
        self.date_picker.update_calendar(
            self.date_picker.sel_year, self.date_picker.sel_month
        )


class DropDownMenuHeader(ButtonBehavior, MDBoxLayout):
    """Class declaration for header of Grade, Area and Date selection"""

    leading_icon = StringProperty()
    text = StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
