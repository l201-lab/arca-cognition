from pattern.es import parse, split, conjugate, PRESENT, IMPERATIVE, SG
from lib.interpreters.interpreter_base import Interpreter
from nltk.tokenize.toktok import ToktokTokenizer
from typing import List, Generator, Any, Tuple
from lib.types import Identifier
import unicodedata
import requests
import string
import re
import os

pron_refl = ["me", "te", "se", "nos", "os"]
pron_dobj = ["lo", "los", "la", "las"]
enclitic_pat = re.compile(
    f".*(?={'|'.join(pron_refl)})(?={'|'.join(pron_dobj)})?")
NLP_API_URI = os.getenv("NLP_API_URI")


def tokenize(s: str):
    return ToktokTokenizer().tokenize(s)


def untokenize(tokens):
    return ("".join([
        " " + token if not (token.startswith("'")
                            or tokens[i - 1] in ['¿', '¡'] or token == "...")
        and token not in string.punctuation else token
        for i, token in enumerate(tokens)
    ]).strip())


def normalize(string: str):
    res = unicodedata.normalize('NFKD',
                                string).encode('ascii',
                                               'ignore').decode('utf-8')
    return res


class NLP(Interpreter):
    def __init__(self, name: str):
        super().__init__(name, False)
        name, cat = self.dumpID().to_tuple()
        self.logger = self.get_logger()

    def get_destinations_ID(self, raw_data) -> List[Identifier]:
        return [self.destinations_ID[0]]

    def preprocess(self, raw_data):
        if raw_data is None:
            return None
        # Remove all non-ascii characters
        res = normalize(raw_data)

        # tokenize
        tokens = tokenize(res)

        # Remove all non-alphanumerical tokens and lowercase them
        tokens = [word.lower() for word in tokens if word.isalnum()]

        # Put tokens together
        res = untokenize(tokens)
        return res

    def process(self, raw_data) -> Generator:
        yield True
        r = requests.get(f"{NLP_API_URI}/nlp/process", params={'sent': raw_data})

        if r.status_code == 200:
            self.logger.info(r.json())
            yield r.json()
        else:
            self.logger.info("Empty or invalid sentence")
            yield None
        return

    def pass_msg(self, msg: str) -> None:
        pass

    def dump_history(self, filename: str, data: List[Any]) -> None:
        pass
