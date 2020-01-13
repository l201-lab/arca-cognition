from flask import Flask
import os, sys, datetime

app = Flask(__name__)
LOGDIR = "logs"


def execute(**kwargs):
    timestamp = str(datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S"))

    path = LOGDIR

    if not os.path.exists(f"{path}/{__name__}"):
        os.mkdir(f"{path}/{__name__}")

    path = f"{path}/{__name__}"

    os.mkdir(f"{path}/{timestamp}")

    path = f"{path}/{timestamp}"

    sys.stdout = open(f"{path}/stdout.txt", "a")
    sys.stderr = open(f"{path}/stderr.txt", "a")
    app.run(kwargs)


@app.route('/')
def hello():
    return "Hello World!"
