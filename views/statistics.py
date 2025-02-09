from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.divider import MDDivider
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.properties import (
    StringProperty,
    ListProperty,
    BooleanProperty,
    NumericProperty,
)
from kivy.clock import Clock

from statistic.queries import (
    get_ascents_per_area,
    get_ascents_per_grade,
    get_ascents_per_year,
    get_total_ascent,
)


class CustomTitleLabel(MDLabel):
    pass


class TableRow(MDBoxLayout):
    value = StringProperty()
    nbre_of_ascents = StringProperty()
    pourcentage = StringProperty()
    is_header = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Table(MDBoxLayout):
    title = StringProperty()
    table_content = ListProperty([])
    header = ListProperty([])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        horizontal_divider = MDDivider()
        header_row = TableRow(
            value=self.header[0],
            nbre_of_ascents=self.header[1],
            pourcentage=self.header[2],
            is_header=True,
        )
        self.add_widget(header_row)
        self.add_widget(horizontal_divider)
        for value, nbre_of_ascents, pourcentage in self.table_content:
            table_row = TableRow(
                value=value,
                nbre_of_ascents=nbre_of_ascents,
                pourcentage=f"{pourcentage} %",
            )
            horizontal_divider = MDDivider()
            self.add_widget(table_row)
            self.add_widget(horizontal_divider)


class StatisticScreen(MDScreen):
    total_ascents = NumericProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(lambda dt: self.table_update())

    def on_pre_enter(self):
        area_table = self.ids.area_table
        grade_table = self.ids.grade_table
        year_table = self.ids.year_table
        self.ids.scroll_view_content.remove_widget(area_table)
        self.ids.scroll_view_content.remove_widget(grade_table)
        self.ids.scroll_view_content.remove_widget(year_table)
        Clock.schedule_once(lambda dt: self.table_update())

    def table_update(self):
        self.total_ascents = get_total_ascent()
        self.ids.total_ascents.text = str(self.total_ascents)
        self.area_table_instanciation()
        self.grade_table_instanciation()
        self.year_table_instanciation()

    def area_table_instanciation(self):
        area_query = get_ascents_per_area()
        header = ["Area", "Ascents", "Percentage"]
        ascents_per_area = self.add_pourcentage(area_query)
        area_table = Table(
            header=header,
            table_content=ascents_per_area,
            title="Ascent per area",
        )
        self.ids["area_table"] = area_table
        self.ids.scroll_view_content.add_widget(area_table)

    def grade_table_instanciation(self):
        grade_query = get_ascents_per_grade()
        header = ["Grade", "Ascents", "Percentage"]
        ascents_per_grade = self.add_pourcentage(grade_query)
        grade_table = Table(
            header=header,
            table_content=ascents_per_grade,
            title="Ascent per grade",
        )
        self.ids["grade_table"] = grade_table
        self.ids.scroll_view_content.add_widget(grade_table)

    def year_table_instanciation(self):
        year_query = get_ascents_per_year()
        header = ["Year", "Ascents", "Percentage"]
        ascents_per_year = self.add_pourcentage(year_query)
        year_table = Table(
            header=header,
            table_content=ascents_per_year,
            title="Ascent per year",
        )
        self.ids["year_table"] = year_table
        self.ids.scroll_view_content.add_widget(year_table)

    def add_pourcentage(self, query_result):
        updated_filtered_list = []
        for filter_value, ascents in query_result:
            pourcentage = round(ascents / self.total_ascents * 100, 1)
            updated_filtered_list.append(
                [str(filter_value), str(ascents), str(pourcentage)]
            )
        return updated_filtered_list
