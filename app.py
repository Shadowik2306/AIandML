from io import StringIO

import pandas
from flask import Flask, render_template, request
import pandas as pd

original_table: pd.DataFrame = pd.DataFrame()
table = []

def ignore_exception(IgnoreException=Exception, DefaultVal=None):
    def dec(function):
        def _dec(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except IgnoreException:
                return DefaultVal

        return _dec

    return dec


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
        df = pd.read_csv(csv_string_io, sep=",")
    else:
        df = original_table

    min_row = min_row - 1 if min_row else 0
    max_row = max_row if max_row else len(df.index)

    min_col = min_col - 1 if min_col else 0
    max_col = max_col if max_col else len(df.columns)

    original_table = df

    table_iloc = df.iloc[min_row:max_row, min_col:max_col]
    return format_table(table_iloc)



def collect_min_max_mean(group_by_column: str, collect_by_column: str):

    grouped_table = original_table.groupby(group_by_column)[collect_by_column]
    columns = {
        f"{collect_by_column} min": "min",
        f"{collect_by_column} mean": "mean",
        f"{collect_by_column} max": "max"
    }
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


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def hello_world():  # put application's code here
    params = {
        "start_index": 0,
        "types": [],
        "null_el": [],
        "not_null_el": []
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

    return render_template("index.html", **params)


if __name__ == '__main__':
    app.run()
