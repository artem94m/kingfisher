import os
import argparse
import sys
import re


class KfArgparse():
    def __init__(self, logger):
        """ parse args from console """
        # get logger from main module
        self.logger = logger

        self.scan_path = None
        self.report_path = None
        self.project_name = None

        # create parser with all necessary arguments and descriptions
        parser = argparse.ArgumentParser(description="Kingfisher - Python 3 Simple Static Code Analyzer")
        # path to a folder or file (required)
        parser.add_argument("-scan", metavar="SCAN_PATH", dest="scan_path", required=True, help="the path to a file/folder for scanning")
        # path to a folder with all reports (default: "reports" in the same catalog)
        parser.add_argument("-report_folder", metavar="REPORT_PATH", dest="report_path", default="reports", help="the path to a reports folder (default: reports)")
        # project name - for creating a report file
        parser.add_argument("-project", metavar="PROJECT_NAME", dest="project_name", help="name of the scanned project (default: will be extracted from a file or folder name)")

        # if no args provided
        if (len(sys.argv) == 1):
            parser.print_help()
        else:
            # parse args from command line
            try:
                parsed = parser.parse_args()
            except SystemExit:
                # can do nothing here, really
                pass
            else:
                # normalize parsed paths
                parsed.scan_path = os.path.normpath(parsed.scan_path)
                parsed.report_path = os.path.normpath(parsed.report_path)

                # if scan_path exits
                if (os.path.exists(parsed.scan_path)):
                    # and it is accessible for reading
                    if os.access(parsed.scan_path, os.R_OK):
                        self.scan_path = parsed.scan_path
                    else:
                        self.logger.error("Path {} is not accessible for reading.".format(parsed.scan_path))
                else:
                    self.logger.error("Path {} does not exist.".format(parsed.scan_path))

                # if project_name was set in command line and it matches RE
                if (parsed.project_name is not None and re.match(r"[a-zA-Z0-9_.-]+", parsed.project_name)):
                    self.project_name = parsed.project_name
                # if no - extract project name from the scan_path
                elif (self.scan_path is not None and (os.path.isfile(self.scan_path) or os.path.isdir(self.scan_path))):
                    self.project_name = os.path.basename(self.scan_path)

                # there is a default value for report path - "reports" folder
                # but a different path also can be provided
                # check if it exists
                if os.path.exists(parsed.report_path):
                    # and if it is directory
                    if os.path.isdir(parsed.report_path):
                        # which is accessible for writing
                        if os.access(parsed.report_path, os.W_OK):
                            self.report_path = parsed.report_path
                        else:
                            self.logger.error("Path {} is not accessible for writing.".format(parsed.report_path))
                    else:
                        self.logger.error("Path {} is not a directory.".format(parsed.report_path))
                # if not exists - try to create
                else:
                    try:
                        os.makedirs(parsed.report_path)
                    except Exception as error:
                        self.logger.error("Cannot create report path: {}".format(str(error)))
                    else:
                        self.report_path = parsed.report_path
