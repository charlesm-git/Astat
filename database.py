import os
import shutil
import subprocess
from kivy.utils import platform


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

    if not os.path.exists(writable_db_path):
        bundled_db_path = os.path.join(os.path.dirname(__file__), db_filename)
        if os.path.exists(bundled_db_path):
            shutil.copyfile(bundled_db_path, writable_db_path)

    return writable_db_path


def run_migrations():
    """Run Alembic migrations automatically at startup."""
    app_dir = os.path.dirname(__file__)

    migration_command = ["alembic", "upgrade", "head"]
    try:
        subprocess.run(migration_command, check=True, cwd=app_dir)
        print("Database migrations applied successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running migrations: {e}")
