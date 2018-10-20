"""logger.py
Simple interface to the built-in Python logger."""

import logging
import os
import time


class Logger(object):
    """Setup the logger and allow clients to get the current logger."""

    def __init__(self, log_name=None):
        """Create the logs directory and instantiate the log name and format.

        Args:
            log_name(str): The name of the log to use. If none is set, then
            the logs should go into logs/log_[timestamp].log.
        """
        # Try to make the logs directory if its not already there
        try:
            os.mkdir("./logs")
        except FileExistsError:
            pass

        # Setup the initial name and format
        if log_name is None:
            log_name = time.strftime("./logs/log_%Y_%m_%d_%H-%M-%S-%Z.log")

        logging.basicConfig(filename=log_name,
                            format="%(asctime)s - %(filename)s.%(funcName)s - "
                                   "%(levelname)s - %(message)s",
                            level=logging.DEBUG)

    @staticmethod
    def get_logger():
        """Get the root logger.

        Returns:
            The root logging.Logger.
        """
        return logging.getLogger()

