from abc import ABC, abstractmethod
from retriever import config


class Searcher(ABC):

    def __init__(self, query, lang):
        self.query = query
        self.lang = lang or config.DEFAULT_LANG

    @abstractmethod
    def start(self):
        pass
