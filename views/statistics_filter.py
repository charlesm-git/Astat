from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock

from models.grade import Grade


class StatisticFilterScreen(MDScreen):
    """Definition of the statistic filtering screen"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(lambda x: self.binds())

    def on_pre_enter(self, *args):
        self.ids.area_selector.selected_area = (
            MDApp.get_running_app().root.selected_area
        )

    def binds(self, *args):
        """Bind the grades sliders with their label display"""
        min_grade_selector = self.ids.min_grade_selector
        min_grade_selector.ids.slider.bind(
            value_pos=lambda *args: self.grade_label_update(min_grade_selector)
        )

        max_grade_selector = self.ids.max_grade_selector
        max_grade_selector.ids.slider.bind(
            value_pos=lambda *args: self.grade_label_update(max_grade_selector)
        )

    def grade_label_update(self, grade_selector):
        grade = Grade.get_grade_value_from_correspondence(
            grade_selector.ids.slider.value + 1
        )
        grade_selector.ids.grade_value.text = grade

    def validate_filter(self):
        """Update the StatisticScreen attributes based on the user filtering
        selection (both with grades and area)"""

        statistic_screen = self.manager.get_screen("statistic")
        statistic_screen.min_grade_filter = (
            self.ids.min_grade_selector.ids.slider.value + 1
        )
        statistic_screen.max_grade_filter = (
            self.ids.max_grade_selector.ids.slider.value + 1
        )
        statistic_screen.area_filter = (
            self.ids.area_selector.ids.selected_area.text
        )
        self.manager.current = "statistic"

    def clear_field(self):
        """Reset all the filtering fields"""
        self.ids.min_grade_selector.ids.slider.value = 0
        self.ids.max_grade_selector.ids.slider.value = 18
        self.ids.area_selector.ids.selected_area.text = "All"
