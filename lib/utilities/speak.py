import sys
import pyttsx3

ES_VOICE_ID = "com.apple.speech.synthesis.voice.monica"


def init_engine():
    engine = pyttsx3.init()
    engine.setProperty('voice', ES_VOICE_ID)
    engine.setProperty('rate', 60)  # setting up new voice rate
    return engine


def say(s):
    engine.say(s)
    engine.runAndWait()  #blocks


engine = init_engine()
say(str(sys.argv[1]))
