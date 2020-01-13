from dotenv import load_dotenv, find_dotenv
from pathlib import Path  # python3 only
import os

env_path = Path(os.getcwd() + "/.env")
print(env_path)
load_dotenv(dotenv_path=env_path, verbose=True)
print(os.getenv("CHUNK"))
