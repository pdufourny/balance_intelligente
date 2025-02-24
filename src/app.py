from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET"])
def iris_index():
    return render_template("index.html")


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=8000, debug=True)
