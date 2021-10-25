from datetime import datetime
from os import path

from kf_modules.report.design import ReportDesign
from kf_modules.report.summary import ReportSummary
from kf_modules.report.title import ReportTitle
from kf_modules.report.vulnerabilities import ReportVulnerabilities

from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph


class KfReport():
    def __init__(self, logger, args, results):
        # get logger from main module
        self.logger = logger

        # get design of the report
        self.design = ReportDesign()

        # create report path
        timestamp = datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
        report_name = f"{args.project_name}_{timestamp}.pdf"
        report_path = path.join(args.report_path, report_name)
        report = self.init_report(report_path)

        # get modules for different parts of the report
        title = ReportTitle(args.project_name, timestamp, logger)
        summary = ReportSummary(results, logger)
        vulnerabilities = ReportVulnerabilities(results, logger)

        # content of report
        content = []
        content += title.get()
        content += summary.get()
        content += vulnerabilities.get()

        self.logger.info("Creating report...")
        report.build(content)

    def init_report(self, report_path):
        """ init report document """
        def footer_template(canvas, doc):
            """ add page number to the footer """
            canvas.saveState()
            # get page number
            page_number_text = "Page {}".format(canvas.getPageNumber())
            # create Paragraph element
            page_number = Paragraph(page_number_text, self.design.styles["PageNumber"])
            # create Paragraph block
            page_number.wrap(20 * mm, 10 * mm)
            # draw Paragraph on the page
            page_number.drawOn(canvas, 190 * mm, 5 * mm)
            canvas.restoreState()

        # init report file
        report = BaseDocTemplate(report_path, pagesize=portrait(A4), rightMargin=self.design.page_margin,
                                 leftMargin=self.design.page_margin, topMargin=self.design.page_margin,
                                 bottomMargin=self.design.page_margin, author="Kingfisher",
                                 title="Kingfisher")
        # create footer template
        frame_footer = Frame(report.leftMargin, report.bottomMargin, report.width, report.height, id="normal")
        template = PageTemplate(id="footer", frames=frame_footer, onPageEnd=footer_template)
        # add footer template to the report file
        report.addPageTemplates([template])

        return report
