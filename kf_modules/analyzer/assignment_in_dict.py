from ast import Assign, Attribute, Constant, Dict, Name, Subscript, walk as ast_walk

from kf_modules.analyzer._common import IsObjValueMeetConditions, is_obj_fit_target, process_attributes_chain


def analyze_assignment_in_dict(py_file_info, name, name_operator, key, key_operator, value, value_operator):
    """Searches for the assignment of the specific value to the specific key of the specific dict variable.

    Returns set with locations of the issues
    """
    issues = set()

    for node in ast_walk(py_file_info.tree):
        # if node is Assign
        if (isinstance(node, Assign) and len(node.targets) == 1 and
                # and Target is a dict (a["key"] = value) or value is a dict (a = {"key": value})
                (isinstance(node.targets[0], Subscript) or isinstance(node.value, Dict))):

            target, keys, values = get_target_keys_values(node)

            # check variable name
            if (is_obj_fit_target(target, name_operator, name, py_file_info.aliases) and keys and values):
                # check every key one by one
                for key_index, key_in_code in enumerate(keys):
                    # if key is a string
                    if (isinstance(key_in_code, Constant) and isinstance(key_in_code.value, str)):
                        # prepare key_in_code and key_to_search for case-insensitive comparison
                        key_in_code_low = key_in_code.value.lower()
                        key_to_search_low = key.lower()

                        if ((key_operator == "eq" and key_in_code_low == key_to_search_low) or
                                (key_operator == "contains" and key_in_code_low.find(key_to_search_low) != -1)):
                            # key is fine, check the value

                            # if there is a value for the key
                            if ((key_index < len(values)) and
                                    # and the value for the key meets the expected conditions
                                    IsObjValueMeetConditions(values[key_index], value_operator, value,
                                                             py_file_info.aliases).result):
                                issue_location = (node.lineno, node.col_offset + 1)
                                issues.add(issue_location)

    return issues


def get_target_keys_values(node):
    """Extracts target, keys and values from the dict assignment
    """
    target = None
    keys = []
    values = []

    # If the assignment is like this: a["key"] = value
    if (isinstance(node.targets[0], Subscript)):
        target = process_attributes_chain(node.targets[0].value)

        # if dict's key is a Constant (a["key"])
        if (isinstance(node.targets[0].slice, Constant)):
            keys.append(node.targets[0].slice)
            values.append(node.value)
    # If the assignment is like this: a = {"key": value}
    elif (isinstance(node.targets[0], (Name, Attribute)) and isinstance(node.value, Dict)):
        target = process_attributes_chain(node.targets[0])
        keys = node.value.keys
        values = node.value.values

    return target, keys, values
