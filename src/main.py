import random
from typing import Annotated

import cv2
from a2wsgi import ASGIMiddleware
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from flask import Flask, render_template, request
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from lib.ml import load_models, process_image

############################################################
# setup flask app
#  flask --app src.main --debug run  to start from sh
############################################################
flask_app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static",
)


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


@flask_app.route("/test_prediction", methods=["POST", "GET"])
def test_pred():
    print("inside /test_prediction")
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

            return render_template(
                "detected_product.html",
                product_id="2",
                product_name="produit de test",
                product_weight="0.5",
                product_price="10€",
            )

    if request.method == "GET":
        print("inside /predict : GET")
        return render_template("client_t.html")
    return


############################################################
# fastapi
############################################################
fast_api_app = FastAPI()


@fast_api_app.get("/")
def read_main():
    return {"message": "Hello World from fastapi"}


@fast_api_app.post("/pred")
def get_pred(
    file: UploadFile,
):  # optimize les acces, le fichier est gardé en RAM ( selon sa taille)

    print("inside /pred with fastapi , received filname : ", file.filename)
    with open(file.filename, "wb") as f:
        f.write(file.file.read())

    lst_product = process_image(file.filename)

    # {{product_id}}  {{product_name}}    {{product_weight}}   {{product_price}}
    return lst_product


@fast_api_app.get("/img")
def get_image(image_num: int):
    print("inside /img with fastapi , asking for image_num : ", image_num)

    # nb = random.randint(1, 10)
    image_path = (
        f"/home/usr/code/pdufourny/balance_intelligente/static/images/{image_num}.png"
    )

    print(image_path)
    return FileResponse(image_path)


############################################################
# keep this last before main()
# ref https://fastapi.tiangolo.com/advanced/wsgi/
############################################################
flask_app.wsgi_app = DispatcherMiddleware(
    flask_app.wsgi_app,
    {
        "/flask": flask_app,
        "/fast": ASGIMiddleware(fast_api_app),
    },
)
# par defaut, appels vers flask
# pour les appels fastapi, ajouter /fast/ dans l'url
# curl -X POST http://127.0.0.1:6000/fast/pred -F "file=@/home/usr/code/pdufourny/balance_intelligente/data/kiwi_test.jpg"


if __name__ == "__main__":
    init()
    # flask_app = Flask(__name__)
    # flask_app.debug = True
    flask_app.run(host="0.0.0.0", port=6000, debug=True)
