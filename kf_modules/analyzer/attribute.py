from ast import Attribute, walk as ast_walk

from kf_modules.analyzer._common import is_obj_equal_target
from kf_modules.analyzer._common import process_attributes_chain


def analyze_attribute(py_file_info, attribute_name):
    """Searches for usage of the specific attribute in code

    Returns set with locations of the issues
    """
    issues = set()

    for node in ast_walk(py_file_info.tree):
        if (isinstance(node, Attribute)):
            full_attr = process_attributes_chain(node)

            if (is_obj_equal_target(full_attr, attribute_name, py_file_info.aliases)):
                issue_location = (node.lineno, node.col_offset + 1)
                issues.add(issue_location)

    return issues
