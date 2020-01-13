import os
import sys
sys.path.append(os.getcwd())

from lib.utilities import settings
import pyaudio
import wave
from tqdm import tqdm
from lib.interpreters.nlp import normalize, tokenize, untokenize

CHUNK = int(os.getenv("CHUNK"))
FORMAT = int(os.getenv("FORMAT"))
CHANNELS = int(os.getenv("CHANNELS"))
RATE = int(os.getenv("RATE"))
WIDTH = int(os.getenv("WIDTH"))
TEST_FOLDER = f"resources/tests/sr"


def setup_pyaudio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    return p, stream


def record(seconds):
    p, stream = setup_pyaudio()
    frames = []

    for i in tqdm(range(0, int(RATE / CHUNK * seconds)), "Recording..."):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()
    return b''.join(frames)


def save(data, filename):
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(WIDTH)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()


def clean(x: str):
    x = normalize(x)
    x_tokens = [word.lower() for word in tokenize(x) if word.isalnum()]
    return untokenize(x_tokens)


def get_descriptive_name(s: str):
    res = "_".join(s.split(' '))[:20]
    base_path = f"{TEST_FOLDER}/{res}"

    i = 0
    fn = base_path + f"{i:03d}"

    while os.path.exists(fn + ".wav") or os.path.exists(fn + ".txt"):
        i += 1
        fn = base_path + f"{i:03d}"

    return fn


def main():
    global TEST_FOLDER
    TEST_FOLDER = os.getcwd() + "/resources/tests/sr"

    temp = os.listdir(TEST_FOLDER)
    for i, test_folder in enumerate(temp):
        print(i, test_folder)
    i = int(input("Select index of your folder: "))
    TEST_FOLDER += f"/{temp[i]}"

    seconds = int(input("Enter record time (in seconds): "))
    input("Press Enter when ready to record.")

    data = record(seconds)
    ans = input("Enter transcription of current audio: ")
    ans = clean(ans)
    filename = get_descriptive_name(ans)
    save(data, filename + ".wav")
    with open(filename + ".txt", "w+") as f:
        f.write(ans + '\n')


if __name__ == "__main__":
    main()
