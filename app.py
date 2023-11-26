import os
from io import StringIO

import numpy
import pandas
from flask import Flask, render_template, request, redirect
import pandas as pd
from pandas.api.types import is_numeric_dtype
import matplotlib.pyplot as plt

from extra.SiteFilter import SiteFilter

original_table: pd.DataFrame = pd.DataFrame()
extra_data_table: pd.DataFrame
table = []
site_filter = SiteFilter()
b0, b1, r = 0, 0, 0


site_filter.add_url("https://www.kaggle.com/datasets/psycon/daily-coffee-price/data", [
    "Date", "Open", "High", "Low", "Close", "Volume", "Currency"
])
site_filter.add_url("https://www.kaggle.com/datasets/mohit2512/jio-mart-product-items", [
    "category", "sub_category", "href", "items", "price"
])
site_filter.add_url("https://www.kaggle.com/datasets/sadeghjalalian/ufo-sightings-in-usa/data", [
    "summary", "city", "state", "shape", "duration", "stats", "report_link", "text", "posted"
])
site_filter.add_url("https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database", [
    "Pregnancies", "Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI", "DiabetesPedigreeFunction", "Age", "Outcome"
])
site_filter.add_url("https://www.kaggle.com/datasets/harlfoxem/housesalesprediction", [
    "date", "price", "bedrooms", "bathrooms", "sqft_living", "sqft_lot", "floors", "waterfront", "view"
])


def ignore_exception(IgnoreException=Exception, DefaultVal=None):
    def dec(function):
        def _dec(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except IgnoreException:
                return DefaultVal

        return _dec

    return dec

# Детерминации и график рассеивания
def linear_regression():
    global b0, b1, r
    if original_table.empty:
        return
    n = len(original_table.dropna(subset=['unemploymentrate', 'oil prices']))
    x = original_table.dropna(subset=['unemploymentrate', 'oil prices'])["unemploymentrate"]  # x
    y = original_table.dropna(subset=['unemploymentrate', 'oil prices'])["oil prices"]  # y

    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(x * y)
    sum_xx = sum(x * x)

    b1 = (sum_xy - (sum_y * sum_x) / n) / (sum_xx - sum_x ** 2 / n)
    b0 = (sum_y - b1 * sum_x) / n
    r = (sum((x * b1 + b0) * (x * b1 + b0)) - n * y.mean() * y.mean()) / (sum(y * y) - n * y.mean() * y.mean())

    print(b1, b0)

    plt.scatter(x, y)
    plt.plot(x, [i * b0 + b1 for i in x], color="r")
    plt.savefig("/home/shadowik/PycharmProjects/AIandML/static/linearRegression.png")
    plt.show()

def format_table(df):
    global table
    table = ([df.columns.values.tolist()] + df.values.tolist())
    return {
        "types": df.dtypes.values.tolist(),
        "null_el": df.isna().sum().values.tolist(),
        "not_null_el": df.notna().sum().values.tolist()
    }

def upload_table(data=None, min_col=-1, max_col=-1, min_row=-1, max_row=-1, new_data=True):
    global table, original_table
    if data and new_data:
        csv_string_io = StringIO(data)
        original_table = pd.read_csv(csv_string_io, sep=",")

        linear_regression()
        add_similar_data()

    min_row = min_row - 1 if min_row else 0
    max_row = max_row if max_row else len(original_table.index)

    min_col = min_col - 1 if min_col else 0
    max_col = max_col if max_col else len(original_table.columns)

    table_iloc = original_table.iloc[min_row:max_row, min_col:max_col]
    return format_table(table_iloc)


def collect_min_max_mean(group_by_column: str, collect_by_column: str):
    grouped_table = extra_data_table.groupby(group_by_column)[collect_by_column]

    columns = {
        f"{collect_by_column} min extra": "min",
        f"{collect_by_column} mean extra": "mean",
        f"{collect_by_column} max extra": "max"
    }

    try:
        ax = grouped_table.agg(**columns).plot(figsize=(10, 5), rot=10)
        # plt.savefig("static/myPlot2.png")
        # plt.show()


    except Exception as e:
        print(e)

    grouped_table = original_table.groupby(group_by_column)[collect_by_column]
    columns = {
        f"{collect_by_column} min": "min",
        f"{collect_by_column} mean": "mean",
        f"{collect_by_column} max": "max"
    }

    try:
        grouped_table.agg(**columns).plot( figsize=(10, 5), rot=10, ax=ax)
        plt.savefig("/home/shadowik/PycharmProjects/AIandML/static/myPlot.png")
        plt.show()
    except Exception as e:
        print(e)


    return grouped_table.agg(**columns).sort_values(f"{collect_by_column} max", ascending=False)


def collect_min_max_mean_2_col(group_by_column: str, collect_by_column):
    grouped_table = original_table.groupby(group_by_column)[[collect_by_column[0], collect_by_column[1]]]
    columns = {
        f"{collect_by_column[0]} min": (collect_by_column[0], 'min'),
        f"{collect_by_column[1]} min": (collect_by_column[1], 'min'),
        f"{collect_by_column[0]} mean": (collect_by_column[0], 'mean'),
        f"{collect_by_column[1]} mean": (collect_by_column[1], 'mean'),
        f"{collect_by_column[0]} max": (collect_by_column[0], 'max'),
        f"{collect_by_column[1]} max": (collect_by_column[1], 'max')

    }
    return grouped_table.agg(**columns).sort_values(f"{collect_by_column[0]} max", ascending=False)


def translate_to_min_max(group_by, collect_by):
    global table
    if original_table.empty:
        return []

    group_by = "country" if group_by == 1 else "year"
    find_dict = {
        1: "oil prices",
        2: "unemploymentrate",
        3: ["oil prices", "unemploymentrate"]
    }
    collect_by = find_dict[collect_by]

    if collect_by.__class__ is not list:
        res = collect_min_max_mean(group_by, collect_by).reset_index()
    else:
        res = collect_min_max_mean_2_col(group_by, collect_by).reset_index()
    return format_table(res)


def add_similar_data():
    global original_table, extra_data_table
    extra_data_table = original_table.copy()
    count_of_new_lines = int(len(extra_data_table) * 0.10)
    if count_of_new_lines == 0: return
    template_of_row: dict = extra_data_table.loc[1].to_dict()

    for key in template_of_row.keys():
        if is_numeric_dtype(extra_data_table[key]):
            template_of_row[key] = round(extra_data_table[key].mean(), 2)
        else:
            template_of_row[key] = extra_data_table[key].mode()[0]

    extra_data_table = pd.concat([extra_data_table, pd.DataFrame([template_of_row] * count_of_new_lines)], ignore_index=True)


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def hello_world():  # put application's code here
    params = {
        "start_index": 0,
        "types": [],
        "null_el": [],
        "not_null_el": [],
    }

    data = {
            "types": [],
            "null_el": [],
            "not_null_el": []

    }

    sint = ignore_exception(ValueError)(int)
    if request.method == "POST":
        if request.form["btn"] == "Group_By":
            data = translate_to_min_max(int(request.form["group_by_col"]), int(request.form["data_by_col"]))
        else:
            try:
                file = request.files.get("formFile")
                file_content = file.read().decode("UTF-8")
            except KeyError:
                file_content = None
            data = upload_table(file_content, sint(request.form["minCol"]), sint(request.form["maxCol"]),
                         sint(request.form["minRow"]), sint(request.form["maxRow"]))
            params["start_index"] = sint(request.form["minRow"]) - 1 if sint(request.form["minRow"]) else 0

    params["types"] = data["types"]
    params["null_el"] = data["null_el"]
    params["not_null_el"] = data["not_null_el"]
    params["data"] = table
    params["a"] = b0
    params["b"] = b1
    params["r"] = r
    return render_template("index.html", **params)


@app.route('/search', methods=['GET', 'POST'])
def bloom_filter_search():  # put application's code here
    params = {
        "state": 0,
        "key": "",
        "url": []
    }
    if request.method == "POST":
        val = request.form["url_input"]
        if not val:
            return render_template("bloom.html", **params)
        if (int(request.form["state"]) <= 0) or (val != request.form["last_word"]):
            if site_filter.contains(val):
                params["state"] = 1
            else:
                params["state"] = -1
            params["key"] = val
        else:
            params["urls"] = site_filter.get_url(val)
            params["state"] = 0

    return render_template("bloom.html", **params)


if __name__ == '__main__':
    try:
        print(__file__)
        os.remove("static/myPlot.png")
        os.remove("static/linearRegression.png")

    except:
        pass

    app.run()
