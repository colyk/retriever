from abc import ABC, abstractmethod

import config

class Searcher(ABC):

    def __init__(self, query, lang):
        self.query = query
        self.lang = lang or config.DEFAULT_LANG