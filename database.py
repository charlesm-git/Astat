import os

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


def get_android_documents_path():
    """Returns the absolute path to the user's Documents directory on Android.
    """
    # Get Android context
    from jnius import autoclass, cast

    Environment = autoclass("android.os.Environment")
    documents_dir = Environment.getExternalStoragePublicDirectory(
        Environment.DIRECTORY_DOWNLOADS
    ).getAbsolutePath()
    return documents_dir


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
