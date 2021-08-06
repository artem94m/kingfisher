import logging
import os
from inspect import getframeinfo, stack
from datetime import datetime


class PreparedLog():
    def __init__(self, logger_name):
        """ create prepared logger """

        # create logger
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)

        # create handler for console output
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # create and set output format
        ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

        # add the handlers to the log
        self.logger.addHandler(ch)

        try:
            # create log directory for files if it does not exist
            if not os.path.exists("logs"):
                os.makedirs("logs")

            # create output filename
            filename = "{}_{}.log".format(logger_name, datetime.today().strftime("%Y-%m-%d"))

            # create handler for file output
            fh = logging.FileHandler(os.path.join("logs", filename))
            fh.setLevel(logging.DEBUG)

            # set output format
            fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(real_filename)s, %(real_funcname)s(), line:%(real_lineno)d - %(message)s"))

            # add the handlers to the log
            self.logger.addHandler(fh)
        except Exception as error:
            self.logger.warning("Error during creation of log file: {}".format(str(error)))

    def info(self, msg):
        # get file name, line number, function name
        caller = getframeinfo(stack()[1][0])
        extra = {
            "real_filename": os.path.relpath(caller.filename),
            "real_lineno": caller.lineno,
            "real_funcname": caller.function
        }

        self.logger.info(msg, extra=extra)

    def warning(self, msg):
        # get file name, line number, function name
        caller = getframeinfo(stack()[1][0])
        extra = {
            "real_filename": os.path.relpath(caller.filename),
            "real_lineno": caller.lineno,
            "real_funcname": caller.function
        }

        self.logger.warning(msg, extra=extra)

    def error(self, msg):
        # get file name, line number, function name
        caller = getframeinfo(stack()[1][0])
        extra = {
            "real_filename": os.path.relpath(caller.filename),
            "real_lineno": caller.lineno,
            "real_funcname": caller.function
        }

        self.logger.error(msg, extra=extra)

    def __del__(self):
        """ remove and close all handlers """
        if (self.logger is not None):
            handlers = self.logger.handlers[:]
            # flush, close and remove every handler
            for handler in handlers:
                handler.flush()
                handler.close()
                self.logger.removeHandler(handler)

        # and the control shot
        logging.shutdown()
