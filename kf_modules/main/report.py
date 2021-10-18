from reportlab.lib.pagesizes import portrait, A4
from reportlab.lib.colors import HexColor, transparent
from reportlab.lib.fonts import addMapping
from reportlab.graphics.shapes import Drawing, Rect, Ellipse, String
from reportlab.graphics import renderPM
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, XPreformatted, Preformatted, Table, Paragraph, Image, Frame, PageTemplate
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import defusedxml.ElementTree as etree
from datetime import datetime
from xml.sax.saxutils import escape
import os


class KfReport():
    def __init__(self, logger, args, results):
        # get logger from main module
        self.logger = logger

        # create report path
        report_name = "{}_{}.pdf".format(args.project_name, datetime.today().strftime("%Y-%m-%d_%H-%M-%S"))
        report_path = os.path.join(args.report_path, report_name)

        # register fonts
        self.init_fonts()
        # init styles
        self.init_styles()

        # create logo image if it does not exist
        logo_path = os.path.join("static", "images", "kingfisher_logo.png")
        if (not os.path.exists(logo_path)):
            self.create_logo(logo_path)

        # init report file
        report = self.init_report(report_path)

        # init content of report
        content = []
        self.add_logo(content, logo_path)
        self.add_project_name(content, args.project_name)
        self.add_timestamp(content, datetime.today().strftime("%H:%M:%S %d-%m-%Y"))

        # if files were skipped
        if (results["skipped"]):
            self.add_skipped(content, results["skipped"])

        vulnerabilities = []
        severities = {
            "High": 0,
            "Medium": 0,
            "Low": 0,
            "Info": 0
        }
        statistics = {}

        # if there are results
        if (results["vulnerabilities"]):
            # go through all checks
            for check_file in sorted(results["vulnerabilities"].keys()):
                # extract data from the check
                check_info = self.extract_data_from_check(check_file)

                # add check info to the report
                self.add_check_name(vulnerabilities, check_info["name"])
                self.add_check_description(vulnerabilities, check_info["description"])
                self.add_check_explanation(vulnerabilities, check_info["explanation"])
                self.add_check_severity(vulnerabilities, check_info["severity"])

                statistics.setdefault(check_info["name"], 0)

                # go through all vulnerable files, which were found for the check
                for python_file in sorted(results["vulnerabilities"][check_file].keys()):
                    # extract source code with line number from specific file
                    source_code = self.extract_source_from_file(python_file)
                    # go through all coords of vulnerability
                    for vuln_coord in sorted(list(results["vulnerabilities"][check_file][python_file])):
                        # add all occurrences of the vulnerability to the report
                        self.add_vulnerability(vulnerabilities, python_file, source_code, vuln_coord)
                        # collect the statistics
                        severities[check_info["severity"]] += 1
                        statistics[check_info["name"]] += 1

                # add recommendations
                self.add_check_recommendations(vulnerabilities, check_info["recommendations"])
                # add links to the check
                self.add_check_links(vulnerabilities, check_info["links"])

            # add stats about found vulnerabilities
            self.add_statistics(content, severities, statistics)
            # add vulnerabilities to content
            content.extend(vulnerabilities)
        else:
            self.add_no_results(content)

        self.logger.info("Found High: {}, Medium: {}, Low: {}, Info: {}".format(severities["High"], severities["Medium"], severities["Low"], severities["Info"]))
        self.logger.info("Creating report...")
        # add content to the report
        report.build(content)

    def extract_source_from_file(self, file):
        """ get source code with line numbers """
        plain = ""
        source_code = []

        # get plain text of the file
        try:
            with open(file, encoding="utf-8") as f:
                plain = f.read()
        except Exception as error:
            self.logger.warning("Cannot read file {}. Error: {}".format(file, str(error)))

        # file is not empty
        if (plain != ""):
            # fill the zero position - code in a file starts from first line
            source_code.append(None)
            # extend current list with lines of code
            source_code.extend([line.strip("\r") for line in plain.split("\n")])

        return source_code if len(source_code) != 0 else None

    def extract_data_from_check(self, check):
        """ parse check for functions to call """
        data = {}

        try:
            # try to parse xml safely
            xml_file = etree.parse(check, forbid_dtd=True, forbid_entities=True, forbid_external=True)
        except Exception as error:
            self.logger.error("Cannot parse check: {}".format(str(error)))
        else:
            # get <check> tag
            root = xml_file.getroot()

            for element in list(root):
                # extract all the necessary data
                if (element.tag in ["name", "description", "explanation", "severity", "recommendations", "links"]):
                    data[element.tag] = element.text.strip()

        return data

    def init_fonts(self):
        """ register fonts for text and code """
        # Roboto (for text)
        roboto_folder = os.path.join("static", "fonts", "Roboto")
        pdfmetrics.registerFont(TTFont("Roboto", os.path.join(roboto_folder, "Roboto-Regular.ttf")))
        pdfmetrics.registerFont(TTFont("RobotoBd", os.path.join(roboto_folder, "Roboto-Bold.ttf")))
        pdfmetrics.registerFont(TTFont("RobotoIt", os.path.join(roboto_folder, "Roboto-Italic.ttf")))
        pdfmetrics.registerFont(TTFont("RobotoBI", os.path.join(roboto_folder, "Roboto-BoldItalic.ttf")))
        addMapping("Roboto", 0, 0, "Roboto")
        addMapping("Roboto", 1, 0, "RobotoBd")
        addMapping("Roboto", 0, 1, "RobotoIt")
        addMapping("Roboto", 1, 1, "RobotoBI")
        # Roboto Mono (for code)
        roboto_mono_folder = os.path.join("static", "fonts", "RobotoMono")
        pdfmetrics.registerFont(TTFont("RobotoMono", os.path.join(roboto_mono_folder, "RobotoMono-Regular.ttf")))
        pdfmetrics.registerFont(TTFont("RobotoMonoBd", os.path.join(roboto_mono_folder, "RobotoMono-Bold.ttf")))
        pdfmetrics.registerFont(TTFont("RobotoMonoIt", os.path.join(roboto_mono_folder, "RobotoMono-Italic.ttf")))
        pdfmetrics.registerFont(TTFont("RobotoMonoBI", os.path.join(roboto_mono_folder, "RobotoMono-BoldItalic.ttf")))
        addMapping("RobotoMono", 0, 0, "RobotoMono")
        addMapping("RobotoMono", 1, 0, "RobotoMonoBd")
        addMapping("RobotoMono", 0, 1, "RobotoMonoIt")
        addMapping("RobotoMono", 1, 1, "RobotoMonoBI")

    def init_styles(self):
        """ init styles for a report file """
        # page margin
        self.page_margin = 10 * mm

        # logo blue
        self.logo_blue = HexColor("#107f84")
        # logo orange
        self.logo_orange = HexColor("#f9a00e")
        # logo grey
        self.logo_grey = HexColor("#555555")

        # font color - dark grey
        self.font_color = HexColor("#444444")
        # code color - black
        self.code_color = HexColor("#000000")
        # bg of page number - light grey
        self.page_number_bg_color = HexColor("#dddddd")

        # line number bg color - light grey
        self.line_no_bg_color = HexColor("#cccccc")
        # line of code bg color - very light grey
        self.line_of_code_bg_color = HexColor("#eeeeee")

        # severity high - red
        self.color_high = HexColor("#f90e0e")
        # severity medium - orange
        self.color_medium = HexColor("#f9a00e")
        # severity low - yellow
        self.color_low = HexColor("#f9e30e")
        # severity info - blue
        self.color_info = HexColor("#0e88f9")

        # list of styles
        self.styles = getSampleStyleSheet()
        # add style for page number
        self.styles.add(ParagraphStyle(name="PageNumber", alignment=TA_LEFT, fontName="RobotoBd", fontSize=10, textColor=self.font_color, backColor=self.page_number_bg_color, borderPadding=2 * mm, leading=12))
        # add style for header
        self.styles.add(ParagraphStyle(name="Header", alignment=TA_LEFT, fontName="RobotoBd", fontSize=18, textColor=self.font_color, leading=22, spaceBefore=3 * mm, spaceAfter=2 * mm))
        # add style for paragraph of text
        self.styles.add(ParagraphStyle(name="RegularParagraph", alignment=TA_JUSTIFY, fontName="Roboto", fontSize=12, textColor=self.font_color, leading=17, spaceAfter=2 * mm))
        # add style for singular line in statistics
        self.styles.add(ParagraphStyle(name="Statistics", alignment=TA_LEFT, fontName="Roboto", fontSize=12, textColor=self.font_color, leading=17))
        # add style for skipped file
        self.styles.add(ParagraphStyle(name="SkippedFile", alignment=TA_LEFT, fontName="Roboto", fontSize=12, textColor=self.font_color, leading=17))
        # add style for name of check
        self.styles.add(ParagraphStyle(name="CheckName", alignment=TA_LEFT, fontName="RobotoBd", fontSize=25, textColor=self.font_color, leading=30, spaceBefore=3 * mm, spaceAfter=2 * mm))
        # add style for singular recommendation
        self.styles.add(ParagraphStyle(name="Recommendation", alignment=TA_JUSTIFY, fontName="Roboto", fontSize=12, textColor=self.font_color, leading=17, leftIndent=0 * mm, bulletFontSize=16, bulletAnchor="start", bulletIndent=0, spaceAfter=1 * mm))
        # add style for singular link
        self.styles.add(ParagraphStyle(name="Link", alignment=TA_LEFT, fontName="Roboto", fontSize=12, textColor=self.font_color, leading=17))

        # add styles for different severity levels
        self.styles.add(ParagraphStyle(name="SeverityHigh", alignment=TA_LEFT, fontName="RobotoBd", fontSize=12, textColor=self.color_high, leading=17, spaceAfter=2 * mm))
        self.styles.add(ParagraphStyle(name="SeverityMedium", alignment=TA_LEFT, fontName="RobotoBd", fontSize=12, textColor=self.color_medium, leading=17, spaceAfter=2 * mm))
        self.styles.add(ParagraphStyle(name="SeverityLow", alignment=TA_LEFT, fontName="RobotoBd", fontSize=12, textColor=self.color_low, leading=17, spaceAfter=2 * mm))
        self.styles.add(ParagraphStyle(name="SeverityInfo", alignment=TA_LEFT, fontName="RobotoBd", fontSize=12, textColor=self.color_info, leading=17, spaceAfter=2 * mm))

        # add style for example of code
        self.styles.add(ParagraphStyle(name="CodeExample", alignment=TA_LEFT, fontName="RobotoMono", fontSize=10, textColor=self.code_color, leading=12, spaceAfter=5 * mm, spaceBefore=5 * mm, leftIndent=10 * mm))

        # add style for vulnerability header
        self.styles.add(ParagraphStyle(name="VulnerableCodeHeader", alignment=TA_LEFT, fontName="RobotoBd", fontSize=11, textColor=self.font_color, leading=13, spaceBefore=1 * mm, spaceAfter=0))
        # style for number of line of code
        self.styles.add(ParagraphStyle(name="VulnerableCodeLineNo", alignment=TA_RIGHT, fontName="RobotoMono", fontSize=10, textColor=self.code_color, leading=12, rightIndent=1 * mm))
        # style for line of code
        self.styles.add(ParagraphStyle(name="VulnerableCodeLine", alignment=TA_LEFT, fontName="RobotoMono", fontSize=10, textColor=self.code_color, leading=12, leftIndent=0))

    def create_logo(self, logo_path):
        """ create logo png """

        # create canvas
        logo = Drawing(900, 200)
        # add orange background
        logo.add(Rect(0, 0, 200, 200, fillColor=self.logo_orange, strokeWidth=1, strokeColor=self.logo_orange))
        # add blue wing
        logo.add(Ellipse(0, 290, 184, 268, fillColor=self.logo_blue, strokeWidth=1, strokeColor=self.logo_blue))
        # add grey border
        logo.add(Rect(5, 5, 191, 190, strokeWidth=10, strokeColor=self.logo_grey, fillColor=transparent))
        # add title
        logo.add(String(220, 90, "KingFisher", fontName="RobotoBd", fontSize=120, fillColor=self.logo_grey))
        # add short description
        logo.add(String(223, 27, "Python 3 Simple Static Code Analyzer", fontName="Roboto", fontSize=40, fillColor=self.logo_grey))
        # save logo to the path

        try:
            renderPM.drawToFile(logo, logo_path, "PNG")
        except Exception as error:
            self.logger.error("Cannot render logo: {}".format(str(error)))

    def init_report(self, report_path):
        """ init report document """
        def footer_template(canvas, doc):
            """ add page number to the footer """
            canvas.saveState()
            # get page number
            page_number_text = "Page {}".format(canvas.getPageNumber())
            # create Paragraph element
            page_number = Paragraph(page_number_text, self.styles["PageNumber"])
            # create Paragraph block
            page_number.wrap(20 * mm, 10 * mm)
            # draw Paragraph on the page
            page_number.drawOn(canvas, 190 * mm, 5 * mm)
            canvas.restoreState()

        # init report file
        report = BaseDocTemplate(report_path, pagesize=portrait(A4), rightMargin=self.page_margin, leftMargin=self.page_margin, topMargin=self.page_margin, bottomMargin=self.page_margin, author="Kingfisher", title="Kingfisher")
        # create footer template
        frame_footer = Frame(report.leftMargin, report.bottomMargin, report.width, report.height, id="normal")
        template = PageTemplate(id="footer", frames=frame_footer, onPageEnd=footer_template)
        # add footer template to the report file
        report.addPageTemplates([template])

        return report

    def add_logo(self, content, logo_path):
        """ add logo to the content of the report """
        logo = Image(logo_path, width=180 * mm, height=40 * mm, hAlign="LEFT")
        content.append(logo)

    def add_project_name(self, content, project_name):
        """ add project name """
        content.append(Paragraph("Project", self.styles["Header"]))
        content.append(Paragraph(project_name, self.styles["RegularParagraph"]))

    def add_timestamp(self, content, timestamp):
        """ add timestamp """
        content.append(Paragraph("Date", self.styles["Header"]))
        content.append(Paragraph(timestamp, self.styles["RegularParagraph"]))

    def add_statistics(self, content, severities, statistics):
        """ add statistics """
        content.append(Paragraph("Found", self.styles["Header"]))
        content.append(Paragraph("<font color='#f90e0e'><strong>High:</strong></font> {}".format(severities["High"]), self.styles["RegularParagraph"]))
        content.append(Paragraph("<font color='#f9a00e'><strong>Medium:</strong></font> {}".format(severities["Medium"]), self.styles["RegularParagraph"]))
        content.append(Paragraph("<font color='#f9e30e'><strong>Low:</strong></font> {}".format(severities["Low"]), self.styles["RegularParagraph"]))
        content.append(Paragraph("<font color='#0e88f9'><strong>Info:</strong></font> {}".format(severities["Info"]), self.styles["RegularParagraph"]))
        content.append(Paragraph("Vulnerabilities", self.styles["Header"]))
        for check_name in statistics:
            content.append(Paragraph("{}: <strong>{}</strong>".format(check_name, statistics[check_name]), self.styles["Statistics"]))

    def add_skipped(self, content, skipped):
        """ add skipped files """
        content.append(Paragraph("Skipped files ({})".format(len(skipped)), self.styles["Header"]))
        for file in skipped:
            content.append(Paragraph(file, self.styles["SkippedFile"]))

    def add_no_results(self, content):
        """ add no results text """
        content.append(Paragraph("No vulnerabilities found", self.styles["Header"]))

    def add_check_name(self, content, name):
        """ add name of check """
        # encode entities
        name = escape(name)

        content.append(Paragraph(name, self.styles["CheckName"]))

    def add_check_description(self, content, description):
        """ add short description of the check """
        # encode entities
        description = escape(description)

        content.append(Paragraph("Description", self.styles["Header"]))
        content.append(Paragraph(description, self.styles["RegularParagraph"]))

    def add_check_explanation(self, content, explanation):
        """ add explanation """
        content.append(Paragraph("Explanation", self.styles["Header"]))

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

                content.append(XPreformatted(escape(fragment), self.styles["CodeExample"]))
            # else print it as a regular paragraph
            else:
                content.append(Paragraph(escape(fragment), self.styles["RegularParagraph"]))

    def add_check_severity(self, content, severity):
        """ add severity """
        content.append(Paragraph("Severity", self.styles["Header"]))

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

        content.append(Paragraph(severity, self.styles[style]))
        content.append(Paragraph("Vulnerabilities", self.styles["Header"]))

    def add_vulnerability(self, content, python_file, source_code, vuln_coord):
        """ add code of the vulnerability """
        # get coords of the vulnerability (line number and position)
        line_number, pos = vuln_coord

        # add vulnerability header
        vulnerability_header = "File {}, Line {}, Pos {}".format(python_file, line_number, pos)
        content.append(Paragraph(vulnerability_header, self.styles["VulnerableCodeHeader"]))

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
        line_no = Paragraph(str(line_number), self.styles["VulnerableCodeLineNo"])
        line_content = Preformatted(chunks.pop(0), self.styles["VulnerableCodeLine"])
        data = [[line_no, line_content]]

        # if the line is longer than 80 symbols - add other chunks without line number but with ">" symbol
        for chunk in chunks:
            data.append(["", Preformatted(">" + chunk, self.styles["VulnerableCodeLine"])])

        # style for code table
        VulnerableCodeTable = [("ALIGN", (0, 0), (0, -1), "RIGHT"),  # line numbers are aligned to the right
                               ("ALIGN", (1, 0), (1, -1), "LEFT"),  # lines of code are aligned to the left
                               ("VALIGN", (0, 0), (-1, -1), "TOP"),  # all items of the tables are vertically aligned to the top
                               ("LEFTPADDING", (0, 0), (-1, -1), 0),  # paddings for all cells are set to zero
                               ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                               ("TOPPADDING", (0, 0), (-1, -1), 0),
                               ("BACKGROUND", (0, 0), (0, -1), self.line_no_bg_color),  # set bg color for line numbers
                               # set background color for lines of code
                               ("BACKGROUND", (1, 0), (1, -1), self.line_of_code_bg_color)]

        # create Table element
        table = Table(data, style=VulnerableCodeTable, rowHeights=5 * mm)
        # set the column of line numbers width to match the length of the line number value
        size_of_line_no_column = (len(str(line_number)) * 3 + 2) * mm
        # set first column width
        table._argW[0] = size_of_line_no_column

        content.append(table)

    def add_check_recommendations(self, content, recommendations):
        """ add recommendations to the report """
        # encode entities
        recommendations = escape(recommendations)

        content.append(Paragraph("Recommendations", self.styles["Header"]))
        # split all the recommendations by "\n"
        fragments = [recommendation for recommendation in recommendations.split("\n") if recommendation not in ["", "\n"]]
        for fragment in fragments:
            # add every recommendation with ● mark
            content.append(Paragraph(fragment, self.styles["Recommendation"], bulletText=u"\u25cf"))

    def add_check_links(self, content, links):
        """ add links to the report """
        content.append(Paragraph("Links", self.styles["Header"]))
        # split all the links by "\n"
        fragments = [link for link in links.split("\n") if link not in ["", "\n"]]
        for fragment in fragments:
            content.append(Paragraph(fragment, self.styles["Link"]))
