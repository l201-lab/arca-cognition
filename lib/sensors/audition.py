from lib.sensors.sensor_base import Sensor
from lib.types import Identifier
from lib.utilities.helpers import bytes_to_np, np_to_bytes
from typing import List, Any
from collections import deque
import numpy as np
import pyaudio
import audioop
import wave
import os


class Audition(Sensor):
    """Abstracts microphone.

    Attributes:
        CHUNK (int): Number of samples.  Set to 4096.
        RATE (int): The sampling rate. Set to 4800 (Hz).
        WIDTH (int): Size of the format. Set to 2.
        FORMAT (type): Set to pyaudio.paInt16.
        CHANNELS (int): Number of channels the stream read from. Set to 1.
        SILENCE_SEC (float): Number seconds of silence/noise that will consider before and after not-noise signal. Set to 1.5.
        SILENCE_FRAMES (int): Helper variable to count number of seconds passed. Defaults to 0.
        IS_NOISE (bool): True if last read buffer was noise, false otherwise. Defaults to True.
        BIAS (int): Number that will be subtracted to the calculated threshold in setup_mic(). Set to 300.
        past_window (deque): container of the past SILENCE_SEC seconds of data.
        """
    def __init__(self, name: str):
        super().__init__(name, True)

        self.CHUNK = int(os.getenv("CHUNK"))
        self.RATE = int(os.getenv("RATE"))
        self.WIDTH = int(os.getenv("WIDTH"))
        self.FORMAT = int(os.getenv("FORMAT"))
        self.CHANNELS = int(os.getenv("CHANNELS"))
        self._p = None

        try:
            self.DEVICE_INDEX = int(os.getenv("DEVICE_INDEX"))
        except Exception:
            self.DEVICE_INDEX = None

        self.SILENCE_FRAMES = 0
        self.SILENCE_SEC = 1
        self.IS_NOISE = True
        self.BIAS = 300
        self.past_window = deque(maxlen=int(self.SILENCE_SEC * self.RATE /
                                            self.CHUNK))
        self.logger = self.get_logger()
        self.logger.info(f"CHUNK: {self.CHUNK}")
        self.logger.info(f"RATE: {self.RATE}")
        self.logger.info(f"WIDTH: {self.WIDTH}")
        self.logger.info(f"FORMAT: {self.FORMAT}")
        self.logger.info(f"CHANNELS: {self.CHANNELS}")

    def get_destinations_ID(self, raw_data: Any) -> List[Identifier]:
        """Decides which destinations to send raw_data.
        Note:
            At the moment, it picks the first destination, since there is only one compatible anyway.

        Args:
            raw_data (Any): data that will determine the relevant destination.

        Returns:
            List[Identifier]: List of Identifiers of the destinations.
        """
        return [self.destinations_ID[0]]

    def pass_msg(self, msg: str) -> None:
        """Receives a message.

        Can be of two types:
            - PAUSE: to call pause()
            - RESUME: to call resume()

        Args:
            msg (str): string sent from another Component through the Agent.

        Returns:
            None
        """
        if msg == "PAUSE":
            self.pause()
            # self._stream.stop_stream()
        elif msg == "RESUME":
            # self._stream.start_stream()
            self.resume()
        else:
            raise Exception("Unrecognized message.")

    def setup_mic(self, seconds: int = 2) -> None:
        """
        Sets up a THRESHOLD recording equal to the rms of the 20% largest bytes of a 2-second (default) signal recorded.

        Args:
            seconds: number of seconds to run the mic setup. Defaults to 2.
        """
        self.logger.info(
            "Setting up Microphone THRESHOLD. Please say something to adjust its sensitivity."
        )
        stream = self.get_stream()
        values = []
        num_samples = int(self.RATE / self.CHUNK * seconds)

        input("Press Enter when ready.")

        for i in range(num_samples):
            temp = stream.read(self.CHUNK, exception_on_overflow=False)
            if self.CHANNELS > 1:
                temp = (np.fromstring(temp, dtype=np.int16)[0::self.CHANNELS]).tostring()
            rms = audioop.rms(temp, self.WIDTH)
            values.append(rms)
            self.logger.info(f"RMS: {rms:<5}")

        values = sorted(values, reverse=True)
        self.THRESHOLD = sum(values[:int(num_samples * 0.2)]) / int(
            num_samples * 0.2) - self.BIAS
        if (self.THRESHOLD < 600):
            self.THRESHOLD = 800

        self.logger.info(f"Threshold set at {self.THRESHOLD}.")
        stream.close()

    def get_stream(self):
        """Helper function to open a pyaudio stream.

        Args:
            None

        Returns:
            stream: instance of pyaudio.Pyaudio.open()
            p: instance of pyaudio.Pyaudio
        """
        stream = self._p.open(format = self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK,
                        input_device_index=self.DEVICE_INDEX)

        return stream

    def reset_cache(self) -> None:
        self.SILENCE_FRAMES = 0
        self.IS_NOISE = True
        self.past_window.clear()
        
    def read_input(self) -> Any:
        """
        Reads a self.CHUNK from self.stream and returns it if its rms
        is over self.THRESHOLD. It will maintain self.past_window, a collection
        of the past chunks, and it will append it to the start of the first
        relevant data it encounters.

        After relevant data, self.IS_NOISE will still be True and data will be
        sent normally, but after self.SILENCE_SEC seconds it will send a chunk
        of empty data and set self.IS_NOISE to True.

        A chunk of audio is relevant if its rms exceeds the self.THRESHOLD.

        Args:
            None

        Returns:
           Any: data or None
        """

        # Reads from pyaudio.stream
        try:
            self.logger.info("Reading chunk")
            data = self._stream.read(self.CHUNK, exception_on_overflow=False)
            if self.CHANNELS > 1:
                data = (np.fromstring(data, dtype=np.int16)[0::self.CHANNELS]).tostring()
        except:
            return None

        # Takes 0.2 biggest values
        data_np = bytes_to_np(data)
        data_np = np_to_bytes(np.sort(data_np)[-int(0.2 * data_np.size):])
        # Calculates rms of sorted and sliced bytearray
        rms = audioop.rms(data_np, self.WIDTH)

        if data != b'' and rms >= self.THRESHOLD:
            self.logger.info(
                    f"RMS Sorted: {rms}\t threshold: {self.THRESHOLD}\t is_valid: True\t SILENCE_SEC: {self.SILENCE_FRAMES * self.CHUNK /self.RATE}")
            self.SILENCE_FRAMES = 0

            if self.IS_NOISE:
                past = b''.join(self.past_window)
                self.past_window.clear()
                data = past + data

            self.IS_NOISE = False
            return data
        else:
            self.logger.info(
                    f"RMS Sorted: {rms}\t threshold: {self.THRESHOLD}\t is_valid: False\t SILENCE_SEC: {self.SILENCE_FRAMES * self.CHUNK /self.RATE}")

            if not self.IS_NOISE:
                self.SILENCE_FRAMES += 1
                if (self.SILENCE_FRAMES * self.CHUNK /
                        self.RATE) >= self.SILENCE_SEC:
                    self.IS_NOISE = True
                    self.logger.info(f"\t\tSENDING BLANK PAD. TRYING TO FORCE RESET.")
                    return bytes([0] * self.CHUNK * 16)
                return data
            else:
                self.past_window.append(data)
            return None

    def setup_perceiver(self) -> None:
        self._p = pyaudio.PyAudio()
        self.setup_mic()
        self._stream = self.get_stream()

    def close_perceiver(self) -> None:
        self._stream.stop_stream()
        self._stream.close()
        self._p.terminate()

    def dump_history(self, filename: str, data: List[Any]) -> None:
        self.logger.info(f"Dumping history into {filename}.wav.")
        with wave.open(f"{filename}.wav", "wb") as waveFile:
            waveFile.setnchannels(1)
            waveFile.setsampwidth(self.WIDTH)
            waveFile.setframerate(self.RATE)
            waveFile.writeframes(b''.join(data))
