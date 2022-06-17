from ast import Assign, Attribute, Constant, List, Name, Set, Tuple, walk as ast_walk

from kf_modules.analyzer._common import is_obj_fit_target, process_attributes_chain


def analyze_unique_assignment_to_set_tuple_list(py_file_info, name, name_operator, values, values_operator):
    """Searches for the assignment where specific unique string values were assigned/missed in a set, tuple or list.

    Returns set with locations of the issues
    """
    issues = set()

    for node in ast_walk(py_file_info.tree):
        # if node is an Assign, contains one target (which is a Name or an Attribute) and
        # an assigned value is a List, Tuple or Set
        if (isinstance(node, Assign) and len(node.targets) == 1 and
                isinstance(node.targets[0], (Name, Attribute)) and
                isinstance(node.value, (List, Tuple, Set))):
            target_obj = node.targets[0]
            full_target = process_attributes_chain(target_obj)

            if (is_obj_fit_target(full_target, name_operator, name, py_file_info.aliases)):
                # get a set of assigned values
                assigned_values = set(elem.value for elem in node.value.elts if isinstance(elem, Constant))
                # convert search values to a set
                search_values = set(values)

                # if all the search values are present in assigned values and operator is "contains"
                if ((values_operator == "contains" and search_values.issubset(assigned_values)) or
                        # if none of the search values are present in the assigned value
                        (values_operator == "missing" and len(search_values.intersection(assigned_values)) == 0)):
                    issue_location = (node.lineno, node.col_offset + 1)
                    issues.add(issue_location)

    return issues
