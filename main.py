from kivy.lang import Builder
from views.list import ListApp

Builder.load_file("kv/list.kv")

if __name__ == "__main__":
    ListApp().run()
