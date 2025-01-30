from kivy.lang import Builder
from kivymd.app import MDApp

from views.list import ListScreen
from views.addascent import AddAscentScreen
from views.statistics import StatisticsScreen
from views.screenmanager import MainScreenManager


class AStatApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Darkred"
        Builder.load_file("kv/list.kv")
        Builder.load_file("kv/addascent.kv")
        Builder.load_file("kv/statistics.kv")
        Builder.load_file("kv/screenmanager.kv")
        return StatisticsScreen()
