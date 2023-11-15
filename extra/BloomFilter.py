import math

from bitarray import bitarray


class BloomFilter:
    size: int = 0
    expected_size: int = 10000

    bloom_filter: bitarray = None
    hash_function_count: int = 1

    def __init__(self, size: int, expected_size: int = 100000):
        self.size = size
        self.expected_size = expected_size

        self.bloom_filter = bitarray(size)
        self.bloom_filter.setall(0)

        self.hash_function_count = round((self.size / self.expected_size) * math.log(2))

    def add_to_filter(self, item):
        for i in range(self.hash_function_count):
            self.bloom_filter[self._hash(item, i)] = 1

    def check_is_not_in_filter(self, item):
        for i in range(self.hash_function_count):
            if self.bloom_filter[self._hash(item, i)] == 0:
                return True
        return False

    def _hash(self, item, key):
        return self._hash_djb2(str(key) + item)

    def _hash_djb2(self, s):
        hash = 5381
        for x in s:
            hash = ((hash << 5) + hash) + ord(x)
        return hash % self.size


