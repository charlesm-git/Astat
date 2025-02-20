from kivymd.uix.screen import MDScreen

from models.area import Area


class SettingsScreen(MDScreen):
    """Screen class for adding ascents"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_area_screen(self):
        location_screen = self.manager.get_screen("area")
        location_screen.model_class = Area
        self.manager.current = "area"
