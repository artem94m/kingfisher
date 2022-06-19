import global_storage

from reportlab.platypus import PageBreak, Paragraph
from reportlab.platypus.tableofcontents import TableOfContents


class ReportTableOfContent():
    """Creates content for the table of content page
    """
    def __init__(self):
        self.data = []

        # add page title
        self.data.append(Paragraph("Table of content", global_storage.design.styles["TableOfContentH1"]))

        # add table of contents with styles
        toc = TableOfContents()
        toc.levelStyles = [global_storage.design.styles["TOCTreeLevel0"],
                           global_storage.design.styles["TOCTreeLevel1"],
                           global_storage.design.styles["TOCTreeLevel2"]]
        self.data.append(toc)

        # break the page
        self.data.append(PageBreak())
