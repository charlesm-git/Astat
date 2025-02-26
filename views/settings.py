import os
import shutil

from kivymd.uix.screen import MDScreen

from views.snackbar import CustomSnackbar
from models.area import Area
from database import get_android_documents_path, get_db_path


class SettingsScreen(MDScreen):
    """Screen class for adding ascents"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_area_screen(self):
        location_screen = self.manager.get_screen("location")
        location_screen.model_class = Area
        self.manager.current = "location"

    def import_db_as_db_file(self):
        document_path = get_android_documents_path()
        db_document_url = os.path.join(document_path, "astat.db")

        if not os.path.exists(db_document_url):
            self.show_snackbar(
                text="No file named astat.db found in your downloads folder\n"
            )
            return

        database = get_db_path()
        shutil.copy(db_document_url, database)

        self.show_snackbar(text="Database copied from the download folder")

    def export_db_as_db_file(self):
        document_path = get_android_documents_path()
        db_copy_url = os.path.join(document_path, "astat.db")
        database = get_db_path()

        shutil.copy(database, db_copy_url)

        self.show_snackbar(text="Database copied to the download folder")

    def show_snackbar(self, text):
        """Function displaying a snackbar for user feedback"""
        snackbar = CustomSnackbar(text=text)
        snackbar.open()
