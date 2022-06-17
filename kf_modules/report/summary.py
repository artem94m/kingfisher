import global_storage

from reportlab.platypus import PageBreak, Paragraph


class ReportSummary():
    """Creates content for the summary page
    """
    def __init__(self, scan_results):
        self.data = []

        # add page title
        self.data.append(Paragraph("Summary", global_storage.design.styles["H1"]))

        # add project name
        self.data.append(Paragraph("Project name", global_storage.design.styles["H2"]))
        self.data.append(Paragraph(scan_results.project, global_storage.design.styles["RegularParagraph"]))

        # add file path to the project
        self.data.append(Paragraph("Project path", global_storage.design.styles["H2"]))
        self.data.append(Paragraph(scan_results.scan_path, global_storage.design.styles["RegularParagraph"]))

        # add scan duration
        self.data.append(Paragraph("Scan duration", global_storage.design.styles["H2"]))
        self.data.append(Paragraph(scan_results.duration, global_storage.design.styles["RegularParagraph"]))

        # number of applied checks
        self.data.append(Paragraph("Number of applied checks", global_storage.design.styles["H2"]))
        self.data.append(Paragraph(f"{len(scan_results.applied_checks)}",
                                   global_storage.design.styles["RegularParagraph"]))
        # add statistics by severity
        self.data.append(Paragraph("Vulnerabilities by severity", global_storage.design.styles["H2"]))
        self.data.append(Paragraph(f"<font color='{global_storage.design.red}'><strong>High:</strong></font> "
                                   f"{scan_results.high_issues}",
                                   global_storage.design.styles["RegularParagraph"]))
        self.data.append(Paragraph(f"<font color='{global_storage.design.orange}'><strong>Medium:</strong></font> "
                                   f"{scan_results.medium_issues}",
                                   global_storage.design.styles["RegularParagraph"]))
        self.data.append(Paragraph(f"<font color='{global_storage.design.yellow}'><strong>Low:</strong></font> "
                                   f"{scan_results.low_issues}",
                                   global_storage.design.styles["RegularParagraph"]))
        self.data.append(Paragraph(f"<font color='{global_storage.design.blue}'><strong>Info:</strong></font> "
                                   f"{scan_results.info_issues}",
                                   global_storage.design.styles["RegularParagraph"]))

        # add info about skipped files if any
        if (scan_results.skipped_files):
            self.data.append(Paragraph(f"Skipped files ({len(scan_results.skipped_files)})",
                                       global_storage.design.styles["H2"]))
            for skipped_file in scan_results.skipped_files:
                self.data.append(Paragraph(f"{skipped_file.file_path} ({skipped_file.failure_reason})",
                                           global_storage.design.styles["SkippedFile"]))

        # break the page
        self.data.append(PageBreak())
