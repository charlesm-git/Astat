from kivy.graphics import Color, Rectangle, Line
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.metrics import dp

from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.widget import MDWidget


class BarChart(MDWidget):
    data = ListProperty()
    data_type = StringProperty()
    bar_height = NumericProperty(80)
    gap = NumericProperty(20)

    def __init__(self, **kwargs):
        super(BarChart, self).__init__(**kwargs)

    def update_height(self):
        self.height = (len(self.data) + 1) * (self.bar_height + self.gap)

    def redraw(self, *args):
        self.canvas.clear()
        self.clear_widgets()
        self.update_height()

        # Determine bar layout
        left_side = self.center_x - self.width / 2

        # Scaling: find maximum value among both sides
        max_value = max(
            group["redpoint"] + group["flash"] for group in self.data
        )

        current_y = self.height - self.bar_height
        for group in self.data:
            redpoint_val = group["redpoint"]
            flash_val = group["flash"]

            label = BarChartLabel(
                text=str(group["label"]), data_type=self.data_type
            )
            label.pos = (left_side, current_y)
            self.add_widget(label)

            bar_start = left_side + label.width
            bar_end = self.center_x + self.width / 2 - dp(30)

            scale = (bar_end - bar_start) / max_value if max_value else 1

            with self.canvas:
                redpoint_width = redpoint_val * scale
                Color(0.969, 0.306, 0.306)
                Rectangle(
                    pos=(bar_start, current_y),
                    size=(redpoint_width, self.bar_height),
                )
                flash_width = flash_val * scale
                Color(0.961, 0.922, 0.365)
                Rectangle(
                    pos=(bar_start + redpoint_width, current_y),
                    size=(flash_width, self.bar_height),
                )
            current_y -= self.bar_height + self.gap

        x_tick = []
        x_tick.append({"pos": bar_end, "value": max_value})
        x_tick.append({"pos": bar_start, "value": 0})

        if max_value <= 5:
            pass
        elif 5 < max_value < 10:
            number_of_division = 2
            division = max_value // number_of_division
            x_tick.append(
                {
                    "pos": bar_start + division * scale,
                    "value": division,
                }
            )
        else:
            number_of_division = 3
            division = max_value // number_of_division
            x_tick.append(
                {
                    "pos": bar_start + division * scale,
                    "value": division,
                }
            )
            x_tick.append(
                {
                    "pos": bar_start + (max_value - division) * scale,
                    "value": max_value - division,
                }
            )

        with self.canvas:
            Color(0, 0, 0)
            for x in x_tick:
                Line(
                    points=[
                        x["pos"],
                        current_y + self.bar_height + self.gap,
                        x["pos"],
                        self.height,
                    ],
                    width=dp(1),
                )

        for x in x_tick:
            tick = BarChartTick(text=str(x["value"]))
            tick.pos = (x["pos"] - tick.width / 2, current_y)
            self.add_widget(tick)


class BarChartLabel(MDLabel):
    data_type = StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BarChartTick(MDLabel):
    pass


class Graph(MDBoxLayout):
    pass
