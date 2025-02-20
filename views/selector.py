from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.slider import MDSlider
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.metrics import dp
from sqlalchemy import select

from models.area import Area


class AreaSelector(MDBoxLayout):
    on_area_selected = ObjectProperty(None, allownone=True)
    selected_area = StringProperty("All")

    def area_selection(self, item):
        """Function for grade dropdown menu configuration and opening"""
        with MDApp.get_running_app().get_db_session() as session:
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
        screen_manager = MDApp.get_running_app().root
        self.selected_area = area_name
        screen_manager.selected_area = self.selected_area
        self.area_selector.dismiss()

        if callable(self.on_area_selected):
            self.on_area_selected()


class GradeSelector(MDBoxLayout):
    title = StringProperty()
    starting_grade_value = StringProperty()
    starting_slider_value = NumericProperty()


class GradeSlider(MDSlider):
    pass
