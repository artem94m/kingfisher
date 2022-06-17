from ast import ExceptHandler, FunctionDef, Pass, walk as ast_walk


def analyze_block(py_file_info, block_name, operator):
    """Searches for empty blocks (contain only pass expressions) in the tree

    Returns set with locations of the issues
    """
    issues = set()

    block_name_to_node = {
        "except": ExceptHandler,
        "def": FunctionDef,
    }

    if (block_name in block_name_to_node and operator == "empty"):
        type_of_node = block_name_to_node[block_name]

        for node in ast_walk(py_file_info.tree):
            if (isinstance(node, type_of_node)):
                # extract from body of the node unique node classes
                body_unique_nodes = {type(expr) for expr in node.body}

                # if body_unique_nodes contains only Pass nodes - node is empty
                if (len(body_unique_nodes) == 1 and body_unique_nodes.pop() == Pass):
                    issue_location = (node.lineno, node.col_offset + 1)
                    issues.add(issue_location)

    return issues
