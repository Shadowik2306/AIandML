import pprint
import sys

class FuzzySet:
    def __init__(self,
                 lst=None,
                 vals=None):
        if vals is None:
            vals = {}

        self._registered = set()
        self.data = list()
        self._trap_rand = {
            "a": lst[0],
            "b": lst[1],
            "c": lst[2],
            "d": lst[3]
        }

        for val in vals:
            self.add(val)

    def add(self, val):
        if val in self._registered:
            return
        if (type(val) is float) or (type(val) is int):
            self.data.append(self._calculate_fuzzy_val(val))
        self._registered.add(val)

    def _calculate_fuzzy_val(self, x):
        res = {
            "val": x,
            "dep": 0
        }

        if (self._trap_rand["b"] < x) and (x < self._trap_rand["c"]):
            res["dep"] = 1
        elif (self._trap_rand["a"] <= x) and (x <= self._trap_rand["b"]):
            res["dep"] = (x - self._trap_rand["a"]) / (self._trap_rand["b"] - self._trap_rand["a"])
        elif (self._trap_rand["c"] <= x) and (x <= self._trap_rand["d"]):
            res["dep"] = (self._trap_rand["d"] - x) / (self._trap_rand["d"] - self._trap_rand["c"])

        return res

    def __getitem__(self, item):
        return self.data[item]

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return str(self.data)



class FuzzyLogicImplement:
    def __init__(self, a: FuzzySet, b: FuzzySet):
        relation = self._impl(a, b)
        pprint.pprint(relation)

    @staticmethod
    def _impl(v1, v2):
        res = []
        for i in range(len(v1)):
            res.append({
                "val": v1[i]["val"],
                "dep": max(1 - v1[i]["dep"], v2[i]["dep"])
            })
        return res


if __name__ == "__main__":

    try:
        # s = [5000, 10000, 15000, 25000, 30000, 35000, 40000]
        # a = FuzzySet(0, 6000, 30000, 70000, s)
        # b = FuzzySet(4000, 8000, 16000, 40000, s)
        print("Введите четкие значения: (через пробел)")
        s = list(map(float, input().split()))
        print("Введите параметры первой трапециевидной функции: (a b c d)")
        tr1 = list(map(float, input().split()))
        if len(tr1) != 4:
            raise ValueError
        print("Введите параметры второй трапециевидной функции: (a b c d)")
        tr2 = list(map(float, input().split()))
        if len(tr1) != 4:
            raise ValueError
    except ValueError:
        print("Ошибка при вводе данных")
        sys.exit(1)

    a = FuzzySet(tr1, s)
    pprint.pprint(a.data)
    print()

    b = FuzzySet(tr2, s)
    pprint.pprint(b.data)
    print()

    FuzzyLogicImplement(a, b)
    print()
    FuzzyLogicImplement(b, a)