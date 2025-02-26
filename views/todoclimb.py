from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.chip import MDChip, MDChipText

from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty
from kivy.metrics import dp

from sqlalchemy import select

from models.grade import Grade
from models.sector import Sector
from models.todoclimb import ToDoClimb
from views.snackbar import CustomSnackbar


class ToDoClimbScreen(MDScreen):
    climb_to_update_id = NumericProperty(None, allownone=True)
    climb_to_update = ObjectProperty(None, allownone=True)
    todolist_id = NumericProperty()

    form = {
        "name": "",
        "grade_id": "",
        "sector_id": "",
        "todolist_id": "",
        "tag": "",
        "star": False,
        "note": "",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(lambda *args: self.create_chips())

    def on_pre_enter(self):
        # Pre filling of the form in case of an update
        if self.climb_to_update_id:
            self.climb_to_update = ToDoClimb.get_from_id(
                self.climb_to_update_id
            )

            # Update name
            self.ids.climb_form_name.text = self.climb_to_update.name

            # Update grade
            grade = Grade.get_from_id(self.climb_to_update.grade_id)
            self.ids.climb_form_grade.text = grade.grade_value
            self.form["grade_id"] = self.climb_to_update.grade_id

            # Update sector
            if self.climb_to_update.sector_id:
                sector = Sector.get_from_id(self.climb_to_update.sector_id)
                self.ids.climb_form_sector.text = sector.name
                self.form["sector_id"] = self.climb_to_update.sector_id

            # Update tag
            if self.climb_to_update.tag:
                for child in self.ids.climb_form_tag.children:
                    if (
                        self.climb_to_update.tag
                        == child.children[1].children[0].text
                    ):
                        child.active = True
                self.form["tag"] = self.climb_to_update.tag

            # Update note
            self.ids.climb_form_note.text = self.climb_to_update.note
            self.form["note"] = self.climb_to_update.note

            # Update star
            if self.climb_to_update.star:
                self.ids.climb_form_star.icon = "star"
                self.form["star"] = True

    def on_enter(self):
        self.form["todolist_id"] = self.todolist_id

    def on_leave(self):
        self.climb_to_update_id = None
        self.climb_to_update = None
        self.clear_all_fields()

    def create_chips(self):
        app = MDApp.get_running_app()
        for tag in ["To Check", "To Try", "Project"]:
            chip = MDChip(
                MDChipText(
                    text=tag,
                ),
                type="filter",
                theme_line_color="Custom",
                line_color=app.theme_cls.surfaceContainerHighestColor,
            )
            chip.bind(active=self.uncheck_chip)
            self.ids.climb_form_tag.add_widget(chip)

    def uncheck_chip(self, current_chip, active) -> None:
        """Removes a mark from an already marked chip."""
        if active:
            for chip in self.ids.climb_form_tag.children:
                if current_chip is not chip:
                    if chip.active:
                        chip.active = False

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
            max_height=dp(350),
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
        self.ids.climb_form_grade.text = grade_name
        self.form["grade_id"] = int(grade_id)
        self.grade_menu.dismiss()

    def open_sector_menu(self, item):
        """Function for grade dropdown menu configuration and opening"""
        with MDApp.get_running_app().get_db_session() as session:
            sectors = session.scalars(
                select(Sector)
                .where(Sector.todolist_id == self.todolist_id)
                .order_by(Sector.name)
            ).all()

        menu_items = [
            {
                "text": f"{sector.name}",
                "on_release": lambda a=sector: self.sector_menu_callback(
                    a.id,
                    a.name,
                ),
            }
            for sector in sectors
        ]
        # Setup of the dropdown menu
        self.sector_menu = MDDropdownMenu(
            caller=item,
            items=menu_items,
            max_height=dp(300),
            width=dp(200),
            position="bottom",
            hor_growth="right",
        )
        self.sector_menu.open()

    def sector_menu_callback(self, sector_id, sector_name):
        """
        Function called when a sector is selected.
        Updated the sector displayed on the label and the content of the form
        """
        self.ids.climb_form_sector.text = sector_name
        self.form["sector_id"] = int(sector_id)
        self.sector_menu.dismiss()

    def update_star(self):
        star = self.ids.climb_form_star
        if star.icon == "star-outline":
            star.icon = "star"
            self.form["star"] = True
        else:
            star.icon = "star-outline"
            self.form["star"] = False

    def submit(self):
        """Configure the actions performed when the form is submitted"""

        # Update the form with the name input and the note
        typed_name = self.ids.climb_form_name.text
        typed_note = self.ids.climb_form_note.text

        if len(typed_name) > 64:
            self.show_snackbar(text="Name too long")
            return

        self.form["name"] = typed_name
        self.form["note"] = typed_note

        # Update the form with the right tag
        active_tag = None
        for child in self.ids.climb_form_tag.children:
            if child.active:
                # Manually accessing MDChipText content from MDChip
                active_tag = child.children[1].children[0].text
        self.form["tag"] = active_tag

        # Update the form with None values for sector_id for database
        # entry
        if not self.form["sector_id"]:
            self.form["sector_id"] = None

        # Check if the form is complete
        incomplete = False
        for key, value in self.form.items():
            if key in ["name", "grade"] and value == "":
                incomplete = True
                break

        # If incomplete, notify the user and return
        if incomplete:
            self.show_snackbar(
                text="Form Incomplete",
            )
            return

        # Database modification

        # Run if an ascent is currently being updated, call update function
        if self.climb_to_update:
            self.climb_to_update.update(
                name=self.form["name"],
                grade_id=self.form["grade_id"],
                sector_id=self.form["sector_id"],
                tag=self.form["tag"],
                note=self.form["note"],
                star=self.form["star"],
            )
            self.show_snackbar(text="Ascent updated successfully")
            self.manager.current = "todolist-detail"
        # Run if an ascent is currently being created
        else:
            ToDoClimb.create(
                name=self.form["name"],
                grade_id=self.form["grade_id"],
                sector_id=self.form["sector_id"],
                tag=self.form["tag"],
                note=self.form["note"],
                todolist_id=self.form["todolist_id"],
                star=self.form["star"],
            )
            # Show snackbar for user feedback
            self.show_snackbar(text="Climb added successfully")
            # Reset all fields
            self.submit_clear_fields()

    def show_snackbar(self, text):
        """Function displaying a snackbar for user feedback"""
        snackbar = CustomSnackbar(text=text)
        snackbar.open()

    def submit_clear_fields(self):
        """Reset only some of the fields after a submit (date and sector are
        kept)"""
        self.ids.climb_form_name.text = ""
        self.ids.climb_form_grade.text = "Grade"
        self.ids.climb_form_note.text = ""
        self.ids.climb_form_star.icon = "star-outline"

        # Reset form
        self.form["name"] = ""
        self.form["grade_id"] = ""
        self.form["note"] = ""
        self.form["star"] = False

    def clear_all_fields(self):
        """Reset all the fields"""
        # Empty the text fields
        self.ids.climb_form_name.text = ""
        self.ids.climb_form_sector.text = "Sector"
        self.ids.climb_form_grade.text = "Grade"
        self.ids.climb_form_note.text = ""
        self.ids.climb_form_star.icon = "star-outline"

        for child in self.ids.climb_form_tag.children:
            child.active = False

        # Reset form
        for key in self.form:
            if key not in ["todolist_id", "star"]:
                self.form[key] = ""
            if key == "star":
                self.form[key] = False

    def clear_sector_field(self):
        self.ids.climb_form_sector.text = "Sector"
        self.form["sector_id"] = ""
