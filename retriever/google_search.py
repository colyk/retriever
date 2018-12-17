from multiprocessing.pool import ThreadPool
from typing import Iterator

import requests
import requests.exceptions as req_ex
from bs4 import BeautifulSoup

from retriever import utils
from retriever.abc_searcher import Searcher


class GoogleSearch(Searcher):

    def __init__(self, query, lang: str = None, results_count: int = 10, file_format: str = ''):
        super().__init__(query=query, lang=lang)

        self.data = []
        self.BASE_URL = 'https://www.google.com/search'

        self.file_format = file_format
        self.__params = {
            'q': query,
            'lr': 'lang_' + self.lang,
            'as_filetype': self.file_format,
        }

        self.results_count = int(round(results_count, -1))
        assert 10 <= results_count <= 50

    def start(self):
        offsets = range(0, self.results_count, 10)
        pool = ThreadPool(self.results_count // 10)
        pool.map(self.__fetch, offsets)
        pool.close()
        pool.join()

    def __fetch(self, offset: int):
        req_params = self.__params.copy()
        req_params.update({'start': offset})
        try:
            res = requests.get(self.BASE_URL, params=req_params)
        except req_ex.Timeout:
            raise
        assert res.status_code == requests.codes.ok
        self.__parse(res.text)

    def __parse(self, html: str):
        soup = BeautifulSoup(html, 'lxml')
        blocks = soup.find_all(class_='g')
        for block in blocks:
            title = block.find('h3').text.strip()
            desc = block.find(class_='st').text.strip()
            url = block.find('a').get('href')[7:]
            self.data.append(
                {
                    'title': title,
                    'desc': desc,
                    'link': self.__clean_url(url)
                }
            )

    def __clean_url(self, url: str) -> str:
        if self.file_format != '':
            return url.split('&')[0]
        return url

    @property
    def links(self) -> Iterator[str]:
        for block in self.data:
            yield block['link']

    @property
    def ft(self):
        return self.file_format

    @ft.setter
    def ft(self, ft):
        self.file_format = ft
        if ft == '':
            del self.__params['as_filetype']
        else:
            self.__params.update({'as_filetype': self.file_format})
        self.clean()

    def __str__(self):
        return '{!r}'.format(self.info())

    def info(self):
        return {'query': self.query, 'results': len(self.data),
                'file_format': self.file_format or 'all',
                'is_fetched': bool(self.data)}

    def clean(self):
        self.data = []


if __name__ == '__main__':
    gs = GoogleSearch(query='дитинство', results_count=10)
    gs.start()
    print(gs)
    for link in gs.links:
        print(link)
        break

    print('Got results: ', len(list(gs.links)))

    gs.ft = 'pdf'
    gs.start()
    print(gs)
    pdf_link = gs.data[0].get('link')
    print(pdf_link)
    is_available = utils.is_exist(pdf_link)
    print(is_available)

    if is_available:
        utils.download_file(pdf_link)
