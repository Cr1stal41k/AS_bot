"""
Module with the implementation of the main methods for obtaining absolute paths to the main files and directories.
"""
from pathlib import Path
import os

__all__ = ["PathStorage"]


class PathStorage:
    """
    PathStorage class. Allows you to get absolute paths to the main files and directories of the project using the
    __pathlib__ library. All absolute paths are calculated based on the location of this file, if the file is moved
    to a directory above or below in the _packages_ directory, then you need to change the
    `_DEPTH_RELATIVE_TO_PROJECT_ROOT` variable to a value that is responsible for the depth at which the file is
    located relative to the project root.
    """

    _DEPTH_RELATIVE_TO_PROJECT_ROOT = 3
    _ABSOLUTE_PATH_TO_PROJECT_ROOT = Path(__file__).parents[_DEPTH_RELATIVE_TO_PROJECT_ROOT]
    _ABSOLUTE_PATH_TO_SRC = _ABSOLUTE_PATH_TO_PROJECT_ROOT / "src"

    @classmethod
    def get_path_to_project_root(cls) -> Path:
        """
        @return: absolute path to the project root.
        """
        return cls._ABSOLUTE_PATH_TO_PROJECT_ROOT

    @classmethod
    def get_path_to_notebooks(cls) -> Path:
        """
        @return:absolute path to the folder with ipynb notebooks.
        """
        return cls._ABSOLUTE_PATH_TO_PROJECT_ROOT / "notebooks"

    @classmethod
    def get_path_to_setting(cls) -> Path:
        """
        @return: absolute path to the folder with settings files.
        """
        return cls._ABSOLUTE_PATH_TO_PROJECT_ROOT / "settings"

    @classmethod
    def get_path_to_models(cls) -> Path:
        """
        @return: absolute path to the folder with settings files.
        """
        return cls._ABSOLUTE_PATH_TO_PROJECT_ROOT / "models"

    @classmethod
    def get_path_to_src(cls) -> Path:
        """
        @return: absolute path to the source directory.
        """
        return cls._ABSOLUTE_PATH_TO_SRC

    @classmethod
    def get_path_to_packages(cls) -> Path:
        """
        @return: absolute path to the packages directory.
        """
        return cls._ABSOLUTE_PATH_TO_SRC / "packages"

    @classmethod
    def get_path_to_database_file(cls) -> Path:
        """
        @return: absolute path to the packages directory.
        """
        return cls._ABSOLUTE_PATH_TO_SRC / "db" / "db.csv"

    @classmethod
    def does_path_exists(cls, path: str or Path) -> bool:
        """
        @return: true if path exists.
        """
        return os.path.exists(path)

    @classmethod
    def does_file_exists(cls, path_to_file: str or Path) -> bool:
        """
        @return: true if file exists.
        """
        return os.path.isfile(path_to_file)
