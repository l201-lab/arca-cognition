import pyttsx3
engine = pyttsx3.init()


def list_voices():
    voices = engine.getProperty('voices')
    for voice in voices:
        print(voice, voice.id)
        engine.setProperty('voice', voice.id)
        # engine.say("Hello World!")
        engine.runAndWait()
        engine.stop()

def test_voice(sent, voiceid):

    engine.setProperty('voice', voiceid)
    engine.say(sent)
    engine.runAndWait()
    engine.stop()


spid = "spanish-latin-am"
test_voice("Hola mundo!", spid)
