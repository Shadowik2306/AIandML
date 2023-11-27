import numbers

from pandas import DataFrame
from typing import Optional

import json

from pandas.core.dtypes.common import is_numeric_dtype


class DecisionTree:
    target: str
    def __init__(self, df: DataFrame, target: str, options: list):
        if not options:
            return
        if target not in df.columns:
            return
        self.target = target
        for option in options:
            if option not in df.columns:
                return

        self.root_node = _Node(df, target, options)

    def get_json(self):
        return json.dumps(self.root_node.get_dct())

    def check_data(self, df: DataFrame):
        res = []
        for row in df.iterrows():
            node = self.root_node
            while not node.final:
                node = node.resend_to_node(row)
            res.append((node.value - row[1][self.target]) ** 2)
        return sum(res) / len(res)


class _Node:
    parent: Optional["_Node"] = None
    left: Optional["_Node"] = None
    right: Optional["_Node"] = None
    samples: int
    value: float
    mse: float
    decision: (str, object) = ()
    final: bool = False

    def __init__(self, df: DataFrame, target: str, options: list, parent: Optional["_Node"] = None):
        self.parent = parent
        self.samples = len(df)
        self.value = df[target].mean()
        if len(df[target].unique()) != 1:
            self.mse = ((df[target] - self.value) ** 2).mean()
        else:
            self.mse = 0
            self.value = df[target].values[0]
        if self.mse == 0:
            self.final = True
            return
        self.find_best_solution(df, target, options)

    def get_dct(self):
        dct = {
            "decision": "",
            "mse": self.mse,
            "samples": self.samples,
            "value": self.value,
        }
        if self.decision:
            if isinstance(self.decision[1], numbers.Number):
                dct["decision"] = f"{self.decision[0]} <= {self.decision[1]}" if self.decision else ""
            else:
                dct["decision"] = f"{self.decision[0]} == {self.decision[1]}" if self.decision else ""
        else:
            dct.pop("decision")

        if self.left:
            dct["yes"] = self.left.get_dct() if self.left else None
        if self.right:
            dct["no"] = self.right.get_dct() if self.right else None
        return dct

    def find_best_solution(self, df: DataFrame, target: str, options: list):
        ig = -100
        for option in options:
            for opt_var in df[option].unique():
                if is_numeric_dtype(df[option]):
                    df_left = df[df[option] <= opt_var]
                    df_right = df[~(df[option] <= opt_var)]
                else:
                    df_left = df[df[option] == opt_var]
                    df_right = df[~(df[option] == opt_var)]
                mse_left = ((df_left[target] - df_left[target].mean()) ** 2).mean()
                mse_right = ((df_right[target] - df_right[target].mean()) ** 2).mean()
                cur_ig = self.mse - ((len(df_left) / len(df)) * mse_left + (len(df_right) / len(df)) * mse_right)
                if cur_ig >= ig:
                    ig = cur_ig
                    self.decision = (option, opt_var)

        if not self.decision:
            self.final = True
            return
        if is_numeric_dtype(df[self.decision[0]]):
            self.left = _Node(df[df[self.decision[0]] <= self.decision[1]], target, options, self)
            self.right = _Node(df[~(df[self.decision[0]] <= self.decision[1])], target, options, self)
        else:
            self.left = _Node(df[df[self.decision[0]] == self.decision[1]], target, options, self)
            self.right = _Node(df[~(df[self.decision[0]] == self.decision[1])], target, options, self)

    def resend_to_node(self, row: tuple):
        if isinstance(self.decision[1], numbers.Number):
            return self.left if row[1][self.decision[0]] <= self.decision[1] else self.right
        else:
            return self.left if row[1][self.decision[0]] == self.decision[1] else self.right
