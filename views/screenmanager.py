from kivymd.uix.navigationbar import MDNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.transition import MDFadeSlideTransition
from kivy.properties import StringProperty


class BaseMDNavigationItem(MDNavigationItem):
    icon = StringProperty()
    text = StringProperty()
    name = StringProperty()


class MainScreenManager(MDBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_switch_tabs(self, item: BaseMDNavigationItem):
        self.ids.screen_manager.current = item.name
