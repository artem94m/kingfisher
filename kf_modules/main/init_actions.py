from datetime import datetime, timedelta
from logging import FileHandler, Formatter, INFO, StreamHandler, getLogger
from os import chdir, getcwd, makedirs, path, remove, scandir, sep
from sys import version_info

import config

import global_storage


class InitActions():
    def __init__(self):
        """Executes some init actions before starting a scan
        """
        self.set_cwd()
        self.init_logger()
        self.clear_old_logs()
        self.get_python_version()

    def set_cwd(self):
        """Sets kingfisher's root folder as cwd
        """
        # get current script's (init_actions.py) full filepath
        file_path = path.realpath(__file__)
        # split it by os-dependent path separator
        file_path_chunks = file_path.split(sep)
        # remove from the chunks everything up to kingfisher's root folder
        root_folder_path_chunks = file_path_chunks[:-3]
        # create root path
        root_folder_path = sep.join(root_folder_path_chunks)
        # set is as cwd
        chdir(root_folder_path)

    def init_logger(self):
        """Creates global logger
        """
        # create logger
        logger = getLogger("kingfisher")
        logger.setLevel(INFO)

        # create handler for console output
        console_handler = StreamHandler()
        console_handler.setFormatter(Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logger.addHandler(console_handler)

        try:
            # create log directory for files if it does not exist
            logs_path = path.join(getcwd(), "logs")
            makedirs(logs_path, exist_ok=True)

            # create output filename
            current_date = datetime.today().strftime("%Y-%m-%d")
            log_file_name = f"{current_date}.log"

            # create handler for file output
            file_handler = FileHandler(path.join(logs_path, log_file_name))
            file_handler.setFormatter(Formatter("%(asctime)s [%(levelname)s] %(pathname)s, "
                                                "%(funcName)s(), line:%(lineno)d - %(message)s"))
            logger.addHandler(file_handler)
        except Exception as error:
            logger.warning(f"Error during creation of FileHandler for the log file: {error}")

        # save logger in global_storage
        global_storage.logger = logger

    def clear_old_logs(self):
        """Deletes old logs, which are existing longer than config.store_logs_for
        """
        logs_path = path.join(getcwd(), "logs")

        if (path.exists(logs_path)):
            for entry in scandir(logs_path):
                if (entry.is_file()):
                    entry_last_modified = datetime.fromtimestamp(entry.stat().st_mtime)
                    current_time = datetime.now()

                    file_was_stored_for = current_time - entry_last_modified
                    time_to_store = timedelta(days=config.store_logs_for)

                    if (file_was_stored_for > time_to_store):
                        remove(entry.path)

    def get_python_version(self):
        """Stores python version in global_storage for later check
        """
        global_storage.python_version = f"{version_info.major}.{version_info.minor}"
