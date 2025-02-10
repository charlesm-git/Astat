from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.slider import MDSlider
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.metrics import dp
from sqlalchemy import select

from models.area import Area
from models.grade import Grade
from database.database import Session


class AreaSelector(MDBoxLayout):
    on_area_selected = ObjectProperty(None, allownone=True)

    def area_selection(self, item):
        """Function for grade dropdown menu configuration and opening"""
        with Session() as session:
            areas = session.scalars(select(Area).order_by(Area.name)).all()

        menu_items = [
            {
                "text": "All",
                "on_release": lambda: self.area_selection_callback(
                    "All",
                ),
            }
        ]
        for area in areas:
            menu_items.append(
                {
                    "text": f"{area.name}",
                    "on_release": lambda a=area: self.area_selection_callback(
                        a.name,
                    ),
                }
            )

        # Setup of the dropdown menu
        self.area_selector = MDDropdownMenu(
            caller=item,
            items=menu_items,
            max_height=dp(200),
            width=dp(180),
            position="bottom",
            hor_growth="right",
        )
        self.area_selector.open()

    def area_selection_callback(self, area_name):
        """
        Function called when an area is selected.
        Updated the area displayed on the label
        """
        self.ids.selected_area.text = area_name
        self.area_selector.dismiss()

        if callable(self.on_area_selected):
            self.on_area_selected()


class GradeSelector(MDBoxLayout):
    title = StringProperty()
    starting_grade_value = StringProperty()
    starting_slider_value = NumericProperty()


class GradeSlider(MDSlider):
    def map_value_to_grade(self, value):
        # Define a mapping from slider value to climbing grade.
        # Adjust the mapping as needed.
        with Session() as session:
            grades = session.scalars(select(Grade.grade_value)).all()
        # Assume slider value is between 0 and len(grades)-1.
        index = int(round(value))
        index = max(0, min(index, len(grades) - 1))
        return grades[index]

    def on_value_pos(self, *args):
        """Override the default update of the value label.
        Instead of displaying an integer value, show a climbing grade.
        """
        self._update_points()

        if self._value_label and self._value_container:
            # Clear the current text, then set it to the mapped climbing grade.
            self._value_label.text = ""
            grade = self.map_value_to_grade(self.value)
            self._value_label.text = grade
            self._value_label.texture_update()
            # Update the texture in the value label container.
            # The group name is set in the MDSliderValueLabel rule.
            label_value_rect = self._value_container.canvas.get_group(
                "md-slider-label-value-rect"
            )[0]
            label_value_rect.texture = None
            label_value_rect.texture = self._value_label.texture
            label_value_rect.size = self._value_label.texture_size

        grade_value = self.value + 1
