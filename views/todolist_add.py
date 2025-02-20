from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.clock import Clock

from models.todolist import ToDoList
from views.snackbar import CustomSnackbar


class ToDoListAddScreen(MDScreen):
    """Screen to add an ToDoList to the database"""

    todolist_to_update_id = NumericProperty(None, allownone=True)
    todolist_to_update = ObjectProperty(None, allownone=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_pre_enter(self):
        if self.todolist_to_update_id:
            self.todolist_to_update = ToDoList.get_from_id(
                self.todolist_to_update_id
            )
            self.ids.todolist_form_name.text = self.todolist_to_update.name

    def on_leave(self):
        self.todolist_to_update = None
        self.todolist_to_update_id = None

    def clear_field(self):
        self.ids.todolist_form_name.text = ""

    def submit(self):
        """Configure the actions performed when the form is submitted"""
        todolist_name = self.ids.todolist_form_name.text
        # If no name is provided, notify the user and return
        if todolist_name == "":
            self.show_snackbar(text="Form Incomplete")
            return
        if len(todolist_name) > 32:
            self.show_snackbar(text="Name entered too long")
            return

        if not self.todolist_to_update:
            todolist = ToDoList.create(name=todolist_name)
            self.show_snackbar(text="List created successfully")

        else:
            self.todolist_to_update.update(name=todolist_name)
            self.show_snackbar(text="Name modified successfully")
            todolist = self.todolist_to_update

        # Setup the to-do list detail view and switch to it after creation
        todolist_detail_screen = self.manager.get_screen("todolist-detail")
        todolist_detail_screen.todolist = todolist
        todolist_detail_screen.todolist_name = todolist.name

        self.manager.current = "todolist-detail"
        self.clear_field()

    def show_snackbar(self, text):
        snackbar = CustomSnackbar(text=text)
        snackbar.open()
