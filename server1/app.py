from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello, this is your HTTP server on port 80 that gets requests from a load balancer served on port 80! Server 1"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002)
