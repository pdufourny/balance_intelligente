from typing import Annotated

# from a2wsgi import ASGIMiddleware
# from fastapi import FastAPI, File, UploadFile
# from fastapi.responses import FileResponse
from flask import Flask, render_template, request, send_file, url_for

from lib.ml import load_models, process_image

# from werkzeug.middleware.dispatcher import DispatcherMiddleware


# from fastapi.middleware.wsgi import WSGIMiddleware


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
    print("inside /")
    return render_template("base_index.html")


# https://flask.palletsprojects.com/en/stable/patterns/fileuploads/
@flask_app.route("/predict", methods=["POST"])
def predict():
    print("inside /predict")
    file = request.files["file"]
    file.save(f"'test_'+{file.filename}")

    lst_product = process_image(file.filename)
    return lst_product


@flask_app.route("/img/<image_num>", methods=["GET"])
def get_image(image_num):
    print("inside /img with fastapi , asking for image_num : ", image_num)

    image_path = f"../static/images/{image_num}.png"
    # image_path = f"/home/usr/code/pdufourny/balance_intelligente/static/images/1.png"
    print("image_path", image_path)
    return send_file(image_path)


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
            lst_product = process_image(file.filename)
            return render_template(
                "detected_product.html",
                product_id=str(lst_product["product_id"]),
                product_name=lst_product["product_name"],
                product_weight=str(lst_product["product_weight"]),
                product_price=str(lst_product["product_price"]),
                net_price=str(lst_product["net_price"]),
                confiance=str(lst_product["confiance"]),
            )

    if request.method == "GET":
        print("inside /predict : GET")
        return render_template("client_t.html")
    return


# par defaut, appels vers flask
# pour les appels fastapi, ajouter /fast/ dans l'url
# curl -X POST http://127.0.0.1:6000/fast/pred -F "file=@/home/usr/code/pdufourny/balance_intelligente/data/kiwi_test.jpg"


if __name__ == "__main__":

    # flask_app = Flask(__name__)
    # flask_app.debug = True
    flask_app.run(host="0.0.0.0", port=9000, debug=True)
