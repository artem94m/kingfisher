from xml.sax.saxutils import escape

import global_storage

from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, Preformatted, Table, XPreformatted


class ReportVulnerabilities():
    """Creates content for the results of the applied checks
    """
    def __init__(self, scan_results):
        self.data = []

        # add page title
        self.data.append(Paragraph("Issues", global_storage.design.styles["H1"]))

        # check if any vulnerabilities were found
        if (scan_results.issues_by_check):
            for check_result in scan_results.applied_checks:
                # get the original check info
                original_check = global_storage.checks.get(check_result.check_name)
                # if there is a correspondent check and any vulnerable files were found by check
                if (original_check and check_result.files_with_issues):
                    # add check info
                    self.data += self.add_check_name(original_check.name)
                    self.data += self.add_check_description(original_check.description)
                    self.data += self.add_check_explanation(original_check.explanation)
                    self.data += self.add_check_severity(original_check.severity)
                    self.data += self.add_issues(check_result.files_with_issues)
                    self.data += self.add_check_recommendations(original_check.recommendations)
                    self.data += self.add_check_links(original_check.links)
                    # break the page
                    self.data.append(PageBreak())
        else:
            self.data.append(Paragraph("No vulnerabilities were found",
                                       global_storage.design.styles["RegularParagraph"]))

    def add_check_name(self, name):
        result = []

        result.append(Paragraph(escape(name), global_storage.design.styles["CheckName"]))

        return result

    def add_check_description(self, description):
        result = []

        result.append(Paragraph("Description", global_storage.design.styles["H3"]))
        result.append(Paragraph(escape(description), global_storage.design.styles["RegularParagraph"]))

        return result

    def add_check_explanation(self, explanation):
        result = []

        result.append(Paragraph("Explanation", global_storage.design.styles["H3"]))

        # split explanation by "\n\n" - we get list of paragraphs
        fragments = [fragment.strip() for fragment in explanation.strip().split("\n\n") if fragment.strip()]
        for fragment in fragments:
            # if fragment starts from KF_CODE_EXAMPLE keyword - print it as a preformatted text (like <pre> tag)
            if (fragment.startswith("KF_CODE_EXAMPLE")):
                # extract code example (remove "KF_CODE_EXAMPLE" from the beginning of the fragment)
                _, code_fragment = fragment.split("KF_CODE_EXAMPLE", 1)

                # add line break for very long lines (>80)
                # for some reason XPreformatted cannot do this
                max_line_length = 80
                code_fragment_lines = []
                for line in code_fragment.splitlines():
                    # split long lines by chunks of length max_line_length
                    if (len(line) > max_line_length):
                        for start in range(0, len(line), max_line_length):
                            code_fragment_lines.append(line[start:start + max_line_length])
                    else:
                        code_fragment_lines.append(line)

                code_fragment = "\n".join(code_fragment_lines)

                result.append(XPreformatted(escape(code_fragment), global_storage.design.styles["CodeExample"]))
            # else print it as a regular paragraph
            else:
                result.append(Paragraph(escape(fragment), global_storage.design.styles["RegularParagraph"]))

        return result

    def add_check_severity(self, severity):
        result = []

        severity_to_style = {
            "High": "SeverityHigh",
            "Medium": "SeverityMedium",
            "Low": "SeverityLow",
            "Info": "SeverityInfo",
        }

        if (severity in severity_to_style):
            style = severity_to_style[severity]

            result.append(Paragraph("Severity", global_storage.design.styles["H3"]))
            result.append(Paragraph(severity, global_storage.design.styles[style]))

        return result

    def add_issues(self, files_with_issues):
        result = []

        # sort by file_path
        files_with_issues.sort(key=lambda item: item.file_path)

        for vuln_file in files_with_issues:
            # add file path
            vulnerability_header = f"File {vuln_file.file_path}"
            result.append(Paragraph(vulnerability_header, global_storage.design.styles["VulnerableCodeHeader"]))

            for issue_location in vuln_file.issues:
                # add issue location
                line_no, pos = issue_location
                issue_location = f"Line {line_no}, Position {pos}"
                result.append(Paragraph(issue_location, global_storage.design.styles["RegularParagraph"]))
                # add code listing
                result.append(self.get_code_listing(line_no, vuln_file.lines_with_issues[line_no]))

        return result

    def get_code_listing(self, line_no, line_content):
        # split long line into chunks of length max_line_length
        max_line_length = 75
        listing_lines = []
        if (len(line_content) > max_line_length):
            for start in range(0, len(line_content), max_line_length):
                listing_lines.append(line_content[start:start + max_line_length])
        else:
            listing_lines.append(line_content)

        # prepare cells of the table (listing)
        cells = []
        is_line_no_processed = False
        for line in listing_lines:
            # first line of table with the source code (listing) contains
            # line_no and first max_line_length symbols
            # of the original line_content
            if (not is_line_no_processed):
                cells.append([Paragraph(str(line_no), global_storage.design.styles["VulnerableCodeLineNo"]),
                              Preformatted(line, global_storage.design.styles["VulnerableCodeLine"])])
                is_line_no_processed = True
            # other symbols of line_content are also splitted into max_line_length chunks
            # and added without line_no, but starts with ">" symbol
            else:
                cells.append(["", Preformatted(">" + line, global_storage.design.styles["VulnerableCodeLine"])])

        # create listing (it is actually Table)
        listing = Table(cells, style=global_storage.design.VulnerableCodeTable, rowHeights=5 * mm)
        # set width of the column with line numbers according to the length of the line_no value (3mm per digit + 2mm)
        listing._argW[0] = (len(str(line_no)) * 3 + 2) * mm

        return listing

    def add_check_recommendations(self, recommendations):
        result = []

        # encode entities
        recommendations = escape(recommendations.strip())

        result.append(Paragraph("Recommendations", global_storage.design.styles["H3"]))

        individual_recommendations = [recom for recom in recommendations.split("\n") if recom]
        for recommendation in individual_recommendations:
            result.append(Paragraph(recommendation, global_storage.design.styles["Recommendation"], bulletText="-"))

        return result

    def add_check_links(self, links):
        result = []

        # encode entities
        links = escape(links.strip())

        result.append(Paragraph("Links", global_storage.design.styles["H3"]))

        individual_links = [link for link in links.split("\n") if link]
        for link in individual_links:
            result.append(Paragraph(link, global_storage.design.styles["Link"]))

        return result
