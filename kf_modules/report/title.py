from os import getcwd, path

import global_storage

from reportlab.graphics import renderPM
from reportlab.graphics.shapes import Drawing, Ellipse, Rect, String
from reportlab.lib.colors import transparent
from reportlab.lib.units import mm
from reportlab.platypus import Image, PageBreak, Paragraph, Spacer


class ReportTitle():
    """Creates content for the title page
    """
    def __init__(self, scan_results):
        self.data = []

        logo_path = path.join(getcwd(), "static", "images", "kingfisher_logo.png")
        if (not path.exists(logo_path)):
            self.create_logo(logo_path)

        if (path.exists(logo_path)):
            # add logo
            self.data.append(Image(logo_path, width=180 * mm, height=40 * mm, hAlign="LEFT"))

        # add short description
        self.data.append(Paragraph("Python 3 Simple Static Code Analyzer",
                                   global_storage.design.styles["TitleKingfisherShortDescription"]))
        # add free space
        self.data.append(Spacer(1, 10 * mm))

        # add project name
        self.data.append(Paragraph("Project", global_storage.design.styles["TitleHeader"]))
        self.data.append(Paragraph(scan_results.project, global_storage.design.styles["TitleText"]))

        # add free space
        self.data.append(Spacer(1, 10 * mm))

        # add timestamp
        self.data.append(Paragraph("Date", global_storage.design.styles["TitleHeader"]))
        self.data.append(Paragraph(scan_results.start_scan_timestamp.strftime("%H:%M:%S %d.%m.%Y"),
                                   global_storage.design.styles["TitleText"]))

        # break the page
        self.data.append(PageBreak())

    def create_logo(self, logo_path):
        """Creates logo image (PNG)
        """
        # create canvas
        logo_obj = Drawing(900, 200)
        # add orange area
        logo_obj.add(Rect(0, 0, 200, 200, fillColor=global_storage.design.logo_orange, strokeWidth=1,
                          strokeColor=global_storage.design.logo_orange))
        # add blue area
        logo_obj.add(Ellipse(0, 290, 184, 268, fillColor=global_storage.design.logo_blue, strokeWidth=1,
                             strokeColor=global_storage.design.logo_blue))
        # add grey border
        logo_obj.add(Rect(4, 4, 192, 192, strokeWidth=10, strokeColor=global_storage.design.logo_grey,
                          fillColor=transparent))
        # add title
        logo_obj.add(String(245, 52, "KingFisher", fontName="RobotoBd", fontSize=135,
                            fillColor=global_storage.design.logo_grey))

        try:
            renderPM.drawToFile(logo_obj, logo_path, "PNG")
        except Exception as error:
            global_storage.logger.error(f"Cannot render logo: {error}")
