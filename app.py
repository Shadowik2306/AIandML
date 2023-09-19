from io import StringIO
from flask import Flask, render_template, request
import pandas as pd

original_table = None
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


def upload_table(data=None, min_col=-1, max_col=-1, min_row=-1, max_row=-1,):
    global table, original_table
    if data:
        csv_string_io = StringIO(data)
        df = pd.read_csv(csv_string_io, sep=",")
    else:
        df = original_table

    min_row = min_row - 1 if min_row else 0
    max_row = max_row if max_row else len(df.index)

    min_col = min_col - 1 if min_col else 0
    max_col = max_col if max_col else len(df.columns)

    original_table = df

    table = ([df.iloc[min_row:max_row, min_col:max_col].columns.values.tolist()] +
             df.iloc[min_row:max_row, min_col:max_col].values.tolist())


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def hello_world():  # put application's code here
    params = {
        "data": table,
        "start_index": 0
    }

    sint = ignore_exception(ValueError)(int)
    if request.method == "POST":
        try:
            file = request.files.get("formFile")
            file_content = file.read().decode("UTF-8")
        except KeyError:
            file_content = None

        upload_table(file_content, sint(request.form["minCol"]), sint(request.form["maxCol"]),
                     sint(request.form["minRow"]), sint(request.form["maxRow"]))
        params["data"] = table
        params["start_index"] = sint(request.form["minRow"]) - 1 if sint(request.form["minRow"]) else 0

    return render_template("index.html", **params)


if __name__ == '__main__':
    app.run()
