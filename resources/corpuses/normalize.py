from nltk.tokenize.toktok import ToktokTokenizer
import string
import sys
import unicodedata

tokenize = ToktokTokenizer().tokenize


def untokenize(tokens):
    return ("".join([
        " " + token if not (token.startswith("'")
                            or tokens[i - 1] in ['¿', '¡'] or token == "...")
        and token not in string.punctuation else token
        for i, token in enumerate(tokens)
    ]).strip())


def fix(line):
    if (line[0:3] == "- -" or line[0:3] == "  -"):
        return '\n' + line[:4] + preprocess(line[4:])
    elif (line[0:3] == "   "):
        return " " + preprocess(line[4:])
    else:
        return line


def preprocess(sent):
    # Remove all non-ascii characters
    res = unicodedata.normalize('NFKD', sent).encode('ascii',
                                                     'ignore').decode('utf8')
    # tokenize
    tokens = tokenize(res)
    print(f"ORIG: {tokens}")
    # Remove all non-alphanumerical tokens and lowercase them
    tokens = [word.lower() for word in tokens if word.isalnum()]
    print(f"LOWER + AN: {tokens}")

    # Put tokens together
    res = untokenize(tokens)
    return res


def main(filename):
    f = open(filename, "r")
    g = open(f"ppr_{filename}", "w+")

    for line in f.readlines():
        g.write(fix(line))

    f.close()
    g.close()


if __name__ == "__main__":
    for filename in sys.argv[1:]:
        main(filename)
