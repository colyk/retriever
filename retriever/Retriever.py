from retriever.google_search import GoogleSearch


class Retriever:
    def __init__(self, query: str, lang: str = None):
        self.query = query.strip()
        if lang is not None:
            self.lang = lang.lower().strip()
        self.lang = None

    def g_search(self, **kwargs):
        return GoogleSearch(query=self.query, lang=self.lang, **kwargs)


if __name__ == "__main__":
    r = Retriever('дитинство')
    searcher = r.g_search(results_count=20)
    for link in searcher.links:
        print(link)
        break
