from defusedxml.ElementTree import parse

from kf_modules.report.design import ReportDesign

from reportlab.platypus import Paragraph


class ReportSummary():
    def __init__(self, results, logger):
        # get logger from the main module
        self.logger = logger
        # get results from the main module
        self.results = results
        # get design of the report
        self.design = ReportDesign()

    def get(self):
        """ returns content of the summary page """
        content = []

        # add skipped files if any
        if (self.results["skipped"]):
            content.append(Paragraph(f"Skipped files ({len(self.results['skipped'])})", self.design.styles["Header"]))
            for filepath in self.results["skipped"]:
                content.append(Paragraph(filepath, self.design.styles["SkippedFile"]))

        # add statistics about vulnerabilities if any
        if (self.results["vulnerabilities"]):
            vulns_by_severity, vulns_by_name = self.calculate_statistics()

            content.append(Paragraph("Vulnerabilities by severity", self.design.styles["Header"]))
            content.append(Paragraph(f"<font color='{self.design.red}'><strong>High:</strong></font> "
                                     f"{vulns_by_severity['High']}",
                                     self.design.styles["RegularParagraph"]))
            content.append(Paragraph(f"<font color='{self.design.orange}'><strong>Medium:</strong></font> "
                                     f"{vulns_by_severity['Medium']}",
                                     self.design.styles["RegularParagraph"]))
            content.append(Paragraph(f"<font color='{self.design.yellow}'><strong>Low:</strong></font> "
                                     f"{vulns_by_severity['Low']}",
                                     self.design.styles["RegularParagraph"]))
            content.append(Paragraph(f"<font color='{self.design.blue}'><strong>Info:</strong></font> "
                                     f"{vulns_by_severity['Info']}",
                                     self.design.styles["RegularParagraph"]))
            self.logger.info(f"Found High: {vulns_by_severity['High']}, Medium: {vulns_by_severity['Medium']}, "
                             f"Low: {vulns_by_severity['Low']}, Info: {vulns_by_severity['Info']}")

            content.append(Paragraph("Vulnerabilities by name", self.design.styles["Header"]))
            for check_name in vulns_by_name:
                content.append(Paragraph(f"{check_name}: <strong>{vulns_by_name[check_name]}</strong>",
                               self.design.styles["Statistics"]))

        return content

    def calculate_statistics(self):
        """ calculate some statistics about found vulnerabilities """
        vulns_by_severity = {
            "High": 0,
            "Medium": 0,
            "Low": 0,
            "Info": 0,
        }
        vulns_by_name = {}

        for check_file in sorted(self.results["vulnerabilities"]):
            # extract data from the check
            check_info = self.extract_data_from_check(check_file)

            vulns_by_name.setdefault(check_info["name"], 0)

            # go through all vulnerable files, which were found for the check
            for python_file in self.results["vulnerabilities"][check_file]:
                count_of_vulns = len(self.results["vulnerabilities"][check_file][python_file])

                vulns_by_severity[check_info["severity"]] += count_of_vulns
                vulns_by_name[check_info["name"]] += count_of_vulns

        return vulns_by_severity, vulns_by_name

    def extract_data_from_check(self, check):
        """ parse check for functions to call """
        data = {}

        try:
            # try to parse xml safely
            xml_file = parse(check, forbid_dtd=True, forbid_entities=True, forbid_external=True)
        except Exception as error:
            self.logger.error(f"Cannot parse check: {error}")
        else:
            # get <check> tag
            root = xml_file.getroot()

            for element in list(root):
                # extract all the necessary data
                if (element.tag in ["name", "description", "explanation", "severity", "recommendations", "links"]):
                    data[element.tag] = element.text.strip()

        return data
