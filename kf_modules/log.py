from datetime import datetime
from inspect import getframeinfo, stack
from logging import DEBUG, FileHandler, Formatter, INFO, StreamHandler, getLogger, shutdown
from os import makedirs, path


class PreparedLog():
    def __init__(self, logger_name):
        """ create prepared logger """

        # create logger
        self.logger = getLogger(logger_name)
        self.logger.setLevel(INFO)

        # create handler for console output
        console_handler = StreamHandler()
        console_handler.setFormatter(Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        self.logger.addHandler(console_handler)

        try:
            # create log directory for files if it does not exist
            if not path.exists("logs"):
                makedirs("logs")

            # create output filename
            current_date = datetime.today().strftime("%Y-%m-%d")
            filename = f"{logger_name}_{current_date}.log"

            # create handler for file output
            file_handler = FileHandler(path.join("logs", filename))
            file_handler.setFormatter(Formatter("%(asctime)s [%(levelname)s] %(real_filename)s,"
                                                "%(real_funcname)s(), line:%(real_lineno)d - %(message)s"))
            self.logger.addHandler(file_handler)
        except Exception as error:
            self.logger.warning(f"Error during creation of log file: {error}")

    def info(self, msg):
        """ print INFO message """
        # get real file name, line number, function name
        caller = getframeinfo(stack()[1][0])
        extra = {
            "real_filename": path.relpath(caller.filename),
            "real_lineno": caller.lineno,
            "real_funcname": caller.function,
        }

        self.logger.info(msg, extra=extra)

    def warning(self, msg):
        """ print WARNING message """
        # get real file name, line number, function name
        caller = getframeinfo(stack()[1][0])
        extra = {
            "real_filename": path.relpath(caller.filename),
            "real_lineno": caller.lineno,
            "real_funcname": caller.function,
        }

        self.logger.warning(msg, extra=extra)

    def error(self, msg):
        """ print ERROR message """
        # get real file name, line number, function name
        caller = getframeinfo(stack()[1][0])
        extra = {
            "real_filename": path.relpath(caller.filename),
            "real_lineno": caller.lineno,
            "real_funcname": caller.function,
        }

        self.logger.error(msg, extra=extra)

    def debug(self, msg):
        """ print DEBUG message """
        # get real file name, line number, function name
        caller = getframeinfo(stack()[1][0])
        extra = {
            "real_filename": path.relpath(caller.filename),
            "real_lineno": caller.lineno,
            "real_funcname": caller.function,
        }

        self.logger.debug(msg, extra=extra)

    def set_verbose(self):
        """ activate verbose log by changing level of logger """
        self.logger.setLevel(DEBUG)

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
        shutdown()
