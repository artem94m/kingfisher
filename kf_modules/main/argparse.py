from argparse import ArgumentParser
from os import R_OK, W_OK, access, makedirs, path
from re import match
from sys import argv


class KfArgparse():
    def __init__(self, logger):
        """ parse args from console """
        # get logger from main module
        self.logger = logger

        # arguments data
        self.scan_path = None
        self.report_path = None
        self.project_name = None

        # create parser with all necessary arguments and descriptions
        self.parser = ArgumentParser(description="Kingfisher - Python 3 Simple Static Code Analyzer")
        # path to a folder or file (required)
        scan_path_help = "the path to a file/folder for scanning"
        self.parser.add_argument("-scan", metavar="SCAN_PATH", dest="scan_path",
                                 required=True, help=scan_path_help)
        # path to a folder with all reports (default: "reports" in the same catalog)
        report_path_help = "the path to a reports folder (default: reports)"
        self.parser.add_argument("-report_folder", metavar="REPORT_PATH", dest="report_path",
                                 default="reports", help=report_path_help)
        # project name - for creating a report file
        project_name_help = "name of the scanned project (default: will be extracted from a file or folder name)"
        self.parser.add_argument("-project", metavar="PROJECT_NAME", dest="project_name",
                                 help=project_name_help)
        # verbose mode - for printing DEBUG messages
        self.parser.add_argument("-v", dest="verbose_mode", action="store_true")

        self.parse()

    def parse(self):
        # if no args provided
        if (len(argv) == 1):
            self.parser.print_help()
        else:
            # parse args from command line
            try:
                parsed = self.parser.parse_args()
            except SystemExit:
                # can do nothing here, really
                pass
            else:
                # parse all arguments separately
                self.parse_scan_path(parsed.scan_path)
                self.parse_report_path(parsed.report_path)
                self.parse_project_name(parsed.project_name)
                self.parse_verbose_mode(parsed.verbose_mode)

    def parse_scan_path(self, scan_path):
        """ process parsed scan path """
        scan_path = path.normpath(scan_path)
        if (path.exists(scan_path)):
            # if it is accessible for reading
            if (access(scan_path, R_OK)):
                self.scan_path = scan_path
            else:
                self.logger.error(f"Path {scan_path} is not accessible for reading.")
        else:
            self.logger.error(f"Path {scan_path} does not exist.")

    def parse_report_path(self, report_path):
        """ process parsed report path """
        report_path = path.normpath(report_path)
        # there is a default value for report path - "reports" folder
        # but a different path also can be provided
        if path.exists(report_path):
            if path.isdir(report_path):
                if (access(report_path, W_OK)):
                    self.report_path = report_path
                else:
                    self.logger.error(f"Path {report_path} is not accessible for writing.")
            else:
                self.logger.error(f"Path {report_path} is not a directory.")
        # if not exists - try to create
        else:
            try:
                makedirs(report_path)
            except Exception as error:
                self.logger.error(f"Cannot create report path: {error}")
            else:
                self.report_path = report_path

    def parse_project_name(self, project_name):
        # if project_name was set in command line and it matches RE
        if (project_name is not None and match(r"[a-zA-Z0-9_.-]+", project_name)):
            self.project_name = project_name
        # if no - extract project name from the scan_path
        elif (self.scan_path is not None):
            self.project_name = path.basename(self.scan_path)

    def parse_verbose_mode(self, verbose):
        if (verbose):
            self.logger.set_verbose()

    def are_ok(self):
        result = False
        if (self.scan_path is not None and
                self.report_path is not None and
                self.project_name is not None):
            result = True

        return result
