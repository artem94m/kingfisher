# -*- coding: utf-8 -*-
from kf_modules.argparse import KfArgparse
from kf_modules.core import KfCore
from kf_modules.log import PreparedLog
from kf_modules.report import KfReport


class Kingfisher():
    def __init__(self):
        # create logger
        self.logger = PreparedLog("kingfisher")

        # parse args from console
        self.args = KfArgparse(self.logger)

        # start processing if arguments are OK
        if ((self.args.scan_path is not None) and (self.args.report_path is not None)):
            self.process()

    def process(self):
        # store results of scan here
        self.results = {}
        self.results["vulnerabilities"] = {}
        # store skipped files here
        self.results["skipped"] = []

        # add separator from previous scan log
        self.logger.info("=" * 80)
        # if any files were found
        files_found = False

        # get scan core from another module
        scan_core = KfCore(self.logger)

        # if there are available checks
        if (scan_core.has_checks()):

            self.logger.info("Start scanning...")
            # get files from scan_path
            for filepath in scan_core.get_files_for_scan(self.args.scan_path):
                # extract required data from the file
                scan_core.extract_data_from_file(filepath)

                # check if tree successfully extracted
                if (scan_core.data["tree"] is None):
                    # add file to skipped list for later processing
                    self.results["skipped"].append(filepath)
                else:
                    # for the later check of found files
                    files_found = True

                    # if there are checks to apply
                    for check in scan_core.get_checks():
                        result = scan_core.apply_check(check)

                        # the result (tuple of tuples with positions of vulnerabilities in source code) is not None -
                        # add it to the results
                        # result structure: check_name -> filename -> ((row, column), (row, column))
                        if (result is not None):
                            self.results["vulnerabilities"].setdefault(check, {})
                            self.results["vulnerabilities"][check][filepath] = result

            # if generator scan_core.get_files_for_scan() returned no files
            if (not files_found):
                self.logger.warning("There are no files for scan!")
        else:
            self.logger.error("There are no available checks!")

        if (files_found):
            # pass all the data to create a report
            KfReport(self.logger, self.args, self.results)


scanner = Kingfisher()
