from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.divider import MDDivider
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.tab import (
    MDTabsItem,
    MDTabsItemIcon,
    MDTabsItemText,
)
from kivy.properties import (
    StringProperty,
    ListProperty,
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
)
from kivy.clock import Clock

from models.grade import Grade
from statistic.queries import (
    get_ascents_per_area,
    get_ascents_per_grade,
    get_ascents_per_year,
    get_total_ascent,
    get_average_grade,
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
    title = StringProperty("")
    content = ListProperty([["", "", ""]])
    header = ListProperty(["", "", ""])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update_table(self, *args):

        for child in self.children[:]:
            if not isinstance(child, CustomTitleLabel):
                self.remove_widget(child)

        header_row = TableRow(
            value=self.header[0],
            nbre_of_ascents=self.header[1],
            pourcentage=self.header[2],
            is_header=True,
        )
        self.add_widget(header_row)
        self.add_widget(MDDivider())
        for value, nbre_of_ascents, pourcentage in self.content:
            table_row = TableRow(
                value=value,
                nbre_of_ascents=nbre_of_ascents,
                pourcentage=f"{pourcentage} %",
            )
            self.add_widget(table_row)
            self.add_widget(MDDivider())


class CustomTableTab(MDScrollView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class GeneralInfoTab(MDBoxLayout):
    total_number_of_ascent = StringProperty()
    average_grade = StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class StatisticScreen(MDScreen):
    total_ascents = NumericProperty(0)
    min_grade_filter = NumericProperty(1)
    max_grade_filter = NumericProperty(19)
    area_filter = StringProperty()

    tab_general = ObjectProperty()
    tab_grade = ObjectProperty()
    tab_year = ObjectProperty()
    tab_area = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.area_filter = self.manager.area_filter
        Clock.schedule_once(lambda dt: self.tab_init())

    def on_pre_enter(self):
        min_grade_value = Grade.get_grade_value_from_correspondence(
            self.min_grade_filter
        )
        max_grade_value = Grade.get_grade_value_from_correspondence(
            self.max_grade_filter
        )
        self.ids.filter_display.text = f"Grades : ({min_grade_value} - {max_grade_value})   /   Area : {self.area_filter}"

        Clock.schedule_once(lambda dt: self.carousel_update())

    def tab_init(self, *args):
        tabs = {
            "General": "clipboard-text-outline",
            "Grade": "speedometer",
            "Year": "calendar-range",
            "Area": "earth",
        }

        for tab_name, tab_icon in tabs.items():
            self.ids.tabs.add_widget(
                MDTabsItem(
                    MDTabsItemIcon(icon=tab_icon),
                    MDTabsItemText(text=tab_name),
                )
            )

        carousel = self.ids.carousel

        general_tab = GeneralInfoTab(
            total_number_of_ascent=str(self.total_ascents)
        )
        carousel.add_widget(general_tab)
        self.ids["general_tab"] = general_tab

        grade_tab = CustomTableTab()
        carousel.add_widget(grade_tab)
        self.ids["grade_tab"] = grade_tab

        year_tab = CustomTableTab()
        carousel.add_widget(year_tab)
        self.ids["year_tab"] = year_tab

        area_tab = CustomTableTab()
        carousel.add_widget(area_tab)
        self.ids["area_tab"] = area_tab

    def carousel_update(self):

        self.total_ascents = get_total_ascent(
            min_grade_correspondence=self.min_grade_filter,
            max_grade_correpondence=self.max_grade_filter,
            area=self.area_filter,
        )
        average_grade = get_average_grade(
            min_grade_correspondence=self.min_grade_filter,
            max_grade_correpondence=self.max_grade_filter,
            area=self.area_filter,
        )
        self.ids.general_tab.total_number_of_ascent = str(self.total_ascents)
        self.ids.general_tab.average_grade = average_grade

        area_table_header, area_table_content, area_table_title = (
            self.area_table_instanciation()
        )
        grade_table_header, grade_table_content, grade_table_title = (
            self.grade_table_instanciation()
        )
        year_table_header, year_table_content, year_table_title = (
            self.year_table_instanciation()
        )

        headers = [
            grade_table_header,
            year_table_header,
            area_table_header,
        ]
        contents = [
            grade_table_content,
            year_table_content,
            area_table_content,
        ]
        titles = [
            grade_table_title,
            year_table_title,
            area_table_title,
        ]
        tables = [
            self.ids.grade_tab.ids.table,
            self.ids.year_tab.ids.table,
            self.ids.area_tab.ids.table,
        ]

        for header, content, title, table in zip(
            headers, contents, titles, tables
        ):
            table.header = header
            table.content = content
            table.title = title
            table.update_table()

    def grade_table_instanciation(self):
        grade_query = get_ascents_per_grade(
            min_grade_correspondence=self.min_grade_filter,
            max_grade_correpondence=self.max_grade_filter,
            area=self.area_filter,
        )
        header = ["Grade", "Ascents", "Percentage"]
        ascents_per_grade = self.add_pourcentage(grade_query)
        title = "Ascent per grade"

        return header, ascents_per_grade, title

    def year_table_instanciation(self):
        year_query = get_ascents_per_year(
            min_grade_correspondence=self.min_grade_filter,
            max_grade_correpondence=self.max_grade_filter,
            area=self.area_filter,
        )
        header = ["Year", "Ascents", "Percentage"]
        ascents_per_year = self.add_pourcentage(year_query)
        title = "Ascent per year"
        return header, ascents_per_year, title

    def area_table_instanciation(self):
        area_query = get_ascents_per_area(
            min_grade_correspondence=self.min_grade_filter,
            max_grade_correpondence=self.max_grade_filter,
            area=self.area_filter,
        )
        header = ["Area", "Ascents", "Percentage"]
        ascents_per_area = self.add_pourcentage(area_query)
        title = "Ascent per area"

        return header, ascents_per_area, title

    def add_pourcentage(self, query_result):
        updated_filtered_list = []
        for filter_value, ascents in query_result:
            pourcentage = round(ascents / self.total_ascents * 100, 1)
            updated_filtered_list.append(
                [str(filter_value), str(ascents), str(pourcentage)]
            )
        return updated_filtered_list
