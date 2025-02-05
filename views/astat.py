from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window

from views.list import ListScreen
from views.adding import AddingScreen
from views.statistics import StatisticScreen
from views.screenmanager import MainScreenManager

# Window.size = (360, 640)

class AStatApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Darkorange"
        Builder.load_file("kv/list-screen.kv")
        Builder.load_file("kv/adding-screen.kv")
        Builder.load_file("kv/statistic-screen.kv")
        Builder.load_file("kv/screenmanager.kv")
        return MainScreenManager()
