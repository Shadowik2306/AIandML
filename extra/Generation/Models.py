import math
import random

import numpy as np
from random import randint, shuffle, choices
from itertools import product


class DataFieldEx:
    def __init__(self, fields_count=10, culture_count=5, range_effective=(1, 100), range_price=(1, 100)):
        self.fields_count = fields_count
        self.culture_count = culture_count
        self.cultures = np.array([randint(*range_price) for i in range(culture_count)])
        self.fields = np.array([[randint(*range_effective) for j in range(culture_count)]
                                for i in range(fields_count)])

    @classmethod
    def load_from_arr(cls, arr: np.ndarray):
        buff = cls(culture_count=0)
        buff.culture_cost = arr
        return buff


class GenericMethod:
    def __init__(self, data: DataFieldEx, child_count: int = 5, gen_limit: int = np.inf, best_limit: float = 0.7):
        generation = np.array([[randint(-1, data.culture_count - 1) for _ in range(data.fields_count)]
                               for _ in range(child_count)])

        chance = np.array([0] * child_count, dtype="double")

        limit = data.fields.max(axis=0).sum() * best_limit
        max_effective = 0
        max_result = np.array([-1] * child_count)
        gen_age = 0
        while gen_age < gen_limit:
            # print(gen_age, generation)
            sum_effective = 0

            for i in range(child_count):
                chance[i] = max(1, self._count_effective(data, generation[i]))
                sum_effective += chance[i]
                if chance[i] > max_effective:
                    max_effective = chance[i]
                    max_result = generation[i]
            chance /= sum_effective

            if max_effective >= limit:
                break

            new_children = []
            for cross in range(child_count):
                try:
                    a, b = self._choices_no_replacement(generation, chance)
                    arr = np.concatenate((a[:data.fields_count / 2], b[data.fields_count/2:]))
                except:
                    arr = self._choices_no_replacement(generation, chance, k=1)[0]

                arr[randint(0, data.fields_count - 1)] = randint(-1, data.culture_count - 1)
                new_children.append(arr)

            generation = np.array(new_children)
            gen_age += 1

        print(max_effective, max_result)

    def _count_effective(self, arr, variant):
        effective = 0
        for i in range(len(variant)):
            if variant[i] < 0:
                continue
            effective += arr.fields[i][variant[i]] - arr.cultures[variant[i]]
        return effective

    @staticmethod
    def _choices_no_replacement(population, weights, k=2):
        population_copy = list(population)
        weights_copy = list(weights)
        result = []
        for n in range(k):
            pos = random.choices(
                range(len(population_copy)),
                weights_copy,
                k=1
            )[0]
            result.append(population_copy[pos])
            del population_copy[pos], weights_copy[pos]
        return result


class BruteForceMethod:
    def __init__(self, arr: DataFieldEx):
        self.max_effective = 0
        self.res = np.array([])

        variant = np.array([-1] * arr.fields_count)

        while self._val_increment(variant, arr.culture_count, arr.fields_count):
            effective = 0
            for i in range(arr.fields_count):
                if variant[i] < 0:
                    continue
                effective += arr.fields[i][variant[i]] - arr.cultures[variant[i]]
            if effective > self.max_effective:
                self.max_effective = effective
                self.res = variant.copy()

        print(self.max_effective, self.res)

    @staticmethod
    def _val_increment(lst: np.ndarray, max_val: int, max_len: int) -> bool:
        for i in range(max_len):
            lst[i] += 1
            if lst[i] != max_val:
                break
            lst[i] = 0
        else:
            return False
        return True


if __name__ == "__main__":
    a = DataFieldEx()
    # BruteForceMethod(a)
    GenericMethod(a, gen_limit=10000)
