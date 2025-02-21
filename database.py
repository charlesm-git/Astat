import os

from alembic.config import Config
from alembic import command

from kivy.utils import platform

from models.grade import Grade

GRADE_ASSOCIATION_DICT = {
    "6a": 1,
    "6a+": 2,
    "6b": 3,
    "6b+": 4,
    "6c": 5,
    "6c+": 6,
    "7a": 7,
    "7a+": 8,
    "7b": 9,
    "7b+": 10,
    "7c": 11,
    "7c+": 12,
    "8a": 13,
    "8a+": 14,
    "8b": 15,
    "8b+": 16,
    "8c": 17,
    "8c+": 18,
    "9a": 19,
}


def get_db_path():
    db_filename = "astat.db"
    if platform == "win":
        data_dir = os.getcwd()
    elif platform == "android":
        # Get Android context
        from jnius import autoclass, cast

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        context = cast("android.content.Context", PythonActivity.mActivity)

        # Get external storage path for your app
        file_p = cast("java.io.File", context.getExternalFilesDir(None))
        data_dir = file_p.getAbsolutePath()

    writable_db_path = os.path.join(data_dir, db_filename)

    return writable_db_path


def run_migrations():
    """Run migrations using Alembic's command API with proper configuration."""
    db_path = get_db_path()

    base_dir = os.path.abspath(os.path.dirname(__file__))
    script_location = os.path.join(base_dir, "migrations")

    # Configure Alembic programmatically
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", script_location)
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")

    # Debug prints
    db_url = alembic_cfg.get_main_option("sqlalchemy.url")
    migrations = os.listdir(os.path.join(script_location, "versions"))
    print(f"database url : {db_url}")
    print(f"migration path: {script_location}")
    print(f"Migration versions: {migrations}")

    try:
        command.upgrade(alembic_cfg, "head")
    except SystemExit as e:
        if e.code != 0:
            print(f"Migration failed with code {e.code}")
            raise


def get_android_documents_path():
    """Returns the absolute path to the user's Documents directory on Android."""
    # Get Android context
    from jnius import autoclass, cast

    Environment = autoclass("android.os.Environment")
    documents_dir = Environment.getExternalStoragePublicDirectory(
        Environment.DIRECTORY_DOCUMENTS
    )
    return documents_dir.getAbsolutePath()


def get_grades_as_object():
    """
    Create and return a list of Grade Objects to initialize the 'grade' table
    in the database
    """
    grades = []
    for grade_value, correspondence in GRADE_ASSOCIATION_DICT.items():
        grades.append(
            Grade(grade_value=grade_value, correspondence=correspondence)
        )
    return grades
