from os import path

from kf_modules.report.design import ReportDesign

from reportlab.graphics import renderPM
from reportlab.graphics.shapes import Drawing, Ellipse, Rect, String
from reportlab.lib.colors import transparent
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph


class ReportTitle():
    def __init__(self, project_name, timestamp, logger):
        # get logger from the main module
        self.logger = logger

        # get design of the report
        self.design = ReportDesign()

        # save info from the main module
        self.project_name = project_name
        self.timestamp = timestamp

    def get(self):
        """ returns content of the title page """
        content = []

        logo_path = path.join("static", "images", "kingfisher_logo.png")
        if (not path.exists(logo_path)):
            self.create_logo(logo_path)

        # add logo
        content.append(Image(logo_path, width=180 * mm, height=40 * mm, hAlign="LEFT"))

        # add project name
        content.append(Paragraph("Project", self.design.styles["Header"]))
        content.append(Paragraph(self.project_name, self.design.styles["RegularParagraph"]))

        # add timestamp
        content.append(Paragraph("Date", self.design.styles["Header"]))
        content.append(Paragraph(self.timestamp, self.design.styles["RegularParagraph"]))

        return content

    def create_logo(self, logo_path):
        """ create logo image """
        # create canvas
        logo = Drawing(900, 200)
        # add orange background
        logo.add(Rect(0, 0, 200, 200, fillColor=self.design.logo_orange, strokeWidth=1,
                      strokeColor=self.design.logo_orange))
        # add blue wing
        logo.add(Ellipse(0, 290, 184, 268, fillColor=self.design.logo_blue, strokeWidth=1,
                         strokeColor=self.design.logo_blue))
        # add grey border
        logo.add(Rect(5, 5, 191, 190, strokeWidth=10, strokeColor=self.design.logo_grey, fillColor=transparent))
        # add title
        logo.add(String(220, 90, "KingFisher", fontName="RobotoBd", fontSize=120, fillColor=self.design.logo_grey))
        # add short description
        logo.add(String(223, 27, "Python 3 Simple Static Code Analyzer", fontName="Roboto", fontSize=40,
                        fillColor=self.design.logo_grey))

        try:
            renderPM.drawToFile(logo, logo_path, "PNG")
        except Exception as error:
            self.logger.error(f"Cannot render logo: {error}")
