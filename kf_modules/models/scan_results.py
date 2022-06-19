from datetime import datetime

import global_storage


class ScanResults():
    """Class to store all info about scan
    """
    def __init__(self, parsed_args, parsed_checks):
        self.project = parsed_args.project
        self.scan_path = parsed_args.scan_path

        self.start_scan_timestamp = datetime.now()
        self.duration = None

        self.applied_checks = CheckResults(parsed_checks)
        self.skipped_files = []

        # statistics
        self.issues_by_check = {}

        self.high_issues = 0
        self.medium_issues = 0
        self.low_issues = 0
        self.info_issues = 0

    def calc_scan_duration(self):
        """Calcs duration of the scan only once
        """
        if (self.duration is None):
            self.duration = str(datetime.now() - self.start_scan_timestamp)
            global_storage.logger.info(f"Scan took: {self.duration}")

    def calc_statistics(self):
        """Calcs statistics for found vulnerabilities
        """
        # severity level in check to attr of ScanResults
        severity_to_attr = {
            "High": "high_issues",
            "Medium": "medium_issues",
            "Low": "low_issues",
            "Info": "info_issues",
        }

        # go through the applied check
        for check_result in self.applied_checks:
            # collect number of issues per check
            number_of_issues = 0
            for file_with_issues in check_result.files_with_issues:
                number_of_issues += len(file_with_issues.issues)

            # collect only info about check with found issues
            if (number_of_issues):
                self.issues_by_check[check_result.check_name] = number_of_issues

            # increase number of issues in category according to the check's severity
            original_check = global_storage.checks.get(check_result.check_name)
            if (original_check and original_check.severity in severity_to_attr):
                # get attribute name to edit
                severity_attr = severity_to_attr[original_check.severity]
                # get updated number of issues for the category
                updated_number_of_issues = getattr(self, severity_attr) + number_of_issues
                # and update it
                setattr(self, severity_attr, updated_number_of_issues)

        message = f"Found issues: High: {self.high_issues}, Medium: {self.medium_issues}, "\
                  f"Low: {self.low_issues}, Info: {self.info_issues}"
        global_storage.logger.info(message)


class CheckResults(list):
    """Class to store results for all the parsed checks
    """
    def __init__(self, parsed_checks):
        """Inits CheckResults with names of already parsed Checks
        """
        for check in parsed_checks:
            self.append(CheckResult(check.name))

    def get(self, check_name):
        """Returns CheckResult for the specified name of the check
        """
        result = None

        for check_result in self.__iter__():
            if (check_result.check_name == check_name):
                result = check_result
                break

        return result


class CheckResult():
    def __init__(self, check_name):
        self.check_name = check_name
        self.files_with_issues = []


class FileWithIssues():
    def __init__(self, py_file_info, issues_location):
        self.file_path = py_file_info.file_path
        self.issues = sorted(list(issues_location))
        self.lines_with_issues = self.get_lines_with_issues(py_file_info.source_code, self.issues)

    def get_lines_with_issues(self, source_code, issues_location):
        """Extracts from the source code only lines with issues
        """
        result = {}

        # get unique lines to extract
        lines_to_get = {line_no for line_no, _pos in issues_location}

        for line_no in lines_to_get:
            result[line_no] = source_code[line_no]

        return result


class SkippedFile():
    """Class to store info about files, excluded from the scan
    """
    def __init__(self, py_file_info):
        self.file_path = py_file_info.file_path
        self.failure_reason = py_file_info.failure_reason
