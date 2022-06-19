from os import path

import global_storage

from kf_modules.report.design import ReportDesign
from kf_modules.report.summary import ReportSummary
from kf_modules.report.title import ReportTitle
from kf_modules.report.toc_tree import ReportTableOfContent
from kf_modules.report.vulnerabilities import ReportVulnerabilities

from reportlab.graphics.shapes import Drawing, Polygon
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph


class KingFisherDocTemplate(BaseDocTemplate):
    def afterFlowable(self, flowable):
        """Detect Level 1 and 2 headings for creation of Table Of Content with anchors
        """
        if isinstance(flowable, Paragraph):
            text = flowable.getPlainText()
            style = flowable.style.name
            if (style == "H1"):
                key = "h1-%s" % self.seq.nextf("heading1")
                self.canv.bookmarkPage(key)
                self.notify("TOCEntry", (1, text, self.page, key))
            if (style == "H2"):
                key = "h2-%s" % self.seq.nextf("heading2")
                self.canv.bookmarkPage(key)
                self.notify("TOCEntry", (2, text, self.page, key))


class ReportGenerator():
    """Class to generate the report
    """
    def __init__(self, reports_path, scan_results):
        # get design of the report
        global_storage.design = ReportDesign()

        global_storage.logger.info("Creating report...")

        # create report path
        timestamp = scan_results.start_scan_timestamp.strftime("%Y-%m-%d_%H-%M-%S")
        report_name = f"{scan_results.project}_{timestamp}.pdf"
        report_path = path.join(reports_path, report_name)
        report = self.init_report(report_path)

        # get modules for different parts of the report
        content = []
        content += ReportTitle(scan_results).data
        content += ReportTableOfContent().data
        content += ReportSummary(scan_results).data
        content += ReportVulnerabilities(scan_results).data

        report.multiBuild(content)

        global_storage.logger.info(f"Report saved at {report_path}")

    def init_report(self, report_path):
        """Init report document
        """
        def footer_template(canvas, doc):
            """Add page number to the footer starting from the second page
            """
            canvas.saveState()

            # add some design at the bottom of the title page
            if (canvas.getPageNumber() == 1):
                title_page_decor = Drawing(600, 900)
                title_page_decor.add(Polygon(points=[0, 0, 0, 150, 600, 400, 600, 0],
                                             strokeWidth=1,
                                             strokeColor=global_storage.design.logo_blue,
                                             fillColor=global_storage.design.logo_blue))
                title_page_decor.add(Polygon(points=[0, 0, 0, 200, 600, 0],
                                             strokeWidth=1,
                                             strokeColor=global_storage.design.logo_orange,
                                             fillColor=global_storage.design.logo_orange))
                title_page_decor.wrap(210 * mm, 210 * mm)
                title_page_decor.drawOn(canvas, 0, 0)
            # add page number on the other pages
            else:
                page_number_text = f"Page {canvas.getPageNumber()}"
                page_number = Paragraph(page_number_text, global_storage.design.styles["PageNumber"])
                # 2mm for every symbol in page_number_text + 3mm for the left and right paddings
                page_number_width = len(page_number_text) * 2 + 3
                page_number.wrap(page_number_width * mm, 10 * mm)
                # draw page_number on A4 page (starting from left bottom corner)
                page_number.drawOn(canvas, (210 - page_number_width) * mm, 5 * mm)

            canvas.restoreState()

        # init report file
        report = KingFisherDocTemplate(report_path, pagesize=portrait(A4),
                                       rightMargin=global_storage.design.page_margin,
                                       leftMargin=global_storage.design.page_margin,
                                       topMargin=global_storage.design.page_margin,
                                       bottomMargin=global_storage.design.page_margin,
                                       author="Kingfisher", title="Kingfisher")
        # add footer template (page number)
        frame_footer = Frame(report.leftMargin, report.bottomMargin, report.width, report.height, id="normal")
        template = PageTemplate(id="footer", frames=frame_footer, onPageEnd=footer_template)
        report.addPageTemplates([template])

        return report
