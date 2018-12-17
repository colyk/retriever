import requests

from retriever.abc_searcher import Searcher


class WikiSearch(Searcher):
    def __init__(self, query, lang=None):
        super().__init__(query=query, lang=lang)
        self.BASE_URL = 'http://{}.wikipedia.org/w/api.php'.format(self.lang)

    def start(self):
        pass

    def __wiki_request(self, params):
        r = requests.get(self.BASE_URL, params=params)
        print(r.status_code)
        print(r.url)

        return r

    def get(self):
        params = {
            'prop': 'extracts',
            'plaintext': '',
            'titles': self.query
        }

        res = self.__wiki_request(params)
        print(res)


if __name__ == '__main__':
    ws = WikiSearch('Масове вимирання')
    ws.get()
