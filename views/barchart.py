from kivymd.app import MDApp
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.properties import ListProperty, NumericProperty
from kivy.metrics import dp
from kivy.clock import Clock

from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.widget import MDWidget


class BarChart(MDWidget):
    # Example data: each dict represents an group with ascent and flash values.
    data = ListProperty(
        [
            {"label": "6c+", "ascent": 1, "flash": 1},
            {"label": "7a", "ascent": 30, "flash": 20},
            {"label": "7a+", "ascent": 10, "flash": 1},
            {"label": "7b", "ascent": 9, "flash": 3},
            {"label": "7b+", "ascent": 5, "flash": 2},
            {"label": "7c", "ascent": 6, "flash": 10},
            {"label": "7c+", "ascent": 2, "flash": 0},
            {"label": "8a", "ascent": 1, "flash": 5},
        ]
    )
    bar_height = NumericProperty(25)
    gap = NumericProperty(5)

    def __init__(self, **kwargs):
        super(BarChart, self).__init__(**kwargs)
        Clock.schedule_once(lambda x: self.update_height())
        self.redraw()

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
            group["ascent"] + group["flash"] for group in self.data
        )

        current_y = 0
        for group in self.data:
            ascent_val = group["ascent"]
            flash_val = group["flash"]

            label = BarChartLabel(text=group["label"])
            label.pos = (left_side, current_y)
            self.add_widget(label)

            bar_start = left_side + label.width
            bar_end = self.center_x + self.width / 2 - dp(30)

            scale = (bar_end - bar_start) / max_value if max_value else 1

            with self.canvas:
                ascent_width = ascent_val * scale
                Color(0.969, 0.306, 0.306)
                Rectangle(
                    pos=(bar_start, current_y),
                    size=(ascent_width, self.bar_height),
                )

                # Draw flash bar (right side) in red
                flash_width = flash_val * scale
                Color(0.961, 0.922, 0.365)
                Rectangle(
                    pos=(bar_start + ascent_width, current_y),
                    size=(flash_width, self.bar_height),
                )

            # Optionally, you could add labels here (requires extra widget or canvas instructions)
            current_y += self.bar_height + self.gap

        division = max_value // 4
        x_tick = [
            {
                "pos": bar_start + (index * division) * scale,
                "value": index * division,
            }
            for index in range(1, 4)
        ]
        x_tick.append({"pos": bar_end, "value": max_value})
        x_tick.append({"pos": bar_start, "value": 0})
        with self.canvas:
            Color(0, 0, 0)
            for x in x_tick:
                Line(points=[x["pos"], current_y, x["pos"], 0], width=dp(1))

        for x in x_tick:
            tick = BarChartTick(text=str(x["value"]))
            tick.pos = (x["pos"] - tick.width / 2, current_y)
            self.add_widget(tick)


class BarChartLabel(MDLabel):
    pass


class BarChartTick(MDLabel):
    pass

class Graph(MDBoxLayout):
    pass