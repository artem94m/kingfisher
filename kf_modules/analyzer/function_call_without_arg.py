from ast import Attribute, Call, Name, keyword as ast_keyword, walk as ast_walk

from kf_modules.analyzer._common import is_obj_fit_target, process_attributes_chain


def analyze_function_call_without_arg(py_file_info, function_name, function_name_operator, param_name, param_pos):
    """Searches for usage of the specific function without a specific argument in code

    Returns set with locations of the issues
    """
    issues = set()

    for node in ast_walk(py_file_info.tree):
        if (isinstance(node, Call) and isinstance(node.func, (Name, Attribute))):
            full_func = process_attributes_chain(node.func)

            if (is_obj_fit_target(full_func, function_name_operator, function_name, py_file_info.aliases)):
                number_of_positional_args = len(node.args)
                passed_keyword_args = [keyword.arg for keyword in node.keywords if isinstance(keyword, ast_keyword)]

                # if param_pos not in range of number of specified positional arguments
                if (not(1 <= param_pos <= number_of_positional_args) and
                        # and current parameter was not found in keywords
                        param_name not in passed_keyword_args):

                    issue_location = (node.lineno, node.col_offset + 1)
                    issues.add(issue_location)

    return issues
