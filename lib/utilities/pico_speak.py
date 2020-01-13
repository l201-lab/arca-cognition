import sys
from subprocess import call

TEMP = "."

def say(msg: str):
    path = f"{TEMP}/temp.wav"
    call(["pico2wave", "--lang=es-ES", f"--wave={path}", msg])
    call(["aplay", path])


say(str(sys.argv[1]))
