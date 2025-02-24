import cv2
from a2wsgi import ASGIMiddleware
from fastapi import FastAPI
from flask import Flask, render_template, request
from werkzeug.middleware.dispatcher import DispatcherMiddleware

############################################################
# setup flask app
#  flask --app src.main --debug run  to start from sh
############################################################
flask_app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static",
)


def init():
    print("starting")


@flask_app.route("/", methods=["GET"])
def iris_index():
    return render_template("base_index.html")


@flask_app.route("/prediction", methods=["POST", "GET"])
def result():
    print("inside /prediction")
    if request.method == "POST":
        print("inside /prediction : POST")
        if "file" not in request.files:
            return "No file part", 400
        file = request.files["file"]
        if file.filename == "":
            return "No selected file", 400
        if file:
            # Sauvegarder le fichier ou effectuer des prédictions
            file.save(f"{file.filename}")
            return "File received", 200
    if request.method == "GET":
        print("inside /predict : GET")
        return render_template("base_index.html")
    return


############################################################
# fastapi
############################################################
fast_api_app = FastAPI()


@fast_api_app.get("/")
def read_main():
    return {"message": "Hello World from fastapi"}


# keep this last before main()
flask_app.wsgi_app = DispatcherMiddleware(
    flask_app.wsgi_app,
    {
        "/flask": flask_app,
        "/fast": ASGIMiddleware(fast_api_app),
    },
)

if __name__ == "__main__":
    init()
    flask_app = Flask(__name__)
    # flask_app.debug = True
    flask_app.run(host="0.0.0.0", port=5000, debug=True)
