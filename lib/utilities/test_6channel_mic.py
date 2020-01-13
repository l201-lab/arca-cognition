import wave
import numpy as np
import pyaudio

RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 6  # change base on firmwares, 1_channel_firmware.bin as 1 or 6_channels_firmware.bin as 6
RESPEAKER_WIDTH = 2
# run getDeviceInfo.py to get index
RESPEAKER_INDEX = 2  # refer to input device id
CHUNK = 1024
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

stream = p.open(rate=RESPEAKER_RATE,
                format=p.get_format_from_width(RESPEAKER_WIDTH),
                channels=RESPEAKER_CHANNELS,
                input=True,
                input_device_index=RESPEAKER_INDEX)

print("* recording")

frames = []

for i in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    a = [0] * RESPEAKER_CHANNELS
    for j in range(RESPEAKER_CHANNELS):
        temp = np.fromstring(data, dtype=np.int16)[j::6]
        a[j] = temp
        if i == 0:
            frames.append([a[j].tostring()])
        else:
            frames[j].append(a[j].tostring())

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

for j in range(RESPEAKER_CHANNELS):
    wf = wave.open(f"output{j}.wav", 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(
        p.get_format_from_width(RESPEAKER_WIDTH)))
    wf.setframerate(RESPEAKER_RATE)
    wf.writeframes(b''.join(frames[j]))
    wf.close()
