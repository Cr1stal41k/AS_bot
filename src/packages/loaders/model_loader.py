"""
This one is responsible for loading the necessary models of the _keras_ or _pickle_ type.
"""
from pathlib import Path
import pickle
from keras import models

__all__ = ["ModelLoader"]


class LoadModelException(Exception):
    """
    Exception class for the model loader.
    """


class ModelLoader:
    """
    Model loader class using the __keras__ and __pickle__ libraries.
    """

    _path = ""
    _reading_mode = "rb"
    _encoding = "utf-8"
    _loader_func = None

    def __init__(self, path: str or Path, reading_mode: str = "rb", loader: str = "pickle", encoding: str = "utf-8"):
        """
        Constructor for objects.
        @param path: path to the file with the model.
        @param reading_mode: the mode of reading the file with the model.
        @param reading_mode: file encoding with model.
        """
        self._path = path
        self._reading_mode = reading_mode
        self._encoding = encoding
        if loader == "pickle":
            self._loader_func = self._loader_for_pickle
        elif loader == "keras":
            self._loader_func = self._loader_for_keras
        else:
            raise LoadModelException(f"Invalid parameter – {loader}")

    def load(self) -> any:
        """
        The method loads the model with path and read mode specified during initialization.
        @return: loaded model.
        @raise LoadModelException: if the file with the bot is not found.
        @raise LoadModelException: if unexpected error.
        """
        try:
            model = self._loader_func()
        except FileNotFoundError as exception:
            raise LoadModelException(f"Can't find model file: {exception}.") from exception
        except Exception as exception:
            raise LoadModelException(f"Unexpected error: {exception}.") from exception
        return model

    def _loader_for_pickle(self) -> any:
        """
        The method loads the model with path and read mode by using library __pickle__.
        @return: loaded model.
        """

        # Binary mode doesn't take an encoding argument.
        # pylint: disable=W1514:
        if self._reading_mode == "rb":
            with open(self._path, self._reading_mode) as file:
                model = pickle.load(file)
        else:
            with open(self._path, self._reading_mode, encoding=self._encoding) as file:
                model = pickle.load(file)
        return model

    def _loader_for_keras(self) -> models.Sequential:
        """
        The method loads the `Sequential` model with path by using library __keras__.
        @return: loaded `Sequential` model.
        """
        return models.load_model(self._path)
