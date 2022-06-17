from ast import Constant, walk as ast_walk
from re import finditer


def analyze_string(py_file_info, text, operator):
    """Searches for the specific text in strings

    Returns set with locations of the issues
    """
    issues = set()

    for node in ast_walk(py_file_info.tree):
        if (isinstance(node, Constant) and isinstance(node.value, str)):
            # convert both values to lowercase for correct search
            node_value = node.value.lower()
            text_to_search = text.lower()

            if (operator == "eq" and node_value == text_to_search):
                issue_location = (node.lineno, node.col_offset + 1)
                issues.add(issue_location)
            if (operator == "starts" and node_value.startswith(text_to_search)):
                issue_location = (node.lineno, node.col_offset + 1)
                issues.add(issue_location)
            elif (operator == "contains"):
                for found in finditer(text_to_search, node_value):
                    # found substring is placed at:
                    # node's position + position in string + 1 (in tree lines start from 0)
                    pos = node.col_offset + found.start() + 1

                    issue_location = (node.lineno, pos)
                    issues.add(issue_location)

    return issues
