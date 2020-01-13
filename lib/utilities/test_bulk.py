import os
import sys
sys.path.append(os.getcwd())

import wave
from typing import List
from lib.interpreters.speech_recognizer import SpeechRecognizer
from lib.interpreters.nlp import normalize, tokenize, untokenize
from Levenshtein import jaro
from lib.utilities import settings  # for loading dotenv
import pandas as pd


def process(sr, wf):
    chunk = int(os.getenv("CHUNK"))
    data = wf.readframes(chunk)
    while data != b'':
        gen = sr.process(data)
        stop = next(gen)
        if stop:
            ans = next(gen)
            return ans
        data = wf.readframes(chunk)
    for i in range(4):
        gen = sr.process(bytes(chunk * [0]))
        if stop:
            ans = next(gen)
            return ans
    return None


def compare(x, y):
    if x is None:
        return [0, x, y]

    x = normalize(x)
    x_tokens = [word.lower() for word in tokenize(x) if word.isalnum()]

    y = normalize(y)
    y_tokens = [word.lower() for word in tokenize(y) if word.isalnum()]

    ppx = untokenize(x_tokens)
    ppy = untokenize(y_tokens)

    return [jaro(ppx, ppy), ppx, ppy]


def test_sr(X: List[str], Y: List[str]):
    """
    X : list of wav filenames.
    Y : list of translations of their corresponding file
    """

    sr = SpeechRecognizer("test_sr", "googlespeech")
    Yp = []
    accuracies = []
    PPX = []
    PPY = []

    for i, filename in enumerate(X):
        wf = wave.open(filename, 'rb')
        if wf.getframerate() != int(os.getenv("RATE")):
            raise Exception("RATE of recorded audio doesn't match mic RATE.")
        ans = process(sr, wf)
        acc, ppx, ppy = compare(ans, Y[i])
        Yp.append(ans)
        accuracies.append(acc)
        PPX.append(ppx)
        PPY.append(ppy)

    raw = {
        'file': X,
        'text': Y,
        'guess': Yp,
        'norm_text': PPX,
        'norm_y': PPY,
        'accuracy': accuracies
    }
    df = pd.DataFrame(raw)

    return df


def main():
    tests_path = os.getcwd() + "/resources/tests/sr"
    X = []
    Y = []

    temp = os.listdir(tests_path)
    for i, test_folder in enumerate(temp):
        print(i, test_folder)
    i = int(input("Select index of your folder: "))
    tests_path += f"/{temp[i]}"

    print(tests_path)
    print(os.listdir(tests_path))
    for f in os.listdir(tests_path):
        if f.endswith(".wav"):
            X.append(os.path.join(tests_path, f))
            basename = os.path.splitext(tests_path + "/" + f)[0]
            with open(basename + ".txt") as g:
                Y.append(g.readline())

    df = test_sr(X, Y)
    score = round(df["accuracy"].mean(), 3)
    df.to_csv(f"{tests_path}/results-{score}.csv")


if __name__ == "__main__":
    main()
