from kivymd.app import MDApp
from views.list import ListScreen
from views.addascent import AddAscentScreen

class AStatApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Darkred"
        return ListScreen()
