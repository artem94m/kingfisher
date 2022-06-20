from os import getcwd, path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.fonts import addMapping
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class ReportDesign():
    def __init__(self):
        self.init_fonts()
        self.init_styles()

    def init_fonts(self):
        """Registers fonts for text and code
        """
        # Roboto (for text)
        roboto_folder = path.join(getcwd(), "static", "fonts", "Roboto")
        pdfmetrics.registerFont(TTFont("Roboto", path.join(roboto_folder, "Roboto-Regular.ttf")))
        pdfmetrics.registerFont(TTFont("RobotoBd", path.join(roboto_folder, "Roboto-Bold.ttf")))
        pdfmetrics.registerFont(TTFont("RobotoIt", path.join(roboto_folder, "Roboto-Italic.ttf")))
        pdfmetrics.registerFont(TTFont("RobotoBI", path.join(roboto_folder, "Roboto-BoldItalic.ttf")))
        addMapping("Roboto", 0, 0, "Roboto")
        addMapping("Roboto", 1, 0, "RobotoBd")
        addMapping("Roboto", 0, 1, "RobotoIt")
        addMapping("Roboto", 1, 1, "RobotoBI")

        # Roboto Mono (for code)
        roboto_mono_folder = path.join(getcwd(), "static", "fonts", "RobotoMono")
        pdfmetrics.registerFont(TTFont("RobotoMono", path.join(roboto_mono_folder, "RobotoMono-Regular.ttf")))
        pdfmetrics.registerFont(TTFont("RobotoMonoBd", path.join(roboto_mono_folder, "RobotoMono-Bold.ttf")))
        pdfmetrics.registerFont(TTFont("RobotoMonoIt", path.join(roboto_mono_folder, "RobotoMono-Italic.ttf")))
        pdfmetrics.registerFont(TTFont("RobotoMonoBI", path.join(roboto_mono_folder, "RobotoMono-BoldItalic.ttf")))
        addMapping("RobotoMono", 0, 0, "RobotoMono")
        addMapping("RobotoMono", 1, 0, "RobotoMonoBd")
        addMapping("RobotoMono", 0, 1, "RobotoMonoIt")
        addMapping("RobotoMono", 1, 1, "RobotoMonoBI")

    def init_styles(self):
        """Init styles for a report file
        """
        self.page_margin = 10 * mm

        # colors
        self.logo_blue = HexColor("#107f84")
        self.logo_orange = HexColor("#f9a00e")
        self.logo_grey = HexColor("#555555")

        self.font_color = HexColor("#444444")
        self.code_color = HexColor("#000000")
        self.page_number_bg_color = HexColor("#dddddd")

        self.line_no_bg_color = HexColor("#cccccc")
        self.line_of_code_bg_color = HexColor("#eeeeee")

        self.red = "#f90e0e"
        self.orange = "#f9a00e"
        self.yellow = "#f9e30e"
        self.blue = "#0e88f9"

        self.color_high = HexColor(self.red)
        self.color_medium = HexColor(self.orange)
        self.color_low = HexColor(self.yellow)
        self.color_info = HexColor(self.blue)

        # list of styles
        self.styles = getSampleStyleSheet()

        # COMMON STYLES #############################################################
        # style for page number
        self.styles.add(ParagraphStyle(name="PageNumber", alignment=TA_CENTER, fontName="RobotoBd",
                                       fontSize=10, textColor=self.font_color, backColor=self.page_number_bg_color,
                                       borderPadding=(2 * mm, 0), leading=12))
        # style for H1
        self.styles.add(ParagraphStyle(name="H1", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=25, textColor=self.font_color, leading=30,
                                       spaceBefore=0, spaceAfter=3 * mm))
        # style for H2
        self.styles.add(ParagraphStyle(name="H2", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=18, textColor=self.font_color, leading=22,
                                       spaceBefore=3 * mm, spaceAfter=2 * mm))
        # style for H3
        self.styles.add(ParagraphStyle(name="H3", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=14, textColor=self.font_color, leading=17,
                                       spaceBefore=3 * mm, spaceAfter=1 * mm))
        # style for paragraph of text
        self.styles.add(ParagraphStyle(name="RegularParagraph", alignment=TA_JUSTIFY, fontName="Roboto",
                                       fontSize=12, textColor=self.font_color, leading=15, spaceAfter=3 * mm))

        # TITLE PAGE STYLES #########################################################
        # style for KingFisher short description Title Header
        self.styles.add(ParagraphStyle(name="TitleKingfisherShortDescription", alignment=TA_LEFT, fontName="Roboto",
                                       fontSize=31, textColor=self.logo_grey, leading=36,
                                       spaceBefore=3 * mm, spaceAfter=3 * mm))
        # style for Title Header
        self.styles.add(ParagraphStyle(name="TitleHeader", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=25, textColor=self.logo_grey, leading=30,
                                       spaceBefore=0, spaceAfter=1 * mm))
        # style for Title Text
        self.styles.add(ParagraphStyle(name="TitleText", alignment=TA_LEFT, fontName="Roboto",
                                       fontSize=16, textColor=self.logo_grey, leading=19,
                                       spaceBefore=1 * mm, spaceAfter=0))

        # TABLE OF CONTENT PAGE STYLES ##############################################
        # style for H1 on Table Of Content page
        self.styles.add(ParagraphStyle(name="TableOfContentH1", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=25, textColor=self.font_color, leading=30,
                                       spaceBefore=0, spaceAfter=3 * mm))
        # styles for table of content
        self.styles.add(ParagraphStyle(name="TOCTreeLevel0", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=16, textColor=self.font_color, leading=19))
        self.styles.add(ParagraphStyle(name="TOCTreeLevel1", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=14, textColor=self.font_color, leading=17,
                                       spaceBefore=0, spaceAfter=1 * mm))
        self.styles.add(ParagraphStyle(name="TOCTreeLevel2", alignment=TA_LEFT, fontName="Roboto",
                                       fontSize=12, textColor=self.font_color, leading=12,
                                       leftIndent=5 * mm))

        # SUMMARY PAGE STYLES #######################################################
        # style severity on summary page
        self.styles.add(ParagraphStyle(name="SummarySeverity", alignment=TA_JUSTIFY, fontName="RobotoBd",
                                       fontSize=12, textColor=self.font_color, leading=15, spaceAfter=0))
        # style skipped file on summary page
        self.styles.add(ParagraphStyle(name="SummarySkippedFile", alignment=TA_JUSTIFY, fontName="Roboto",
                                       fontSize=12, textColor=self.font_color, leading=15, spaceAfter=0))

        # ISSUES PAGE STYLES #######################################################
        # style for example of code
        self.styles.add(ParagraphStyle(name="IssuesCodeExample", alignment=TA_LEFT, fontName="RobotoMono",
                                       fontSize=10, textColor=self.code_color, leading=12,
                                       spaceAfter=5 * mm, spaceBefore=5 * mm, leftIndent=10 * mm))
        # styles for different severity levels
        self.styles.add(ParagraphStyle(name="IssuesSeverityHigh", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=12, textColor=self.color_high,
                                       leading=17, spaceAfter=3 * mm))
        self.styles.add(ParagraphStyle(name="IssuesSeverityMedium", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=12, textColor=self.color_medium,
                                       leading=17, spaceAfter=3 * mm))
        self.styles.add(ParagraphStyle(name="IssuesSeverityLow", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=12, textColor=self.color_low,
                                       leading=17, spaceAfter=3 * mm))
        self.styles.add(ParagraphStyle(name="IssuesSeverityInfo", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=12, textColor=self.color_info,
                                       leading=17, spaceAfter=3 * mm))
        # style for vulnerable file text
        self.styles.add(ParagraphStyle(name="IssuesVulnerableFile", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=12, textColor=self.font_color, leading=13,
                                       spaceBefore=3 * mm, spaceAfter=0))
        # style for vulnerable code location text
        self.styles.add(ParagraphStyle(name="IssuesVulnerableCodeLocation", alignment=TA_LEFT, fontName="Roboto",
                                       fontSize=11, textColor=self.font_color, leading=13,
                                       spaceBefore=1 * mm, spaceAfter=1 * mm))
        # style for number of line of code
        self.styles.add(ParagraphStyle(name="VulnerableCodeLineNo", alignment=TA_RIGHT, fontName="RobotoMono",
                                       fontSize=10, textColor=self.code_color, leading=12,
                                       rightIndent=1 * mm))
        # style for line of code
        self.styles.add(ParagraphStyle(name="VulnerableCodeLine", alignment=TA_LEFT, fontName="RobotoMono",
                                       fontSize=10, textColor=self.code_color, leading=12,
                                       leftIndent=0))

        # style for listing with vulnerable code
        self.vulnerable_code_listing = [  # line numbers are aligned to the right
                                        ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                                        # lines of code are aligned to the left
                                        ("ALIGN", (1, 0), (1, -1), "LEFT"),
                                        # all items of the tables are vertically aligned to the top
                                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                        # paddings for all cells are set to zero
                                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                                        # set bg color for line numbers
                                        ("BACKGROUND", (0, 0), (0, -1), self.line_no_bg_color),
                                        # set background color for lines of code
                                        ("BACKGROUND", (1, 0), (1, -1), self.line_of_code_bg_color)]

        # style for a singular recommendation
        self.styles.add(ParagraphStyle(name="IssuesRecommendation", alignment=TA_JUSTIFY, fontName="Roboto",
                                       fontSize=12, textColor=self.font_color, leading=15, leftIndent=0 * mm,
                                       bulletFontSize=16, bulletAnchor="start", bulletIndent=0, spaceAfter=2 * mm))
        # style for a singular link
        self.styles.add(ParagraphStyle(name="IssuesLink", alignment=TA_LEFT, fontName="Roboto",
                                       fontSize=12, textColor=self.font_color, leading=15, spaceAfter=1 * mm))
