from os import path

import global_storage

from kf_modules.report.design import ReportDesign
from kf_modules.report.summary import ReportSummary
from kf_modules.report.title import ReportTitle
from kf_modules.report.vulnerabilities import ReportVulnerabilities

from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph


class ReportGenerator():
    """Class to generate the report
    """
    def __init__(self, reports_path, scan_results):
        # get design of the report
        global_storage.design = ReportDesign()

        # create report path
        timestamp = scan_results.start_scan_timestamp.strftime("%Y-%m-%d_%H-%M-%S")
        report_name = f"{scan_results.project}_{timestamp}.pdf"
        report_path = path.join(reports_path, report_name)
        report = self.init_report(report_path)

        # get modules for different parts of the report
        content = []
        content += ReportTitle(scan_results).data
        content += ReportSummary(scan_results).data
        content += ReportVulnerabilities(scan_results).data

        global_storage.logger.info("Creating report...")
        report.build(content)

    def init_report(self, report_path):
        """Init report document
        """
        def footer_template(canvas, doc):
            """ add page number to the footer """
            canvas.saveState()
            # get page number
            page_number_text = "Page {}".format(canvas.getPageNumber())
            # create Paragraph element
            page_number = Paragraph(page_number_text, global_storage.design.styles["PageNumber"])
            # create Paragraph block
            page_number.wrap(20 * mm, 10 * mm)
            # draw Paragraph on the page
            page_number.drawOn(canvas, 190 * mm, 5 * mm)
            canvas.restoreState()

        # init report file
        report = BaseDocTemplate(report_path, pagesize=portrait(A4),
                                 rightMargin=global_storage.design.page_margin,
                                 leftMargin=global_storage.design.page_margin,
                                 topMargin=global_storage.design.page_margin,
                                 bottomMargin=global_storage.design.page_margin,
                                 author="Kingfisher", title="Kingfisher")
        # create footer template
        frame_footer = Frame(report.leftMargin, report.bottomMargin, report.width, report.height, id="normal")
        template = PageTemplate(id="footer", frames=frame_footer, onPageEnd=footer_template)
        # add footer template to the report file
        report.addPageTemplates([template])

        return report
