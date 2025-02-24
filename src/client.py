import cv2
from a2wsgi import ASGIMiddleware
from fastapi import FastAPI
from flask import Flask, render_template, request
from werkzeug.middleware.dispatcher import DispatcherMiddleware

############################################################
# aim is to test the server by sending real life images on demand
# should be replaced by a mobile app with kivy
# run with : flask --app src.client --debug run --host=0.0.0.0 --port=7000
############################################################

############################################################
# setup flask client app
############################################################
client_app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static",
)


def init():
    print("starting client")


@client_app.route("/", methods=["GET"])
def root():
    return render_template("client_t.html")


@client_app.route("/client", methods=["GET"])
def result():
    print("inside /client")
    if request.method == "GET":
        print("inside /predict : GET")
        return render_template("client_t.html")
    else:
        print("inside /client:client :", request.method)
        return
    return


############################################################
# fastapi
############################################################
fast_api_app = FastAPI()


@fast_api_app.get("/")
def read_main():
    return {"message": "Hello World from fastapi"}


# keep this last before main()
client_app.wsgi_app = DispatcherMiddleware(
    client_app.wsgi_app,
    {
        "/flask": client_app,
        "/fast": ASGIMiddleware(fast_api_app),
    },
)

if __name__ == "__main__":
    init()
    client_app = Flask(__name__)
    # flask_app.debug = True
    client_app.run(host="0.0.0.0", port=6000, debug=True)
