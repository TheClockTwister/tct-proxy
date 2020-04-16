import logging
from typing import Union
import os


class Logger(logging.Logger):
    def __init__(self, name: str, log_file: str = "logs/logs.txt", log_level: Union[str, int] = "INFO"):
        super().__init__(name)

        self.setLevel(logging.DEBUG)

        fh, ch = logging.FileHandler(log_file), logging.StreamHandler()

        fh.setLevel(logging.DEBUG)
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.addHandler(fh)
        self.addHandler(ch)

        self.debug("\n\n\n----------------------------------------------------------")


logger = Logger(__name__, log_level=os.getenv("LOG_LEVEL") if os.getenv("LOG_LEVEL") is not None else "INFO")
