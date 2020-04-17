import logging
from typing import Union
import os


class Logger(logging.Logger):
    """ A simple logging class that logs to the standard logging file and the console output
     with different log levels. If "LOG_LEVEL" is specified as an environment variable, this
     log level will be used for both, console and log file."""

    def __init__(self, name: str, log_file: str = "logs/server.log", log_level: Union[str, int] = None):
        super().__init__(name)

        self.setLevel(logging.DEBUG)

        fh, ch = logging.FileHandler(log_file), logging.StreamHandler()

        fh.setLevel(logging.DEBUG if log_level is None else log_level)
        ch.setLevel(logging.INFO if log_level is None else log_level)

        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.addHandler(fh)
        self.addHandler(ch)

        self.debug("\n\n\n----------------------------------------------------------")


logger = Logger(__name__, log_level=os.getenv("LOG_LEVEL"))
