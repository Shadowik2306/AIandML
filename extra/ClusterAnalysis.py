import pprint
import random

from pandas import DataFrame
from typing import Optional
import matplotlib.pyplot as plt

class ClusterAnalysis:
    cluster_count: int
    options: list[str]
    cluster_center_cords: list[(float, float)]
    distances: dict[tuple[float, float], list[float]] = {}
    membership_table: dict[tuple[float, float], list[float]] = {}

    def __init__(self, df: DataFrame, options: list[str], cluster_count: Optional[int] = None):
        if len(options) != 2:
            return

        self.options = options[:]
        # self.cluster_count = cluster_count if cluster_count else random.randint(2, 4)
        self.cluster_count = 3
        self.cluster_center_cords = [(0, 0)] * self.cluster_count
        self._first_membership_table(df)
        self.calculate()

    def calculate(self):
        while True:
            self._calculate_centers()
            self._calculate_distances()
            k = self._recalculate_membership()
            if k <= 0.001:
                break
        pprint.pprint(self.membership_table)

    def visualize(self):
        plt.scatter(self.cluster_center_cords[0][0], self.cluster_center_cords[0][1], c="#FF0000")
        plt.scatter(self.cluster_center_cords[1][0], self.cluster_center_cords[1][1], c="#00FF00")
        plt.scatter(self.cluster_center_cords[2][0], self.cluster_center_cords[2][1], c="#0000FF")
        for i in self.membership_table.keys():
            plt.scatter(i[0], i[1], c=(self.membership_table[i][0],self.membership_table[i][1],self.membership_table[i][2] ))
        plt.savefig("/home/shadowik/PycharmProjects/AIandML/static/cluster.png")
        plt.show()

    def check(self, last_membership):
        if max([sum([abs(self.membership_table[key][i] - last_membership[key][i]) for i in range(self.cluster_count)]) for key in self.membership_table.keys()]) < 0.01:
            return True
        return False

    def _calculate_centers(self):
        for cluster_id in range(self.cluster_count):
            x = sum([key[0] * value[cluster_id] ** 2 for key, value in self.membership_table.items()]) / \
                sum([value[cluster_id] ** 2 for _, value in self.membership_table.items()])
            y = sum([key[1] * value[cluster_id] ** 2 for key, value in self.membership_table.items()]) / \
                sum([value[cluster_id] ** 2 for _, value in self.membership_table.items()])
            self.cluster_center_cords[cluster_id] = (x, y)

    def _calculate_distances(self):
        for cords_point in self.membership_table.keys():
            for i, cords_centroid in enumerate(self.cluster_center_cords):
                self.distances[cords_point][i] = ((cords_point[0] - cords_centroid[0]) ** 2 + (cords_point[1] - cords_centroid[1]) ** 2) ** (1/2)

    def _recalculate_membership(self):
        change_value = []
        for cords in self.distances.keys():
            buff_list = []
            for cluster_id in range(self.cluster_count):
                buff = self.membership_table[cords][cluster_id]
                self.membership_table[cords][cluster_id] = \
                    sum([(self.distances[cords][cluster_id] ** 2) / (self.distances[cords][i] ** 2) for i in range(self.cluster_count)]) ** (-1 / (2 - 1))
                buff_list.append(abs(self.membership_table[cords][cluster_id] - buff))
            change_value.append(sum(buff_list))
        return max(change_value)


    def _first_membership_table(self, df: DataFrame):
        for _, (x, y) in df[self.options].dropna(thresh=2).iterrows():
            self.membership_table[(x, y)] = [random.random() for _ in range(self.cluster_count)]
            for i in range(self.cluster_count):
                self.membership_table[(x, y)][i] /= sum(self.membership_table[(x, y)])
            self.distances[(x, y)] = [0] * self.cluster_count

            # self.membership_table = {
            #     (1, 3): [0.8, 0.2],
            #     (2, 5): [0.7, 0.3],
            #     (4, 8): [0.2, 0.8],
            #     (7, 9): [0.1, 0.9],
            # }
            # self.distances = {
            #     (1, 3): [0.8, 0.2],
            #     (2, 5): [0.7, 0.3],
            #     (4, 8): [0.2, 0.8],
            #     (7, 9): [0.1, 0.9],
            # }
        # pprint.pprint(self.membership_table)
