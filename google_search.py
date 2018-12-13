import requests
from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool
import requests.exceptions as req_ex

DEFAULT_LANG = 'uk'


class GoogleSearch:
    # TODO search only in wiki
    # [+] TODO search only files

    def __init__(self, query, lang=None, results_count=10, wiki_only=False, filetype=None):
        self.data = []
        self.query = query
        self.lang = lang or DEFAULT_LANG
        self.filetype = filetype or 'all'
        self.base_url = self.__format_url()
        assert 10 <= results_count <= 50
        assert results_count % 10 == 0
        self.results_count = results_count

    def start(self):
        self.__get_data()

    def __format_url(self):
        g_template = 'https://www.google.com/search?lr=lang_{}&q={}&as_filetype={}'
        return g_template.format(self.lang, self.query, self.filetype)

    def __get_data(self):
        offsets = range(0, self.results_count, 10)
        pool = ThreadPool(self.results_count // 10)
        data = pool.map(self.__fetch, offsets)
        pool.close()
        pool.join()

    def __fetch(self, offset):
        g_offset_template = '{}&start={}'
        url = g_offset_template.format(self.base_url, offset)
        try:
            res = requests.get(url)
        except req_ex.Timeout:
            # bad connection
            raise
        assert res.status_code == 200
        html = res.text
        self.__parse(html)

    def __parse(self, html):
        soup = BeautifulSoup(html, 'lxml')
        blocks = soup.find_all(class_='g')
        for block in blocks:
            title = block.find('h3').text.strip()
            desc = block.find(class_='st').text.strip()
            link = block.find('a').get('href')[7:]
            # TODO make pure
            self.data.append(
                {
                    'title': title,
                    'desc': desc,
                    'link': link
                }
            )

    @staticmethod
    def __validate_url(url):
        # format pdf links - trim
        pass

    @staticmethod
    def download_file(url, filename):
        r = requests.get(url, stream=True)
        downloaded_file = open(filename, 'wb')
        for chunk in r.iter_content(chunk_size=256):
            if chunk:
                downloaded_file.write(chunk)

    @property
    def links(self):
        for block in self.data:
            yield block['link']

    @property
    def ft(self):
        return self.filetype

    @ft.setter
    def ft(self, ft):
        self.filetype = ft
        self.base_url = self.__format_url()


if __name__ == '__main__':
    gs = GoogleSearch(query='дитинство', results_count=50, filetype='pdf')
    gs.start()
    for link in gs.links:
        print(link)
        break

    print('Got results: ', len(list(gs.links)))
    print(gs.data[0])

    gs.ft = 'all'
    gs.start()
    print(gs.data[1])
