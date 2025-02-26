from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.properties import ListProperty
from kivy.metrics import dp


class PopulationPyramid(Widget):
    # Example data: each dict represents an age group with male and female values.
    data = ListProperty(
        [
            {"age": "0-9", "male": 10, "female": 12},
            {"age": "10-19", "male": 20, "female": 18},
            {"age": "20-29", "male": 30, "female": 28},
            {"age": "30-39", "male": 25, "female": 27},
            {"age": "40-49", "male": 15, "female": 14},
            {"age": "50-59", "male": 5, "female": 6},
        ]
    )

    def __init__(self, **kwargs):
        super(PopulationPyramid, self).__init__(**kwargs)
        self.bind(pos=self.redraw, size=self.redraw, data=self.redraw)
        self.redraw()

    def redraw(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Draw central vertical axis
            mid_x = self.center_x
            
            # Determine bar layout
            n = len(self.data)
            gap = dp(5)
            bar_height = (self.height - gap * (n + 1)) / n

            # Scaling: find maximum value among both sides
            max_value = max(
                max(group["male"], group["female"]) for group in self.data
            )
            # Available width for each side (left/right)
            side_width = (self.width / 2) - dp(20)
            scale = side_width / max_value if max_value else 1

            current_y = self.y + gap
            for group in self.data:
                male_val = group["male"]
                female_val = group["female"]

                # Draw male bar (left side) in blue
                male_width = male_val * scale
                Color(0, 0, 0, 0.7)
                Rectangle(
                    pos=(mid_x - male_width, current_y),
                    size=(male_width, bar_height),
                )

                # Draw female bar (right side) in red
                female_width = female_val * scale
                Color(0, 0, 0, 0.4)
                Rectangle(
                    pos=(mid_x, current_y), size=(female_width, bar_height)
                )

                # Optionally, you could add labels here (requires extra widget or canvas instructions)

                current_y += bar_height + gap
