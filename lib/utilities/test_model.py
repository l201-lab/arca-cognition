
import os
import sys
sys.path.append(os.getcwd())

from lib.utilities import settings
from lib.models.chatterbot_model import Language

lang = Language("language", "ARCA")

def test_model():
    while True:
        x = input("> ")
        if x == "stop":
            break
        data = {"text": x}
        ans = lang.chat(data)
        print(ans)

    return

if __name__ == "__main__":
    test_model()
