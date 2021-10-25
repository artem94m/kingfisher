from xml.sax.saxutils import escape

from defusedxml.ElementTree import parse

from kf_modules.report.design import ReportDesign

from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Preformatted, Table, XPreformatted


class ReportVulnerabilities():
    def __init__(self, results, logger):
        # get logger from the main module
        self.logger = logger
        # get results from the main module
        self.results = results
        # get design of the report
        self.design = ReportDesign()

    def get(self):
        """ returns content of the pages with vulnerabilities page """
        content = []

        if (self.results["vulnerabilities"]):
            # go through all checks
            for check_file in sorted(self.results["vulnerabilities"]):
                # extract data from the check
                check_info = self.extract_data_from_check(check_file)

                # add check info to the report
                content += self.add_check_name(check_info["name"])
                content += self.add_check_description(check_info["description"])
                content += self.add_check_explanation(check_info["explanation"])
                content += self.add_check_severity(check_info["severity"])

                content.append(Paragraph("Vulnerabilities", self.design.styles["Header"]))

                # go through all vulnerable files, which were found for the check
                for python_file in sorted(self.results["vulnerabilities"][check_file]):
                    # extract source code with line number from specific file
                    source_code = self.extract_source_from_file(python_file)
                    # go through all coords of vulnerability
                    for vuln_coord in sorted(list(self.results["vulnerabilities"][check_file][python_file])):
                        # add all occurrences of the vulnerability to the report
                        content += self.add_vulnerability(python_file, source_code, vuln_coord)

                content += self.add_check_recommendations(check_info["recommendations"])
                content += self.add_check_links(check_info["links"])
        else:
            content.append(Paragraph("No vulnerabilities were found", self.design.styles["Header"]))

        return content

    def add_check_name(self, name):
        """ add name of check """
        result = []
        result.append(Paragraph(escape(name), self.design.styles["CheckName"]))

        return result

    def add_check_description(self, description):
        """ add short description of the check """
        result = []
        result.append(Paragraph("Description", self.design.styles["Header"]))
        result.append(Paragraph(escape(description), self.design.styles["RegularParagraph"]))

        return result

    def add_check_explanation(self, explanation):
        """ add explanation """
        result = []
        result.append(Paragraph("Explanation", self.design.styles["Header"]))

        # split explanation by double "\n" - we get list of fragments
        fragments = [fragment.lstrip("\r\n") for fragment in explanation.split("\n\n") if fragment != ""]
        for fragment in fragments:
            # if fragment starts from KF_CODE_EXAMPLE keyword - print it as a preformatted text (like <pre> tag)
            if (fragment.startswith("KF_CODE_EXAMPLE")):
                fragment = fragment.replace("KF_CODE_EXAMPLE", "", 1)

                # add line break for very long lines
                # for some reason XPreformatted cannot do this
                # get lines from the fragment
                lines = fragment.split("\n")
                for number, line in enumerate(lines):
                    # transform line of code into the list of symbols
                    symbols = list(line)
                    # set size for chunks of line
                    chunk_size = 80
                    # add "\n" before every end-of-the-chunk symbol
                    for end_of_chunk in range(0, len(line), chunk_size):
                        if (end_of_chunk != 0):
                            symbols[end_of_chunk] = "\n" + symbols[end_of_chunk]
                    # join symbols back to the line - now there are "\n" before every eightieth symbol
                    lines[number] = "".join(symbols)
                # restore fragment variable
                fragment = "\n".join(lines)

                result.append(XPreformatted(escape(fragment), self.design.styles["CodeExample"]))
            # else print it as a regular paragraph
            else:
                result.append(Paragraph(escape(fragment), self.design.styles["RegularParagraph"]))

        return result

    def add_check_severity(self, severity):
        """ add severity """
        result = []
        result.append(Paragraph("Severity", self.design.styles["Header"]))

        # set style for severity
        style = "SeverityInfo"

        if (severity == "High"):
            style = "SeverityHigh"
        elif (severity == "Medium"):
            style = "SeverityMedium"
        elif (severity == "Low"):
            style = "SeverityLow"
        elif (severity == "Info"):
            style = "SeverityInfo"

        result.append(Paragraph(severity, self.design.styles[style]))

        return result

    def add_vulnerability(self, python_file, source_code, vuln_coord):
        """ add code of the vulnerability """
        result = []
        # get coords of the vulnerability (line number and position)
        line_number, pos = vuln_coord

        # add vulnerability header
        vulnerability_header = f"File {python_file}, Line {line_number}, Pos {pos}"
        result.append(Paragraph(vulnerability_header, self.design.styles["VulnerableCodeHeader"]))

        # transform line of code into the list of symbols
        symbols = list(source_code[line_number])
        # set size for chunks of line
        chunk_size = 75
        # add "\n" before every end-of-the-chunk symbol
        for end_of_chunk in range(0, len(source_code[line_number]), chunk_size):
            symbols[end_of_chunk] = "\n" + symbols[end_of_chunk]
        # join symbols back to the line - now there are "\n" before every eightieth symbol
        line_new = "".join(symbols)
        # and now we get chunks (80 symbols long, except, sometimes, last one) from the line
        chunks = [chunk for chunk in line_new.split("\n") if chunk != ""]

        # first line of table with the source code contains line number and first eighty symbols
        line_no = Paragraph(str(line_number), self.design.styles["VulnerableCodeLineNo"])
        line_content = Preformatted(chunks.pop(0), self.design.styles["VulnerableCodeLine"])
        data = [[line_no, line_content]]

        # if the line is longer than 80 symbols - add other chunks without line number but with ">" symbol
        for chunk in chunks:
            data.append(["", Preformatted(">" + chunk, self.design.styles["VulnerableCodeLine"])])

        # create Table element
        table = Table(data, style=self.design.VulnerableCodeTable, rowHeights=5 * mm)
        # set the column of line numbers width to match the length of the line number value
        size_of_line_no_column = (len(str(line_number)) * 3 + 2) * mm
        # set first column width
        table._argW[0] = size_of_line_no_column

        result.append(table)

        return result

    def add_check_recommendations(self, recommendations):
        """ add recommendations to the report """
        result = []
        # encode entities
        recommendations = escape(recommendations)

        result.append(Paragraph("Recommendations", self.design.styles["Header"]))
        # split all the recommendations by "\n"
        fragments = [recomm for recomm in recommendations.split("\n") if recomm not in ["", "\n"]]
        for fragment in fragments:
            # add every recommendation with - mark
            result.append(Paragraph(fragment, self.design.styles["Recommendation"], bulletText="-"))

        return result

    def add_check_links(self, links):
        """ add links to the report """
        result = []
        result.append(Paragraph("Links", self.design.styles["Header"]))
        # split all the links by "\n"
        fragments = [link for link in links.split("\n") if link not in ["", "\n"]]
        for fragment in fragments:
            result.append(Paragraph(fragment, self.design.styles["Link"]))

        return result

    # SUPPORT FUNCTIONS #############################################################
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

    def extract_source_from_file(self, filepath):
        """ get source code with line numbers """
        plain = ""
        source_code = []

        # get plain text of the file
        try:
            with open(filepath, encoding="utf-8") as f:
                plain = f.read()
        except Exception as error:
            self.logger.warning(f"Cannot read file {filepath}. Error: {error}")

        # file is not empty
        if (plain != ""):
            # fill the zero position - code in a file starts from first line
            source_code.append(None)
            # extend current list with lines of code
            source_code.extend([line.strip("\r") for line in plain.split("\n")])

        return source_code if len(source_code) != 0 else None
