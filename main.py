from kivy.lang import Builder
from views.list import ListApp
# from database.database_setup import initialize_db

Builder.load_file("kv/list.kv")

if __name__ == "__main__":
    # initialize_db()
    ListApp().run()
