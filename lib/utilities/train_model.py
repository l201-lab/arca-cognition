import os
import sys
sys.path.append(os.getcwd())

from lib.utilities import settings
from lib.models.chatterbot_model import Language
from chatterbot.trainers import ListTrainer


lang = Language("language", "ARCA")
trainer = ListTrainer(lang.chatbot)


def train_model(corpus: str = None):
    sentences = []

    if corpus is not None and os.path.exists(corpus):
        filename = f"{os.getcwd()}/{corpus}"
        print(filename)

        print("Training...")
        lang.train([filename])
        print("Done.")
        return
    else:
        while True:
            line = input(">> ")
            if line == "/exit":
                break
            ans = lang.chat({"text": line})[0]["data"]
            print("[ARCA]: ", ans)
            sentences.append(line)
    for sent in sentences:
        print(sent)
    x = input("Want to use this conversation to train the model? (y/n)")
    if x == "y":
        print("Training...")
        trainer.train(sentences)
    print("Done.")
  
if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1:
        for arg in args[1:]:
            train_model(arg)
    else:
        train_model()
