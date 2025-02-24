from flask import Flask, render_template, request

# from fastapi import FastAPI
# from werkzeug.middleware.dispatcher import DispatcherMiddleware
# from a2wsgi import ASGIMiddleware

############################################################
# setup flask app
############################################################
flask_app = Flask(__name__)


def init():
    print("starting")


@flask_app.route("/", methods=["GET"])
def iris_index():
    return f"OK"


# render_template("index.html")
"""
@flask_app.route("/prediction", methods=["POST","GET"])
def result():
    if request.method == "POST":
        data = request.get_json()
        print("reception ok")
        # sauvegarder image pour vérification
        return "ok"
    if request.method == 'GET':
        print("inside /predict : GET")
        return render_template('base_index.html')
    return
"""


############################################################
# fastapi
############################################################
# fast_api_app = FastAPI()


"""@fast_api_app.get("/")
def read_main():
    return {"message": "Hello World from fastapi"}



# keep this last before main()
flask_app.wsgi_app = DispatcherMiddleware(flask_app.wsgi_app, {
    '/flask': flask_app,
    '/fast': ASGIMiddleware(fast_api_app),
})
"""
if __name__ == "__main__":
    # init()
    # flask_app = Flask(__name__)
    flask_app.debug = True
    flask_app.run(host="0.0.0.0", port=8000, debug=True)
