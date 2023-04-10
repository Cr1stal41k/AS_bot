"""
This module operation all bot operations: loading models, get intent, answer and so on.
"""
from typing import Union
import re
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import SGD
from nltk.corpus import stopwords
from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance_seqs

# import pyaspeller todo: library not installed, unable to resolve dependencies for this project
import pymorphy2
import numpy as np
import nltk
from src.packages.loaders import ModelLoader
from src.packages.path_storage.path_storage import PathStorage
from src.packages.loaders import config


class ChatModelException(Exception):
    """
    Class-exception for any errors with config loading.
    """


class ChatModel:
    """
    Class ChatModel responding for all bots operations.
    """

    _DICTIONARY_PATH = PathStorage.get_path_to_models() / "words.pkl"
    _DICTIONARY_READING_MODE = "rb"
    _INTENTS_PATH = PathStorage.get_path_to_models() / "intents.pkl"
    _INTENTS_READING_MODE = "rb"
    _PERCEPTRON_PATH = PathStorage.get_path_to_models() / "perceptron.h5"

    _dictionary = None
    _intents = None
    _perceptron = None

    _lemmatizer = pymorphy2.MorphAnalyzer()

    # __speller = pyaspeller.YandexSpeller()

    # ------- Initialization and loading area -------
    def __init__(self, dictionary: any = None, intents: any = None, perceptron: any = None) -> None:
        """
        Class initialization with loading models.
        @param dictionary: custom class responsible for loading dictionary.
        @param intents: custom class responsible for loading intents.
        @param perceptron: custom class responsible for loading perceptron.
        """
        self._download_nltk_data()
        self._load_dictionary(dictionary)
        self._load_intents(intents)
        self._load_perceptron(perceptron)

    @staticmethod
    def _download_nltk_data():
        nltk.download("punkt")
        nltk.download("stopwords")

    def _load_dictionary(self, dictionary: any) -> None:
        """
        Loading dictionary, if it does not exists.
        @param dictionary: custom class responsible for loading dictionary.
        """
        if dictionary is None:
            dictionary_loader = ModelLoader(self._DICTIONARY_PATH, self._DICTIONARY_READING_MODE)
            self._dictionary = dictionary_loader.load()
        else:
            self._dictionary = dictionary

    def _load_intents(self, intents: any) -> None:
        """
        Loading intents, if it does not exists.
        @param intents: custom class responsible for loading intents.
        """
        if intents is None:
            intents_loader = ModelLoader(self._INTENTS_PATH, self._INTENTS_READING_MODE)
            self._intents = intents_loader.load()
        else:
            self._intents = intents

    def _load_perceptron(self, perceptron: any) -> None:
        """
        Loading perceptron, if it does not exists.
        @param  perceptron: custom class responsible for loading perceptron.
        @raise LoadModelException: if unexpected error.
        """
        if perceptron is None:
            perceptron_loader = ModelLoader(self._PERCEPTRON_PATH, loader="keras")
            self._perceptron = perceptron_loader.load()
        else:
            self._perceptron = perceptron

    # ------- Service functions area -------
    @staticmethod
    def _remove_garbage(raw_text: str) -> str:
        """
        Removing garbage (any characters not from the Russian and English alphabets, numbers a etc.) from text.
        @param raw_text: text to be processed.
        @return: processed text containing only letters and spaces.
        """
        return re.sub("[^А-Яа-яA-Za-z- ]", "", raw_text)

    @staticmethod
    def _tokenize(raw_text: str) -> list:
        """
        Tokenizing text.
        @param raw_text: text to be processed.
        @return: list with words.
        """
        raw_text = raw_text.lower()
        tokens = nltk.word_tokenize(raw_text)
        return tokens

    # def _correct_orthography(self, sentence: str) -> str:
    #     """
    #     Checks and corrects spelling errors in sentences.
    #     @param sentence: sentence to check.
    #     @return: corrected sentence
    #     """
    #     changes = {change["word"]: change["s"][0] for change in self.__speller.spell(sentence)}
    #     for word, suggestion in changes.items():
    #         sentence = sentence.replace(word, suggestion)
    #     return sentence

    @staticmethod
    def _fix_typos(word: str, words: list) -> str:
        """
        Checks and corrects word typos.
        @param word: word to check.
        @param words: the dictionary against which the check will be carried out.
        @return: if word contains typos > 45% - return uncorrected word, else - corrected word.
        """
        array = np.array(words)
        result = list(zip(words, list(normalized_damerau_levenshtein_distance_seqs(word, array))))
        command, rate = min(result, key=lambda x: x[1])

        if rate > 0.45:
            return word
        return command

    @staticmethod
    def _remove_stop_words(tokenized_text: list) -> list:
        """
        Removing stop words from tokenized text.
        @param tokenized_text: list, that contains tokens.
        @return: list, without stop words.
        """
        stop_words = set(stopwords.words(["russian", "english"]))
        filtered_tokens = [word for word in tokenized_text if word not in stop_words]
        return filtered_tokens

    def _to_base_form(self, raw_text: list) -> list:
        """
        Brings the words back to its base form.
        @param raw_text: raw text, which needs to be processed.
        @return: list in which words are reduced to their base form.
        """
        base_form = []
        for word in raw_text:
            if len(word) < 2:
                continue
            word = self._lemmatizer.parse(word)[0]
            base_form.append(word.normal_form)
        return base_form

    def _word_processing(self, text: str) -> list:
        """
        Function, which unites everything related to word processing.
        @param text: raw text.
        @return: list with processed words.
        """
        text = self._remove_garbage(text)
        # text = self._correct_orthography(text)
        text = self._tokenize(text)
        text = self._to_base_form(text)
        result = self._remove_stop_words(text)
        return result

    # ------- Answering area -------
    def get_intent(self, text: str, threshold: float = None) -> str:
        """
        Getting intent and return with random answer for it.
        @param text: some question from user.
        @param threshold: model confidence threshold. that is, if the model's confidence in the answer
        is below the threshold, then it is probably the wrong answer.
        @return: intent for user's question.
        """
        if threshold is None:
            threshold = config["threshold"]

        vectors = self._text_to_vector(text)
        prediction = self._make_prediction(vectors)
        intent = self._get_intent(prediction, threshold)
        return intent

    def _text_to_vector(self, text: str) -> list:
        """
        Transforming text to vector.
        @param text: some question from user.
        @return: vector converted from user question.
        @raise ChatModelException: if an exception occurs during text vectorization.
        """
        try:
            prepared_data = self._word_processing(text)
            prepared_data_fixed_typos = []
            for word in prepared_data:
                word = self._fix_typos(word, self._dictionary)
                prepared_data_fixed_typos.append(word)
            bag = [0] * len(self._dictionary)
            for word in prepared_data_fixed_typos:
                for i, value in enumerate(self._dictionary):
                    if word == value:
                        bag[i] = 1
            return bag
        except Exception as exception:
            raise ChatModelException(f"Text vectorizing exception: {exception}.") from exception

    def _make_prediction(self, vectorized_text: list) -> list:
        """
        Making prediction on vectorized text.
        @param vectorized_text: vectorized question from user.
        @return: prediction on the question.
        @raise ChatModelException: if the perceptron exception occurs.
        """
        try:
            return self._perceptron.predict(np.array([vectorized_text]))[0]
        except Exception as exception:
            raise ChatModelException(f"Perceptron exception: {exception}.") from exception

    def _get_intent(self, prediction: list, threshold: float) -> Union[str, None]:
        """
        Getting intent for predicted value.
        @param prediction: list with predicted intent and probability.
        @return: the resulting intention.
        @raise ChatModelException: if the exclusion of the intention decoder occurs.
        """
        try:
            results = [[i, value] for i, value in enumerate(prediction) if value > threshold]
            results.sort(key=lambda x: x[1], reverse=True)
            if len(results) == 0:
                return None
            results_list = []
            for result in results:
                results_list.append({"intent": self._intents[result[0]], "probability": str(result[1])})
            return results_list[0].get("intent")
        except Exception as exception:
            raise ChatModelException(f"Intent decoder exception: {exception}") from exception

    # ------- Model creating area -------
    @staticmethod
    def make_multi_layer_perceptron(matrix_x, vector_y):
        """
        Creating keras sequential model for predictions.
        @param matrix_x: matrix of all possible keywords.
        @param vector_y: a vector of all kinds of jumbled intentions.
        @return: the adjusted model for training and the trained model.
        """
        model = Sequential()
        model.add(Dense(128, input_shape=(len(matrix_x[0]),), activation="relu"))
        model.add(Dropout(0.4))
        model.add(Dense(64, activation="relu"))
        model.add(Dropout(0.4))
        model.add(Dense(len(vector_y[0]), activation="softmax"))

        sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
        model.compile(loss="categorical_crossentropy", optimizer=sgd, metrics=["accuracy"])

        hist = model.fit(np.array(matrix_x), np.array(vector_y), epochs=60, batch_size=5)

        return model, hist
