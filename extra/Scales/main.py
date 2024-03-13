import matplotlib.pyplot as plt


class FuzzySet:
    def __init__(self,
                 vals=None,
                 lst=None):
        if vals is None:
            vals = {}

        self._registered = set()
        self.data = list()
        self._trap_rand = {}
        if len(lst) == 4:
            self._trap_rand = {
                "a": lst[0],
                "b": lst[1],
                "c": lst[2],
                "d": lst[3]
            }
        elif len(lst) == 3:
            self._trap_rand = {
                "a": lst[0],
                "b": lst[1],
                "c": lst[1],
                "d": lst[2]
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


if __name__ == "__main__":
    func_high = [15000, 30000, 40000, 50000]
    func_middle = [10000, 15000, 20000]
    func_less = [0, 10000, 15000]

    funcs = [("Большие убытки", func_high),
             ("Cредние убытки", func_middle),
             ("Малые убытки", func_less)]

    data = [9868, 27666, 24235, 25991, 20903, 1675, 29183, 1217, 4921, 27045, 4828, 7472, 667,
            12571, 11551, 13917, 23427, 14727, 16102, 9516]


    huge = FuzzySet(data, func_high)
    middle = FuzzySet(data, func_middle)
    less = FuzzySet(data, func_less)

    ax = plt.subplot()
    for fun in funcs:
        if len(fun[1]) == 3:
            ax.plot(fun[1], [0, 1, 0], label=fun[0])
        else:
            ax.plot(fun[1], [0, 1, 1, 0], label=fun[0])
    ax.legend()

    for i in range(len(data)):
        max_val = max(huge[i]["dep"], middle[i]["dep"], less[i]["dep"])
        ax.plot(data[i], max_val, "go")
        plt.text(data[i], max_val, data[i])



    plt.show()