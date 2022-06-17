from argparse import ArgumentParser
from logging import DEBUG
from os import R_OK, W_OK, access, makedirs, path, walk
from re import match
from sys import argv

import global_storage


class ArgsParser():
    def __init__(self):
        """Parse args from the console
        """
        self.scan_path = None
        self.reports_path = None
        self.project = None
        self.verbose = None

        # create parser with all necessary arguments and descriptions
        self.parser = ArgumentParser(description="Kingfisher - Python 3 Simple Static Code Analyzer")

        self.parser.add_argument("-scan_path", metavar="SCAN_PATH", dest="scan_path", required=True,
                                 help="path to a file/folder for scanning")

        self.parser.add_argument("-reports_path", metavar="REPORTS_PATH", dest="reports_path",
                                 default="reports",
                                 help="path to store the report (default: kingfisher/reports)")

        self.parser.add_argument("-project", metavar="PROJECT", dest="project",
                                 default=None,
                                 help="project name must comply next regex: r'[a-zA-Z0-9_.-]{1,30}' "
                                 "(default: will be extracted from SCAN_PATH)")

        self.parser.add_argument("-v", dest="verbose", action="store_true",
                                 default=False,
                                 help="enable verbose mode")

        # if no args provided
        if (len(argv) == 1):
            self.parser.print_help()
        else:
            # parse args from command line
            try:
                parsed = self.parser.parse_args()
            except SystemExit:
                # output error message
                pass
            else:
                # parse all arguments separately
                self.parse_scan_path(parsed.scan_path)
                self.parse_reports_path(parsed.reports_path)
                self.parse_project(parsed.project)
                self.parse_verbose(parsed.verbose)

    def parse_scan_path(self, scan_path):
        """Parse and process -scan_path param
        """
        absolute_scan_path = path.abspath(scan_path)

        if (path.exists(absolute_scan_path)):
            if (access(absolute_scan_path, R_OK)):
                # check if there are .py-files to scan
                there_are_py_files = False

                if (path.isfile(absolute_scan_path) and absolute_scan_path.endswith(".py")):
                    there_are_py_files = True
                elif (path.isdir(absolute_scan_path)):
                    for _, _, files in walk(absolute_scan_path):
                        py_files = [file for file in files if file.endswith(".py")]
                        if (py_files):
                            there_are_py_files = True
                            break

                if (there_are_py_files):
                    self.scan_path = absolute_scan_path
                else:
                    global_storage.logger.error(f"Path {absolute_scan_path} does not contain any .py-file!")
            else:
                global_storage.logger.error(f"Path {absolute_scan_path} is not accessible for reading.")
        else:
            global_storage.logger.error(f"Path {absolute_scan_path} does not exist.")

    def parse_reports_path(self, reports_path):
        """Parse and process -reports_path param
        """
        absolute_reports_path = path.abspath(reports_path)

        if (path.exists(absolute_reports_path)):
            if (path.isdir(absolute_reports_path)):
                if (access(absolute_reports_path, W_OK)):
                    self.reports_path = absolute_reports_path
                else:
                    global_storage.logger.error(f"Path {absolute_reports_path} is not accessible for writing.")
            else:
                global_storage.logger.error(f"Path {absolute_reports_path} is not a directory.")
        else:
            try:
                makedirs(absolute_reports_path)
            except Exception as error:
                global_storage.logger.error(f"Cannot create report path {absolute_reports_path}: {error}")
            else:
                self.reports_path = absolute_reports_path

    def parse_project(self, project):
        """Parse and process -project param
        """
        # if project was set in command line and it matches
        if (project and match(r"[a-zA-Z0-9_.-]{1,30}", project)):
            self.project = project
        # if no - extract project name from the scan_path
        elif (self.scan_path and match(r"[a-zA-Z0-9_.-]{1,30}", path.basename(self.scan_path))):
            global_storage.logger.debug("Get project name from -scan_path argument.")
            self.project = path.basename(self.scan_path)

        if (self.project is None):
            global_storage.logger.error("Value for -project argument is not correct!")

    def parse_verbose(self, verbose):
        """Parse and process -v param
        """
        self.verbose = verbose

        if (verbose):
            global_storage.logger.setLevel(DEBUG)

    @property
    def are_correct(self):
        """Checks if all the arguments were parsed correctly
        """
        result = True

        if (self.scan_path is None or
                self.reports_path is None or
                self.project is None or
                self.verbose is None):
            result = False

        return result
