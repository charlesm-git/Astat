from datetime import date
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel
from kivymd.uix.pickers import MDModalDatePicker
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty
from kivy.metrics import dp
from sqlalchemy import select

from database.database import Session
from models.area import Area
from models.grade import Grade
from models.ascent import Ascent


class DropDownMenuHeader(ButtonBehavior, MDBoxLayout):
    leading_icon = StringProperty()
    text = StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AddAscentScreen(MDScreen):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AddingForm(MDBoxLayout):
    form = {
        "name": "",
        "grade_id": "",
        "area_id": "",
        "date": "",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def open_grade_menu(self, item):
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
        self.ids.form_grade.text = grade_name
        self.form["grade_id"] = int(grade_id)
        self.grade_menu.dismiss()

    def open_area_menu(self, item):
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
        self.ids.form_area.text = area_name
        self.form["area_id"] = int(area_id)
        self.area_menu.dismiss()

    def show_date_picker(self):
        date_dialog = MDModalDatePicker()
        date_dialog.bind(on_ok=self.picker_on_ok)
        date_dialog.bind(on_cancel=date_dialog.dismiss)
        date_dialog.open()

    def picker_on_ok(self, date_picker_instance):
        self.ids.form_date_picker.text = str(
            date_picker_instance.get_date()[0]
        )
        self.form["date"] = date_picker_instance.get_date()[0]
        date_picker_instance.dismiss()

    def submit(self):
        self.get_name_from_form()
        print(self.form)
        for value in self.form.values():
            if value == "":
                print("Form Incomplete")
                return
        with Session() as session:
            if not session.scalar(
                select(Ascent).where(
                    Ascent.name == self.form["name"],
                    Ascent.grade_id == self.form["grade_id"],
                    Ascent.area_id == self.form["area_id"],
                )
            ):
                Ascent.create(
                    name=self.form["name"],
                    grade_id=self.form["grade_id"],
                    area_id=self.form["area_id"],
                    ascent_date=self.form["date"],
                )
                print("Ascent added")
            else:
                print("Ascent already exist in the database")

    def get_name_from_form(self):
        typed_name = self.ids.form_name.text
        self.form["name"] = typed_name
