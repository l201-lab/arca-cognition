from flask import Flask, request, jsonify, make_response
from duckling import DucklingWrapper, Language
from dotenv import load_dotenv
import os
import unicodedata
load_dotenv()

app = Flask(__name__)
duck = DucklingWrapper(language=Language.SPANISH, maximum_heap_size='512m')
DUCKLING_HOST = os.getenv("DUCKLING_HOST")
DUCKLING_PORT = os.getenv("DUCKLING_PORT")


def normalize(string: str):
    res = unicodedata.normalize('NFKD',
                                string).encode('ascii',
                                               'ignore').decode('utf-8')
    return res


def _parse_date(sent: str):
    if sent is None:
        return None
    ans = duck.parse_time(sent)
    precedence = ["year", "month", "day", "hour", "minute", "second"]

    if len(ans) > 0:
        text = ans[0]["text"]
        val = ans[0]["value"]["value"]
        if "grain" in ans[0]["value"]:
            if normalize(text.lower()) not in [
                    "manana", "pasado manana", "ayer", "hoy"
            ]:
                precision = precedence[
                    precedence.index(ans[0]["value"]["grain"]) - 1]
            else:
                precision = precedence[
                    precedence.index(ans[0]["value"]["grain"])]
        else:
            precision = None

        if "to" in val:
            return {"text": text, "value": val["to"], "precision": precision}
        else:
            return {"text": text, "value": val, "precision": precision}
    else:
        return None


@app.route('/')
def parse_date():
    sent = request.args.get('sent')
    if sent is not None and sent != "":
        body = _parse_date(sent)
        code = 200
    else:
        body = {"message": "Bad Request"}
        code = 400
    res = make_response(jsonify(body), code)
    return res


if __name__ == '__main__':
    print("DUCKLING AT: ", DUCKLING_HOST, DUCKLING_PORT)
    app.run(port=DUCKLING_PORT)
