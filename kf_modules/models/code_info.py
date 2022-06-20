from ast import Import, ImportFrom, parse as ast_parse, walk as ast_walk
from tokenize import TokenInfo, tok_name, tokenize

import global_storage


class Comment():
    """Class to store comment info
    """
    def __init__(self, location, text):
        # extract line and position
        line_no, pos = location

        # number line in source code
        self.line_no = line_no
        # adjust position in line value, because it starts from 0
        self.pos = pos + 1
        # text of the comment
        self.text = text.rstrip()


class CodeInfoExtractor():
    """Class to extract all the required info from the .py-file
    """
    def __init__(self, py_file):
        # marker if info was extracted successfully
        self.extracted_successful = False
        # failure reason if not
        self.failure_reason = ""

        self.file_path = py_file
        self.source_code = self.extract_source_code_from_file(py_file)

        if (self.source_code is not None):
            self.tree = self.extract_tree_from_file(py_file)

            if (self.tree is not None):
                self.comments = self.extract_comments_from_file(py_file)
                self.aliases = self.extract_aliases_from_tree(self.tree)

        if (not self.failure_reason):
            self.extracted_successful = True

    def extract_source_code_from_file(self, py_file):
        """Gets source code from the file
        """
        source_code = None

        try:
            with open(py_file, "r", encoding="utf-8") as fd:
                source_code = {line_no: text.rstrip() for line_no, text in enumerate(fd.readlines(), start=1)}
        except Exception as error:
            self.failure_reason = error
            global_storage.logger.warning(f"Cannot extract source code from file {py_file}: {error}")

        return source_code

    def extract_tree_from_file(self, py_file):
        """Gets AST from the file
        """
        source_code = None
        tree = None

        try:
            with open(py_file, "rb") as fd:
                source_code = fd.read()
        except Exception as error:
            self.failure_reason = error
            global_storage.logger.warning(f"Cannot read file {py_file}: {error}")
        else:
            try:
                tree = ast_parse(source_code, feature_version=(3, 9))
            except Exception as error:
                self.failure_reason = error
                global_storage.logger.warning(f"Cannot get AST from file {py_file}: {error}. Skipping...")

        return tree

    def extract_comments_from_file(self, py_file):
        """Gets comments from the file

           AST tree contains only function description comment, but it ignores
           multiline comments and #-comments in the middle of code
           To get them - we use tokenize module
        """
        comments = []

        try:
            with open(py_file, "rb") as fd:
                prev_token = None
                cur_token = None
                next_token = None

                for token in tokenize(fd.readline):
                    # we need the prev, current and next tokens to parse multiline comments correctly
                    prev_token = cur_token
                    cur_token = next_token
                    next_token = token

                    if (isinstance(prev_token, TokenInfo) and
                            isinstance(cur_token, TokenInfo) and
                            isinstance(next_token, TokenInfo)):
                        # if token is #-comment
                        if (tok_name[cur_token.type] == "COMMENT"):
                            comments.append(Comment(cur_token.start, cur_token.string))
                        # if token is a multiline comment (""")
                        elif (tok_name[prev_token.type] != "OP" and
                                tok_name[cur_token.type] == "STRING" and
                                cur_token.string.startswith('"""') and
                                cur_token.string.endswith('"""') and
                                tok_name[next_token.type] == "NEWLINE"):

                            # get line_no of the first line of the comment
                            init_line_no = cur_token.start[0]
                            # split multiline comments by \n
                            comment_lines = cur_token.string.split("\n")
                            # marker to check if the first line of the comment was processed
                            is_first_line_processed = False
                            for line_no, line_text in enumerate(comment_lines, start=init_line_no):
                                location = cur_token.start if not is_first_line_processed else (line_no, 0)
                                is_first_line_processed = True
                                comments.append(Comment(location, line_text))
        except Exception as error:
            self.failure_reason = error
            global_storage.logger.warning(f"Cannot extract comments from file {py_file}: {error}")

        return comments

    def extract_aliases_from_tree(self, tree):
        """Gets dict of aliases for imported objects

            Examples:
            from hashlib import md5 as my_hash => "my_hash": "hashlib.md5"
            import token as t => "t": "token"
            from os import path => "path": "os.path"
        """
        aliases = {}

        for node in ast_walk(tree):
            if (isinstance(node, Import)):
                # collect only imports with "as" keyword
                node_aliases = {alias.asname: alias.name for alias in node.names if alias.asname}
                aliases.update(node_aliases)
            elif (isinstance(node, ImportFrom)):
                # get "from" value if possible
                from_value = f"{node.module}." if node.module is not None else ""
                node_aliases = {}

                for alias in node.names:
                    # add alias if it is specified
                    if (alias.asname):
                        node_aliases[alias.asname] = f"{from_value}{alias.name}"
                    # otherwise - add the full path to the original name only if "from" was specified
                    elif (from_value):
                        node_aliases[alias.name] = f"{from_value}{alias.name}"

                aliases.update(node_aliases)

        return aliases
