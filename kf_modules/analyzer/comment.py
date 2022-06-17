from re import IGNORECASE, finditer


def analyze_comment(py_file_info, text):
    """Searches for the specific text in comments

    Returns set with locations of the issues
    """
    issues = set()

    # check if there are comments and text to search is not an empty string
    if (py_file_info.comments and text):
        for comment in py_file_info.comments:
            for issue in finditer(text, comment.text, IGNORECASE):
                issue_location = (comment.line_no, comment.pos + issue.start())
                issues.add(issue_location)

    return issues
