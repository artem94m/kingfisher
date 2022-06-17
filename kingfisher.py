# -*- coding: utf-8 -*-
import global_storage

from kf_modules.main.analyzer import Analyzer
from kf_modules.main.args_parser import ArgsParser
from kf_modules.main.checks_parser import ChecksParser
from kf_modules.main.init_actions import InitActions
from kf_modules.main.report import ReportGenerator


class Kingfisher():
    def __init__(self):
        InitActions()

        parsed_args = ArgsParser()

        if (parsed_args.are_correct):
            global_storage.checks = ChecksParser().get_checks()

            if (global_storage.checks):
                scan_results = Analyzer(parsed_args).results
                ReportGenerator(parsed_args.reports_path, scan_results)


if (__name__ == "__main__"):
    Kingfisher()
