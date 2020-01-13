from lib.interpreters.interpreter_base import Interpreter
from lib.types import Identifier
from typing import List, Generator, Any
from pocketsphinx.pocketsphinx import Decoder
from google.cloud import speech
from google.oauth2 import service_account
import os


class SpeechRecognizer(Interpreter):
    def __init__(self, name: str, sr: str = "pocketsphinx"):
        super().__init__(name, True)
        self.logger = self.get_logger()
        self.sr = sr
        self.current_data = []
        self.setup()

    def setup(self) -> None:
        self.RATE = int(os.getenv("RATE"))
        self.CHUNK = int(os.getenv("CHUNK"))
        self.setup_pocketsphinx()

        if (self.sr == "googlespeech"):
            self.setup_googlespeech()

    def setup_pocketsphinx(self) -> None:
        self.logger.info("Setting up PocketSphinx.")
        self.MODELDIR = "resources/model"

        config = Decoder.default_config()
        config.set_string('-hmm', os.path.join(self.MODELDIR, 'es-es'))
        config.set_string('-lm', os.path.join(self.MODELDIR, 'es-es.lm'))
        config.set_string('-dict', os.path.join(self.MODELDIR, 'es.dict'))
        config.set_string('-logfn', '/dev/null')

        self.decoder = Decoder(config)

        self.prev_buf_is_speech = False
        self.decoder.start_utt()
        self.logger.info("Done setting up PocketSphinx.")

    def setup_googlespeech(self) -> None:
        self.logger.info("Setting up Google Speech.")
        credentials = service_account.Credentials.from_service_account_file(
            'resources/keys/credentials.json')
        config = speech.types.RecognitionConfig(
            encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code='es-PE',
            sample_rate_hertz=self.RATE,
        )
        self.client = speech.SpeechClient(credentials=credentials)
        self.streaming_config = speech.types.StreamingRecognitionConfig(
            config=config)
        self.logger.info("Done setting up Google Speech.")

    def get_destinations_ID(self, raw_data) -> List[Identifier]:
        return [self.destinations_ID[0]]

    def preprocess(self, raw_data):
        """Filtering"""
        return raw_data

    def query_gs(self):
        requests = (speech.types.StreamingRecognizeRequest(audio_content=chunk)
                    for chunk in self.current_data)
        responses = self.client.streaming_recognize(
            config=self.streaming_config, requests=requests)
        try:
            response = next(responses)
            data = response.results[0].alternatives[0].transcript
            conf = response.results[0].alternatives[0].confidence
        except Exception as e:
            self.logger.info(f"{self.name}>> {e}")
            conf = None
            data = None
        self.current_data.clear()
        return data, conf

    def query_ps(self):
        try:
            data = self.decoder.hyp().hypstr
            conf = self.decoder.hyp().best_score
            if data == "":
                data = None
        except Exception as e:
            self.logger.info(f"{self.name}>> {e}")
            conf = None
            data = None
        return data, conf

    def process(self, raw_data) -> Generator:
        self.decoder.process_raw(raw_data, False, False)
        cur_buf_is_speech = self.decoder.get_in_speech()
        data = None
        self.logger.info(
            f"prev: {self.prev_buf_is_speech}, current: {cur_buf_is_speech}")

        force_speech = False
        if raw_data == bytes([0] * self.CHUNK * 16):
            force_speech = True
            self.logger.info("RECEIVED FORCE STOP")

        if force_speech or (self.prev_buf_is_speech and not cur_buf_is_speech):
            # No longer in speech -> stop listening and process
            self.logger.info("No longer in speech, yielding True.")
            yield True
            self.decoder.end_utt()
            if (self.sr == "googlespeech"):
                data, conf = self.query_gs()
            elif (self.sr == "pocketsphinx"):
                data, conf = self.query_ps()
            self.logger.info(
                f"{self.name}>> Heard DATA: '{data}' with confidence: {conf}.")
            self.decoder.start_utt()
            self.prev_buf_is_speech = cur_buf_is_speech
        elif not self.prev_buf_is_speech and cur_buf_is_speech:
            # Now in speech -> Start listening
            self.current_data.append(raw_data)
            self.prev_buf_is_speech = cur_buf_is_speech
            yield False

        elif self.prev_buf_is_speech and cur_buf_is_speech:
            # Still in speech -> Keep on listening
            self.current_data.append(raw_data)
            self.prev_buf_is_speech = cur_buf_is_speech
            yield False

        else:
            self.prev_buf_is_speech = cur_buf_is_speech
            yield False

        yield data
        return

    def pass_msg(self, msg: str) -> None:
        if msg == "RESUME":
            self.e.set()

    def dump_history(self, filename: str, data: List[Any]) -> None:
        pass
