from kivy.lang import Builder
from views.astat import AStatApp
# from database.database_setup import initialize_db

Builder.load_file("kv/list.kv")
Builder.load_file("kv/addascent.kv")

if __name__ == "__main__":
    # initialize_db()
    AStatApp().run()
