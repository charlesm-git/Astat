from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivy.clock import Clock

from kivy.properties import StringProperty, NumericProperty
from sqlalchemy import select

from models.todolist import ToDoList


class ToDoListScreen(MDScreen):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(lambda *args: self.init_list())

    def on_pre_enter(self):
        Clock.schedule_once(lambda *args: self.init_list())

    def init_list(self):
        with MDApp.get_running_app().get_db_session() as session:
            todolists = (
                session.scalars(select(ToDoList).order_by(ToDoList.name)).all()
            )
            scroll_view = self.ids.scroll_view_content
            scroll_view.clear_widgets()
            for todolist in todolists:
                todolist_item = ToDoListItem(
                    title=todolist.name,
                    todolist_id=todolist.id,
                )
                scroll_view.add_widget(todolist_item)


class ToDoListItem(MDCard):
    title = StringProperty()
    todolist_id = NumericProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.screen_manager = MDApp.get_running_app().root.ids.screen_manager

    def open_todolist_detail(self):
        todolist_detail_screen = self.screen_manager.get_screen(
            "todolist-detail"
        )
        todolist = ToDoList.get_from_id(self.todolist_id)

        todolist_detail_screen.todolist = todolist
        todolist_detail_screen.todolist_name = todolist.name
        self.screen_manager.current = "todolist-detail"

    # def open_option_menu(self, item):
    #     menu_items = [
    #         {"text": "Delete", "on_release": lambda: self.delete_item()},
    #         {"text": "Update", "on_release": lambda: self.update_item()},
    #     ]
    #     self.option_menu = MDDropdownMenu(
    #         caller=item,
    #         items=menu_items,
    #         max_height=dp(200),
    #         width=dp(180),
    #         position="bottom",
    #         hor_growth="right",
    #     )
    #     self.option_menu.open()

    def delete_item(self):
        ToDoList.delete(self.todolist_id)
        self.option_menu.dismiss()
        self.refresh_callback(self)
