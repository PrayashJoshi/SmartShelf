from flask import Flask

app = Flask("api")

@app.route("/", methods=["GET"])
def hello():
    return "Hello, World!"