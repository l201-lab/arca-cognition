import os
import sys
import numpy as np
import logging
import datetime


def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)


def rec_dict_access(d, k0=""):
    ans = []
    for k, v in d.items():
        if isinstance(v, dict):
            prefix = k0 + " " if k0 != "" else ""
            ans.extend(rec_dict_access(v, prefix + k))
        else:
            for event in v:
                ans.append((f"{k0 + ' '+  k}", event))
    return ans


def get_date():
    return str(datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S"))


def bytes_to_np(bytes_signal):
    return np.frombuffer(bytes_signal, dtype=np.int16)


def np_to_bytes(np_signal):
    return np_signal.tobytes()


file_formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

# def get_logger(name: str, filename: str):
#     logging.basicConfig(
#         level=logging.DEBUG,
#         format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
#         datefmt='%m-%d %H:%M',
#         filename=filename,
#         filemode='w')
#     console = logging.StreamHandler()
#     console.setLevel(logging.INFO)
#
#     formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
#
#     console.setFormatter(formatter)
#     logging.getLogger('').addHandler(console)
#
#     logging.info('Jackdaws love my big sphinx of quartz.')
#
#     return logging.getLogger(name)


def setup_logger(name: str, log_file: str, level=logging.INFO):
    """Function setup as many loggers as you want"""

    file_formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    console_formatter = logging.Formatter(
        '%(name)-12s: %(levelname)-8s %(message)s')

    create_path(os.path.dirname(log_file))
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
