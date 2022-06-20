from ast import Attribute, Call, Name, walk as ast_walk

from kf_modules.analyzer._common import is_obj_fit_target, process_attributes_chain


def analyze_function_call(py_file_info, function_name, operator):
    """Searches for usage of the specific function in code

    Returns set with locations of the issues
    """
    issues = set()

    for node in ast_walk(py_file_info.tree):
        if (isinstance(node, Call) and isinstance(node.func, (Name, Attribute))):
            full_func = process_attributes_chain(node.func)

            if (is_obj_fit_target(full_func, operator, function_name, py_file_info.aliases)):
                issue_location = (node.lineno, node.col_offset + 1)
                issues.add(issue_location)

    return issues
