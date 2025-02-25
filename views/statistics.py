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
from kivymd.app import MDApp
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
    """Custom title. Configured in .kv"""

    pass


class TableRow(MDBoxLayout):
    """
    Configure the display of one row of a table.
    Uses TableCell defined in .kv
    """

    value = StringProperty()
    ascents = StringProperty()
    flash = StringProperty()
    is_header = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Table(MDBoxLayout):
    """3 columns Table to display data. Uses TableRow"""

    title = StringProperty("")
    content = ListProperty([["", "", ""]])
    header = ListProperty(["", "", ""])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update_table(self, *args):
        """
        Updates the content of the table from the current attributes definition
        """
        # Clears the content of the table
        for child in self.children[:]:
            if not isinstance(child, CustomTitleLabel):
                self.remove_widget(child)

        # Define the header
        header_row = TableRow(
            value=self.header[0],
            ascents=self.header[1],
            flash=self.header[2],
            is_header=True,
        )
        self.add_widget(header_row)

        # MDDivider used to draw a line between each row
        self.add_widget(MDDivider())

        # Using the current attribute definitions, creates the TableRow and add
        # them to the table
        for (
            value,
            ascents,
            flash,
        ) in self.content:
            table_row = TableRow(
                value=value,
                ascents=ascents,
                flash=flash,
            )
            self.add_widget(table_row)
            self.add_widget(MDDivider())


class CustomTableTab(MDScrollView):
    """Tab used to display tables. Used by MDTabs"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class GeneralInfoTab(MDBoxLayout):
    """Table used to display general information. Used by MDTabs"""

    total_number_of_ascent = StringProperty()
    average_grade = StringProperty()
    total_number_of_flash = StringProperty()
    average_flash_grade = StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class StatisticScreen(MDScreen):
    """
    Screen displaying statistics.

    Contains :
    - 4 tabs to display general informations and tables (statistics per area,
    grade and year)
    - A floating button to go to the filter screen
    """

    total_ascents = NumericProperty(0)
    total_flash = NumericProperty(0)
    min_grade_filter = NumericProperty(1)
    max_grade_filter = NumericProperty(19)
    area_filter = StringProperty("All")

    tab_general = ObjectProperty()
    tab_grade = ObjectProperty()
    tab_year = ObjectProperty()
    tab_area = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(lambda dt: self.tab_init())

    def on_pre_enter(self):
        """
        Actions performed when entering the screen :
        - Update of the filter display based on the current filtering setup
        - Update of the statistic carousel by calling update_carousel()
        """
        min_grade_value = Grade.get_grade_value_from_correspondence(
            self.min_grade_filter
        )
        max_grade_value = Grade.get_grade_value_from_correspondence(
            self.max_grade_filter
        )
        self.area_filter = MDApp.get_running_app().root.selected_area
        self.ids.filter_display.text = (
            f"Grades : ({min_grade_value} - {max_grade_value})"
            f"   /   Area : {self.area_filter}"
        )

        Clock.schedule_once(lambda dt: self.carousel_update())

    def tab_init(self, *args):
        """
        Initialise the tab display with 4 tabs.
        The content of the carousel is initialised empty and updated when
        entering the screen (see on_pre_enter()).
        """

        # Setup the tab bar
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

        # Setup the carousel
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
        """
        Update the content of the carousel with the current filters
        """
        # Update the total number of ascents
        self.total_ascents, self.total_flash = get_total_ascent(
            min_grade_correspondence=self.min_grade_filter,
            max_grade_correpondence=self.max_grade_filter,
            area=self.area_filter,
        )
        # Update the average grade
        average_grade, average_flash_grade = get_average_grade(
            min_grade_correspondence=self.min_grade_filter,
            max_grade_correpondence=self.max_grade_filter,
            area=self.area_filter,
        )

        self.ids.general_tab.total_number_of_ascent = str(self.total_ascents)
        self.ids.general_tab.total_number_of_flash = str(self.total_flash)

        if average_grade:
            self.ids.general_tab.average_grade = average_grade
        else:
            self.ids.general_tab.average_grade = "Not defined"

        if average_flash_grade:
            self.ids.general_tab.average_flash_grade = average_flash_grade
        else:
            self.ids.general_tab.average_flash_grade = "Not defined"

        # Update the content of the tables

        # Get the data from the database from the filters
        area_table_header, area_table_content, area_table_title = (
            self.area_table_instanciation()
        )
        grade_table_header, grade_table_content, grade_table_title = (
            self.grade_table_instanciation()
        )
        year_table_header, year_table_content, year_table_title = (
            self.year_table_instanciation()
        )

        # Build the lists for tables update
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

        # Update the tables
        for header, content, title, table in zip(
            headers, contents, titles, tables
        ):
            table.header = header
            table.content = content
            table.title = title
            table.update_table()

    def grade_table_instanciation(self):
        """Get from the database the informations related to the GRADE table
        based on the current filters"""
        grade_query = get_ascents_per_grade(
            min_grade_correspondence=self.min_grade_filter,
            max_grade_correpondence=self.max_grade_filter,
            area=self.area_filter,
        )
        header = ["Grade", "Ascents", "Flash"]
        ascents_per_grade = self.add_pourcentage(grade_query)
        title = "Ascent per grade"

        return header, ascents_per_grade, title

    def year_table_instanciation(self):
        """Get from the database the informations related to the YEAR table
        based on the current filters"""
        year_query = get_ascents_per_year(
            min_grade_correspondence=self.min_grade_filter,
            max_grade_correpondence=self.max_grade_filter,
            area=self.area_filter,
        )
        header = ["Year", "Ascents", "Flash"]
        ascents_per_year = self.add_pourcentage(year_query)
        title = "Ascent per year"
        return header, ascents_per_year, title

    def area_table_instanciation(self):
        """Get from the database the informations related to the AREA table
        based on the current filters"""
        area_query = get_ascents_per_area(
            min_grade_correspondence=self.min_grade_filter,
            max_grade_correpondence=self.max_grade_filter,
            area=self.area_filter,
        )
        header = ["Area", "Ascents", "Flash"]
        ascents_per_area = self.add_pourcentage(area_query)
        title = "Ascent per area"

        return header, ascents_per_area, title

    def add_pourcentage(self, query_result):
        """Add a pourcentage column to the database query result"""
        updated_filtered_list = []
        for filter_value, ascents, flashes in query_result:
            ascent_pourcentage = round(ascents / self.total_ascents * 100, 1)
            flash_pourcentage = round(flashes / ascents * 100, 1)
            updated_filtered_list.append(
                [
                    str(filter_value),
                    str(ascents),
                    str(flashes),
                ]
            )
        return updated_filtered_list
