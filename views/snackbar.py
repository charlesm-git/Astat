from kivymd.uix.snackbar import (
    MDSnackbar,
    MDSnackbarText,
    MDSnackbarButtonContainer,
    MDSnackbarCloseButton,
)

from kivy.properties import StringProperty
from kivy.metrics import dp


class CustomSnackbar(MDSnackbar):

    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set Snackbar properties
        self.y = dp(100)
        self.orientation = "horizontal"
        self.pos_hint = {"center_x": 0.5}
        self.size_hint_x = 0.9
        self.duration = 5

        # Add Text
        self.add_widget(MDSnackbarText(text=text, adaptive_size=True))

        # Add Close Button inside a Button Container
        button_container = MDSnackbarButtonContainer()
        close_button = MDSnackbarCloseButton(
            icon="close", on_release=lambda x: self.dismiss()
        )
        button_container.add_widget(close_button)

        self.add_widget(button_container)

    def open(self):
        super().open()
