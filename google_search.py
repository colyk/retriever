from multiprocessing.pool import ThreadPool
from pprint import pprint
from typing import Iterator

import requests
import requests.exceptions as req_ex
from bs4 import BeautifulSoup

from text import Text
from wiki_search import WikiSearch

DEFAULT_LANG = 'uk'


class GoogleSearch:

    def __init__(self, query, lang: str = None, results_count: int = 10, wiki_only: bool = False, filetype: str = None):
        self.data = []

        self.query = query
        self.lang = lang or DEFAULT_LANG
        self.filetype = filetype or 'all'
        self.__base_url = 'https://www.google.com/search'
        self.__req_params = {
            'q': query,
            'as_filetype': self.filetype,
            'lr': 'lang_' + self.lang
        }

        assert 10 <= results_count <= 50
        assert results_count % 10 == 0
        self.results_count = results_count

        self.__get_data()

    def __get_data(self):
        offsets = range(0, self.results_count, 10)
        pool = ThreadPool(self.results_count // 10)
        pool.map(self.__fetch, offsets)
        pool.close()
        pool.join()

    def __fetch(self, offset: int):
        p = self.__req_params.copy()
        p.update({'start': offset})
        try:
            res = requests.get(self.__base_url, params=p)
        except req_ex.Timeout:
            raise
        assert res.status_code == requests.codes.ok
        self.__parse(res.text)

    def __parse(self, html):
        soup = BeautifulSoup(html, 'lxml')
        blocks = soup.find_all(class_='g')
        for block in blocks:
            title = block.find('h3').text.strip()
            desc = block.find(class_='st').text.strip()
            link = block.find('a').get('href')[7:]
            self.data.append(
                {
                    'title': title,
                    'desc': desc,
                    'link': self.__clean_url(link)
                }
            )

    def __clean_url(self, url):
        if self.filetype != 'all':
            return url.split('&')[0]
        return url

    @staticmethod
    def download_file(url: str, filename: str):
        r = requests.get(url, stream=True)
        downloaded_file = open(filename, 'wb')
        for chunk in r.iter_content(chunk_size=256):
            if chunk:
                downloaded_file.write(chunk)

    @staticmethod
    def is_exist(url: str)->bool:
        return requests.head(url, allow_redirects=True).ok

    @property
    def links(self)->Iterator:
        for block in self.data:
            yield block['link']

    @property
    def ft(self):
        return self.filetype

    @ft.setter
    def ft(self, ft):
        self.filetype = ft
        self.__req_params.update({'as_filetype': self.filetype})
        self.__get_data()


if __name__ == '__main__':
    gs = GoogleSearch(query='дитинство', results_count=50, filetype='pdf')
    for link in gs.links:
        print(link)
        break

    print('Got results: ', len(list(gs.links)))
    pprint(gs.data[0])

    gs.ft = 'all'
    pdf_link = gs.data[0].get('link')
    print(pdf_link)
    is_available = GoogleSearch.is_exist(pdf_link)
    print(is_available)

    if is_available:
        GoogleSearch.download_file(pdf_link, 'file.pdf')
