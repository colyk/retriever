import requests

import config


class WikiSearch:
    def __init__(self, title, lang=None):
        self.title = title
        self.lang = lang or import config.DEFAULT_LANG
        self.BASE_URL = 'http://{}.wikipedia.org/w/api.php'.format(self.lang)

    def __wiki_request(self, params):
        r = requests.get(self.BASE_URL, params=params)
        print(r.status_code)
        print(r.url)

        return r

    def get(self):
        params = {
            'prop': 'extracts',
            'explaintext': '',
            'titles': self.title
        }

        res = self.__wiki_request(params)
        print(res)


if __name__ == '__main__':
    ws = WikiSearch('Масове вимирання')
    ws.get()
