from ast import Attribute, Call, Name, keyword as ast_keyword, walk as ast_walk

from kf_modules.analyzer._common import IsObjValueMeetConditions, is_obj_fit_target, process_attributes_chain


def analyze_function_call_with_arg(py_file_info, function_name, function_name_operator,
                                   param_name, param_pos, param_operator, param_value):
    """Searches for usage of the specific function with a specific argument in code

    Returns set with locations of the issues
    """
    issues = set()

    for node in ast_walk(py_file_info.tree):
        if (isinstance(node, Call) and isinstance(node.func, (Name, Attribute))):
            full_func = process_attributes_chain(node.func)

            if (is_obj_fit_target(full_func, function_name_operator, function_name, py_file_info.aliases)):
                is_extracted_successful, param = get_param_from_func_node(node, param_name, param_pos)

                if (is_extracted_successful and
                        IsObjValueMeetConditions(param, param_operator, param_value, py_file_info.aliases).result):
                    issue_location = (node.lineno, node.col_offset + 1)
                    issues.add(issue_location)

    return issues


def get_param_from_func_node(node, param_name, param_pos):
    """Extracts the specific param from function call
    """
    # need this for the case when param is equal None
    is_extracted_successful = False
    param = None

    # look for the parameter in keyword args first
    for keyword in node.keywords:
        if (isinstance(keyword, ast_keyword) and param_name == keyword.arg):
            param = keyword.value
            is_extracted_successful = True
            break
    # if did not found param in keyword args - then search in positional args
    if (not is_extracted_successful):
        if (1 <= param_pos <= len(node.args)):
            param_pos_in_args_list = param_pos - 1
            param = node.args[param_pos_in_args_list]

            is_extracted_successful = True

    return is_extracted_successful, param
