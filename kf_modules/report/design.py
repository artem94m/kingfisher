from os import getcwd, path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_RIGHT
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
        """ register fonts for text and code """
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
        """ init styles for a report file """
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
        # add style for page number
        self.styles.add(ParagraphStyle(name="PageNumber", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=10, textColor=self.font_color, backColor=self.page_number_bg_color,
                                       borderPadding=2 * mm, leading=12))
        # add style for H1
        self.styles.add(ParagraphStyle(name="H1", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=18, textColor=self.font_color, leading=22,
                                       spaceBefore=3 * mm, spaceAfter=2 * mm))
        # add style for H2
        self.styles.add(ParagraphStyle(name="H2", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=16, textColor=self.font_color, leading=22,
                                       spaceBefore=3 * mm, spaceAfter=2 * mm))
        # add style for H3
        self.styles.add(ParagraphStyle(name="H3", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=14, textColor=self.font_color, leading=22,
                                       spaceBefore=3 * mm, spaceAfter=2 * mm))
        # add style for paragraph of text
        self.styles.add(ParagraphStyle(name="RegularParagraph", alignment=TA_JUSTIFY, fontName="Roboto",
                                       fontSize=12, textColor=self.font_color, leading=17, spaceAfter=2 * mm))
        # add style for singular line in statistics
        self.styles.add(ParagraphStyle(name="Statistics", alignment=TA_LEFT, fontName="Roboto",
                                       fontSize=12, textColor=self.font_color, leading=17))
        # add style for skipped file
        self.styles.add(ParagraphStyle(name="SkippedFile", alignment=TA_LEFT, fontName="Roboto",
                                       fontSize=12, textColor=self.font_color, leading=17))
        # add style for name of check
        self.styles.add(ParagraphStyle(name="CheckName", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=25, textColor=self.font_color, leading=30,
                                       spaceBefore=3 * mm, spaceAfter=2 * mm))
        # add style for singular recommendation
        self.styles.add(ParagraphStyle(name="Recommendation", alignment=TA_JUSTIFY, fontName="Roboto",
                                       fontSize=12, textColor=self.font_color, leading=17, leftIndent=0 * mm,
                                       bulletFontSize=16, bulletAnchor="start", bulletIndent=0, spaceAfter=1 * mm))
        # add style for singular link
        self.styles.add(ParagraphStyle(name="Link", alignment=TA_LEFT, fontName="Roboto",
                                       fontSize=12, textColor=self.font_color, leading=17))

        # add styles for different severity levels
        self.styles.add(ParagraphStyle(name="SeverityHigh", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=12, textColor=self.color_high,
                                       leading=17, spaceAfter=2 * mm))
        self.styles.add(ParagraphStyle(name="SeverityMedium", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=12, textColor=self.color_medium,
                                       leading=17, spaceAfter=2 * mm))
        self.styles.add(ParagraphStyle(name="SeverityLow", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=12, textColor=self.color_low,
                                       leading=17, spaceAfter=2 * mm))
        self.styles.add(ParagraphStyle(name="SeverityInfo", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=12, textColor=self.color_info,
                                       leading=17, spaceAfter=2 * mm))

        # add style for example of code
        self.styles.add(ParagraphStyle(name="CodeExample", alignment=TA_LEFT, fontName="RobotoMono",
                                       fontSize=10, textColor=self.code_color, leading=12,
                                       spaceAfter=5 * mm, spaceBefore=5 * mm, leftIndent=10 * mm))

        # add style for vulnerability header
        self.styles.add(ParagraphStyle(name="VulnerableCodeHeader", alignment=TA_LEFT, fontName="RobotoBd",
                                       fontSize=11, textColor=self.font_color, leading=13,
                                       spaceBefore=1 * mm, spaceAfter=0))
        # style for number of line of code
        self.styles.add(ParagraphStyle(name="VulnerableCodeLineNo", alignment=TA_RIGHT, fontName="RobotoMono",
                                       fontSize=10, textColor=self.code_color, leading=12,
                                       rightIndent=1 * mm))
        # style for line of code
        self.styles.add(ParagraphStyle(name="VulnerableCodeLine", alignment=TA_LEFT, fontName="RobotoMono",
                                       fontSize=10, textColor=self.code_color, leading=12,
                                       leftIndent=0))

        # style for code table
        self.VulnerableCodeTable = [  # line numbers are aligned to the right
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
