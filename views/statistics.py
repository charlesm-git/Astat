from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty
from kivy.clock import Clock

from utils.calculation import get_total_ascent
from utils.plotmaker import (
    graph_ascent_per_area,
    graph_ascent_per_grade,
    graph_ascent_per_year,
)


class GraphBlock(MDBoxLayout):
    title = StringProperty()
    image_link = StringProperty()
    image_path = StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def reload(self):
        self.ids.image.reload()


class StatisticScreen(MDScreen):
    _initialised = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(lambda dt: self.graph_update())
        self._initialised = True

    def on_enter(self):
        if self._initialised:
            Clock.schedule_once(lambda dt: self.graph_update())

    def graph_update(self):
        self.ids.total_ascent_input.text = str(get_total_ascent())
        graph_ascent_per_area()
        graph_ascent_per_grade()
        graph_ascent_per_year()
        self.ids.graph_ascent_per_area.reload()
        self.ids.graph_ascent_per_grade.reload()
        self.ids.graph_ascent_per_year.reload()
