from astat import AStatApp
from kivy.config import Config

Config.set("kivy", "log_level", "debug")  # or debug

if __name__ == "__main__":
    AStatApp().run()
