from ast import Assign, Attribute, Name, Tuple, walk as ast_walk

from kf_modules.analyzer._common import IsObjValueMeetConditions, is_obj_fit_target, process_attributes_chain


def analyze_assignment_var(py_file_info, name, name_operator, value, value_operator):
    """Searches for the assignment of specified simple value to the specified variable.

    Returns set with locations of the issues
    """
    issues = set()

    for node in ast_walk(py_file_info.tree):
        if (isinstance(node, Assign) and len(node.targets) == 1):
            # Supported types of assignment:
            # a = 1
            # a, b = 1, 2
            # Not supported types of assignment:
            # a = b = 1
            # a,b = c
            # lists for targets and values
            targets = []
            values = []

            # if it is a simple singular assignment: a = 4 or a.b.c.d = 3
            if (isinstance(node.targets[0], (Attribute, Name))):
                targets.append(node.targets[0])
                values.append(node.value)
            # if it is a simple multiple assignment: a, a.d.c = 3, "password"
            elif (isinstance(node.targets[0], Tuple) and isinstance(node.value, Tuple)):
                targets = node.targets[0].elts
                values = node.value.elts

            # get the number of valid assignments (when a target has a value)
            number_of_valid_assignments = min(len(targets), len(values))
            for assign_index in range(0, number_of_valid_assignments):
                target_obj = targets[assign_index]
                value_obj = values[assign_index]

                if (isinstance(target_obj, (Attribute, Name))):
                    full_target = process_attributes_chain(target_obj)

                    if (is_obj_fit_target(full_target, name_operator, name, py_file_info.aliases) and
                            IsObjValueMeetConditions(value_obj, value_operator, value, py_file_info.aliases).result):
                        issue_location = (node.lineno, node.col_offset + 1)
                        issues.add(issue_location)

    return issues
