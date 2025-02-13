import os
import shutil
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from kivymd.app import MDApp

# is_test = os.getenv("TEST_ENV", "false").lower == "true"

# # Load the appropriate .env file
# if not is_test:
#     load_dotenv()  # Load .env for normal app usage.

# DATABASE_URL = os.getenv("DATABASE_URL")
# SENTRY_DSN = os.getenv("SENTRY_DSN")
# JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")


def get_db_path():
    db_filename = "ascents.db"
    app = MDApp.get_running_app()
    user_data_dir = app.user_data_dir
    db_path = os.path.join()(user_data_dir, db_filename)

    if not os.path.exists(db_path):
        bundled_db_path = os.path.join(os.path.dirname(__file__), db_filename)
        if os.path.exists(bundled_db_path):
            shutil.copy(bundled_db_path, db_path)

    return db_path


db_path = get_db_path()

DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(DATABASE_URL, echo=False)

session_factory = sessionmaker(bind=engine)

Session = scoped_session(session_factory)
