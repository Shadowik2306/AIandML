from extra.BloomFilter import BloomFilter


class SiteFilter:
    def __init__(self):
        self.filter: BloomFilter = BloomFilter(100000)
        self.keyword_urls: dict[str, list[str]] = {}

    def add_url(self, url: str, keywords: list[str]):
        for keyword in keywords:
            url_low = keyword.lower()
            self.filter.add_to_filter(url_low)
            if url_low not in self.keyword_urls:
                self.keyword_urls[url_low] = []
            self.keyword_urls[url_low].append(url)

    def get_url(self, keyword: str) -> list[str]:
        lowercase_string = keyword.lower()
        if self.filter.check_is_not_in_filter(lowercase_string):
            return []
        else:
            return self.keyword_urls[lowercase_string]

    def contains(self, keyword: str) -> bool:
        return not self.filter.check_is_not_in_filter(keyword.lower())
