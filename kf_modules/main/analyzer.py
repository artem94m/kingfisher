from os import path, walk as os_walk

import global_storage

from kf_modules.analyzer.assignment_in_dict import analyze_assignment_in_dict
from kf_modules.analyzer.assignment_var import analyze_assignment_var
from kf_modules.analyzer.attribute import analyze_attribute
from kf_modules.analyzer.block import analyze_block
from kf_modules.analyzer.comment import analyze_comment
from kf_modules.analyzer.function_call import analyze_function_call
from kf_modules.analyzer.function_call_with_arg import analyze_function_call_with_arg
from kf_modules.analyzer.function_call_without_arg import analyze_function_call_without_arg
from kf_modules.analyzer.string import analyze_string
from kf_modules.analyzer.unique_assignment_to_set_tuple_list import analyze_unique_assignment_to_set_tuple_list
from kf_modules.models.code_info import CodeInfoExtractor
from kf_modules.models.scan_results import FileWithIssues, ScanResults, SkippedFile


class Analyzer():
    def __init__(self, parsed_args):
        """Apply checks against the files
        """
        self.results = ScanResults(parsed_args, global_storage.checks)

        global_storage.logger.info(f"Starting scan of {parsed_args.project}...")

        for py_file_path in self.get_py_files(parsed_args.scan_path):
            py_file_info = CodeInfoExtractor(py_file_path)

            if (py_file_info.extracted_successful):
                for check in global_storage.checks:
                    self.apply_check_to_file(check, py_file_info)
            else:
                self.results.skipped_files.append(SkippedFile(py_file_info))

        self.results.calc_statistics()
        self.results.calc_scan_duration()

    def get_py_files(self, scan_path):
        """Yields .py-files for scan
        """
        if (path.isfile(scan_path)):
            yield scan_path
        elif (path.isdir(scan_path)):
            for folder_path, _, files in os_walk(scan_path, topdown=True):
                for candidate_file in files:
                    _, file_ext = path.splitext(candidate_file)

                    if (file_ext == ".py"):
                        file_path = path.join(folder_path, candidate_file)
                        yield file_path

    def apply_check_to_file(self, check, py_file_info):
        """Applies the check to the file
        """
        name_to_func = {
            "analyze_assignment_in_dict": analyze_assignment_in_dict,
            "analyze_assignment_var": analyze_assignment_var,
            "analyze_attribute": analyze_attribute,
            "analyze_block": analyze_block,
            "analyze_comment": analyze_comment,
            "analyze_function_call": analyze_function_call,
            "analyze_function_call_with_arg": analyze_function_call_with_arg,
            "analyze_function_call_without_arg": analyze_function_call_without_arg,
            "analyze_string": analyze_string,
            "analyze_unique_assignment_to_set_tuple_list": analyze_unique_assignment_to_set_tuple_list,
        }

        # set to collect locations (tuple with line_no and pos) of issues
        issues_location = set()

        for pattern in check.patterns:
            # if function is known
            if (pattern.func_to_call in name_to_func):
                analyze = name_to_func[pattern.func_to_call]

                found_issues = analyze(py_file_info, **pattern.params)
                issues_location.update(found_issues)

        if (issues_location):
            # get the CheckResult for the applied Check
            check_result = self.results.applied_checks.get(check.name)

            # get info about the vulnerable file
            file_with_issues = FileWithIssues(py_file_info, issues_location)
            # and add it to the CheckResult
            check_result.files_with_issues.append(file_with_issues)
