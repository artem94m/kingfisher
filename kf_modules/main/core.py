import ast
import tokenize
import re
import os
import xmlschema
import defusedxml.ElementTree as etree


class KfCore():
    def __init__(self, logger):
        # get logger from main module
        self.logger = logger

        # get available checks
        self.collect_checks()

        # block to node dict for empty block check
        self.block_to_node = {
            "except": ast.ExceptHandler,
            "def": ast.FunctionDef
        }

    ################################################################################
    """ functions for primary processing of checks """

    def collect_checks(self):
        """ append available checks to self.checks list """
        self.checks = []
        checks_path = os.path.join("checks", "default")
        check_schema_path = os.path.join("checks", "valid_check_schema.xsd")

        self.logger.info("Collecting checks...")

        # check if path is exists
        if (os.path.exists(checks_path) and os.path.isdir(checks_path)):
            # and it is accessible for reading
            if os.access(checks_path, os.R_OK):
                # if check schema (check.xsd) exists
                if (os.path.exists(check_schema_path)):
                    # and it is safe
                    if (self.is_xml_file_safe(check_schema_path)):
                        # go through recursively
                        for root, _, files in os.walk(checks_path, topdown=True):
                            for file in files:
                                # if file starts with "check_", ends with ".xml"
                                if (file.startswith("check_") and file.endswith(".xml")):
                                    check_path = os.path.join(root, file)
                                    # if check is a safe xml-file
                                    if (self.is_xml_file_safe(check_path)):
                                        # if check is valid
                                        if (self.is_xml_valid(check_path, check_schema_path)):
                                            # and enabled - append it to the list
                                            if (self.is_check_enabled(check_path)):
                                                self.checks.append(check_path)
                                            else:
                                                self.logger.info("Check {} is disabled".format(check_path))
                                        else:
                                            self.logger.warning("Check {} is not valid!".format(check_path))
                                    else:
                                        self.logger.error("Check {} is not safe!".format(check_path))
                    else:
                        self.logger.error("Schema of check {} is not safe!".format(check_schema_path))
                else:
                    self.logger.error("Schema of check {} is missing!".format(check_schema_path))
            else:
                self.logger.error("Checks folder is not accessible for reading!")
        else:
            self.logger.error("Checks folder does not exist!")

    def is_xml_file_safe(self, xml_filename):
        """ check if xml file is safe for parsing """
        result = False

        try:
            # try to parse xml safely
            etree.parse(xml_filename, forbid_dtd=True, forbid_entities=True, forbid_external=True)
        except Exception as error:
            self.logger.error("Cannot parse XML-file: {}".format(str(error)))
        else:
            result = True

        return result

    def is_xml_valid(self, xml_filename, xsd_filename):
        """ check if xml-file is valid again specific schema """
        result = False

        try:
            # try to parse schema
            schema = xmlschema.XMLSchema(xsd_filename)
        except Exception as error:
            self.logger.error("Schema {} is corrupted: {}".format(xsd_filename, str(error)))
        else:
            try:
                # and try to check xml against schema
                result = schema.is_valid(xml_filename)
            except Exception as error:
                self.logger.error("File {} is corrupted: {}".format(xml_filename, str(error)))

        return result

    def is_check_enabled(self, xml_filename):
        """ verify if check is enabled """
        result = False

        try:
            # try to parse xml safely
            xml_file = etree.parse(xml_filename, forbid_dtd=True, forbid_entities=True, forbid_external=True)
        except Exception as error:
            self.logger.error("Cannot parse check: {}".format(str(error)))
        else:
            # get root element (<check>)
            root = xml_file.getroot()
            # and check if it is enabled
            if ("status" in root.attrib and root.attrib["status"] == "enabled"):
                result = True

        return result

    def has_checks(self):
        """ if there are any checks """
        return bool(len(self.checks))

    def get_checks(self):
        """ get check names one by one """
        for check in self.checks:
            yield check

    ################################################################################
    """ functions for primary processing of files """

    def get_files_for_scan(self, scan_path):
        """ get .py files from provided scan_path """

        # if scan_path is a .py file - return only this file
        if (os.path.isfile(scan_path) and os.path.splitext(scan_path)[1] == ".py"):
            yield scan_path
        # if scan_path is a folder
        elif (os.path.isdir(scan_path)):
            # go through recursively
            for root, _, files in os.walk(scan_path, topdown=True):
                for file in files:
                    # and yield only .py files one by one
                    if (os.path.splitext(file)[1] == ".py"):
                        yield (os.path.join(root, file))

    def extract_data_from_file(self, file):
        """ extract all the necessary data from the file """
        self.data = {}

        # get AST
        self.data["tree"] = self.extract_tree_from_file(file)
        # get comments
        self.data["comments"] = self.extract_comments_from_file(file)
        # get aliases of imported objects
        self.data["aliases"] = self.extract_aliases_from_tree(self.data["tree"])

    def extract_tree_from_file(self, file):
        """ get AST from file """
        plain = None
        tree = None

        # get plain text of the file
        try:
            with open(file, "rb") as f:
                plain = f.read()
        except Exception as error:
            self.logger.warning("Cannot read file {}: {}".format(file, str(error)))
        else:
            # if file is not empty
            if (plain is not None):
                try:
                    # get AST from file using grammar for Python 3.8
                    tree = ast.parse(plain, feature_version=(3, 8))
                except Exception:
                    self.logger.warning("Cannot get AST from file {}. Skipping...".format(file))
        return tree

    def extract_comments_from_file(self, file):
        """ get comments from file """

        """
            AST tree contains only function description comment but it ignores comments like this (long string in the middle of code) and #-comments
            To deal with it - use tokenize module
        """
        comments = {}

        try:
            # open file with "rb" mode - required for tokenize
            with open(file, "rb") as f:
                # get all tokens from the file
                tokens = tokenize.tokenize(f.readline)

                # store previous token to exclude operations with a long string like this: """ text """ + OR print(""" text """)
                prev_token = None

                # go through all tokens
                for token in tokens:
                    # if token is #-comment
                    if (tokenize.tok_name[token.type] == "COMMENT"):
                        # token.start - returns a tuple with a number of line and column - position where the comment starts
                        row = token.start[0]
                        # adjust column value, because it starts from 0
                        column = token.start[1] + 1
                        # remove end of the line
                        text = token.string.rstrip("\r\n")
                        # add comment with the line and column number
                        comments[(row, column)] = text
                    # if token is a very long string (""") and it is not a part of expression - add it to the comments
                    elif (tokenize.tok_name[token.type] == "STRING" and tokenize.tok_name[prev_token.type] != "OP"):
                        # if it is one-liner (token starts and ends on the same line) - add to comments
                        if (token.start[0] == token.end[0]):
                            row = token.start[0]
                            column = token.start[1] + 1
                            text = token.string.rstrip("\r\n")
                            comments[(row, column)] = text
                        # if comment is multiline - add every string as a separate comment - for better positioning of vulnerabilities
                        else:
                            # get the number of the first line of the comment
                            line_no = token.start[0]
                            # split multiline comments by \n
                            comment_lines = token.string.split("\n")
                            # go through all comment lines
                            for line_no_in_comment, line in enumerate(comment_lines):
                                # first line of comment
                                if (line_no_in_comment == 0):
                                    # starts where token starts
                                    row = token.start[0]
                                    # adjust column position
                                    column = token.start[1] + 1
                                else:
                                    # line number where token starts plus line number in comment
                                    row = line_no + line_no_in_comment
                                    # technically, second and other lines of the comment starts from 1 position
                                    column = 1

                                # remove end of the line
                                text = line.rstrip("\r")
                                # add every line of multiline comments separately
                                comments[(row, column)] = text
                    # save token as previous
                    prev_token = token
        except Exception as error:
            self.logger.warning("Cannot extract comments from file {}: {}".format(file, str(error)))

        return comments

    def extract_aliases_from_tree(self, tree):
        """ get dict of aliases of imported objects """
        """
            Example:
            from hashlib import md5 as my_hash => my_hash: hashlib.md5
        """
        imported = {}

        # if tree was successfully parsed
        if (tree is not None and isinstance(tree, ast.Module)):
            # go through all the notes
            for node in ast.walk(tree):
                # if node is "import ..." or "from ... import ..."
                if (isinstance(node, (ast.Import, ast.ImportFrom))):
                    # ImportFrom also contains name of the imported module
                    base = ""
                    if (hasattr(node, "module") and node.module is not None):
                        base = node.module + "."

                    # go through all imported objects
                    for obj in node.names:
                        # if object has no alias
                        if (obj.asname is None):
                            # and was imported with ImportFrom (has module name)
                            if (base != ""):
                                # add to the result
                                # Example: "from hashlib import md5" converts to: "md5" : "hashlib.md5"
                                # key in dict is the object's name, which is used in the source code
                                # value in the dict is the actual path to the imported object
                                imported[obj.name] = base + obj.name
                        # if object has alias ("as ..." in import)
                        else:
                            # add to the result
                            # Example: "import hashlib as h" converts to: "h" : "hashlib"
                            # Example: "from hashlib import md5 as m" converts to: "m" : "hashlib.md5"
                            imported[obj.asname] = base + obj.name

        return imported

    ################################################################################
    """ functions to apply checks against files """

    def apply_check(self, check):
        """ apply checks to file data """
        result = set()

        # create dict of functions to call
        functions_to_call = self.parse_check(check)

        # if there are simple checks
        if (len(functions_to_call["pattern_simple"]) != 0):
            # try to apply all the simple checks to every node in the AST-tree
            for node in ast.walk(self.data["tree"]):
                # go through all functions and params
                for func_and_params in functions_to_call["pattern_simple"]:
                    # extract function and params separately
                    func_name, params = func_and_params

                    # call function with params
                    found = getattr(self, func_name)(node, **params)

                    if (found is not None):
                        result.update(found)

        # if there are checks for comments
        if ("comments" in functions_to_call and len(functions_to_call["comments"]) != 0):
            # go through all functions and params
            for func_and_params in functions_to_call["comments"]:
                # extract function and params separately
                func_name, params = func_and_params

                # call function with params
                found = getattr(self, func_name)(**params)

                if (found is not None):
                    result.update(found)

        return result if len(result) != 0 else None

    def parse_check(self, check):
        """ parse check for patterns """
        results = {}

        try:
            # try to parse xml safely
            xml_file = etree.parse(check, forbid_dtd=True, forbid_entities=True, forbid_external=True)
        except Exception as error:
            self.logger.error("Cannot parse check: " + str(error))
        else:
            # get patterns element (<patterns>)
            patterns = xml_file.find("patterns")
            # go thtough all subelements
            for pattern in patterns:
                if (pattern.tag == "pattern_simple"):
                    results.setdefault("pattern_simple", [])
                    # pattern_simple contains always only one subelement - get it
                    check_type = list(pattern).pop()

                    # add checks for comments to a separate list
                    # because they do not need to go through the tree
                    if (check_type.tag == "comment"):
                        results.setdefault("comments", [])
                        results["comments"].append(
                            (
                                "search_in_comment",
                                {"string": check_type.text.strip()}
                            )
                        )
                    elif (check_type.tag == "string"):
                        results["pattern_simple"].append(
                            (
                                "search_in_string_literal",
                                {
                                    "string": check_type.text.strip(),
                                    "operator": check_type.attrib["operator"]
                                }
                            )
                        )
                    elif (check_type.tag == "block" and check_type.attrib["operator"] == "empty"):
                        results["pattern_simple"].append(
                            (
                                "search_if_block_is_empty",
                                {"block_name": check_type.text.strip()}
                            )
                        )
                    elif (check_type.tag == "attribute"):
                        results["pattern_simple"].append(
                            (
                                "search_usage_of_attribute",
                                {"attr_to_find": check_type.text.strip()}
                            )
                        )
                    elif (check_type.tag == "function_call"):
                        name_tag = check_type.find("name")
                        results["pattern_simple"].append(
                            (
                                "search_function_call",
                                {
                                    "function_name": "" if name_tag.text is None else name_tag.text.strip(),
                                    "function_name_operator": name_tag.attrib["operator"]
                                }
                            )
                        )
                    elif (check_type.tag == "function_call_with_arg"):
                        name_tag = check_type.find("name")
                        param_tag = check_type.find("param")

                        operator, param_value = self.get_operator_and_value(param_tag)

                        results["pattern_simple"].append(
                            (
                                "search_function_call_with_arg",
                                {
                                    "function_name": "" if name_tag.text is None else name_tag.text.strip(),
                                    "function_name_operator": name_tag.attrib["operator"],
                                    "param_name": param_tag.attrib["name"].strip(),
                                    "param_pos": int(param_tag.attrib["pos"].strip()),
                                    "param_operator": operator,
                                    "param_value": param_value
                                }
                            )
                        )
                    elif (check_type.tag == "function_call_without_arg"):
                        name_tag = check_type.find("name")
                        param_tag = check_type.find("param")
                        results["pattern_simple"].append(
                            (
                                "search_function_call_without_arg",
                                {
                                    "function_name": "" if name_tag.text is None else name_tag.text.strip(),
                                    "function_name_operator": name_tag.attrib["operator"],
                                    "param_name": param_tag.attrib["name"].strip(),
                                    "param_pos": int(param_tag.attrib["pos"].strip())
                                }
                            )
                        )
                    elif (check_type.tag == "assignment_var"):
                        name_tag = check_type.find("name")

                        value_tag = check_type.find("value")

                        operator, value = self.get_operator_and_value(value_tag)

                        results["pattern_simple"].append(
                            (
                                "search_attribute_assignment",
                                {
                                    "name": "" if name_tag.text is None else name_tag.text.strip(),
                                    "name_operator": name_tag.attrib["operator"],
                                    "value": value,
                                    "value_operator": operator
                                }
                            )
                        )
                    elif (check_type.tag == "assignment_in_dict"):
                        name_tag = check_type.find("name")
                        key_tag = check_type.find("key")
                        value_tag = check_type.find("value")

                        operator, value = self.get_operator_and_value(value_tag)

                        results["pattern_simple"].append(
                            (
                                "search_dict_assignment",
                                {
                                    "name": "" if name_tag.text is None else name_tag.text.strip(),
                                    "name_operator": name_tag.attrib["operator"],
                                    "key": "" if key_tag.text is None else key_tag.text.strip(),
                                    "key_operator": key_tag.attrib["operator"],
                                    "value": value,
                                    "value_operator": operator
                                }
                            )
                        )
                    elif (check_type.tag == "unique_assignment_to_set_tuple_list"):
                        name_tag = check_type.find("name")
                        values_tag = check_type.find("values")

                        values = [value.text for value in list(values_tag)]

                        results["pattern_simple"].append(
                            (
                                "search_tuple_list_set_multiple_assignment",
                                {
                                    "name": "" if name_tag.text is None else name_tag.text.strip(),
                                    "name_operator": name_tag.attrib["operator"],
                                    "values_operator": values_tag.attrib["operator"],
                                    "values": values
                                }
                            )
                        )

        return results

    def get_operator_and_value(self, value_tag):
        """ extract operator and value from specific value type """
        # get inner tag
        value_type = list(value_tag).pop()

        # default
        operator = ""
        value = ""

        if (value_type.tag == "str"):
            operator = value_type.attrib["operator"]
            # strip string from newlines and spaces
            if (value_type.text is None):
                value = ""
            elif (isinstance(value_type.text, str)):
                value = value_type.text.strip()
            value = ast.Constant(value=value)
        elif (value_type.tag == "int"):
            operator = value_type.attrib["operator"]
            # convert value to integer
            value = ast.Constant(value=int(value_type.text))
        elif (value_type.tag == "bool"):
            operator = value_type.attrib["operator"]
            # bool value in xsd can be only "True", "False")
            if (value_type.text.strip() == "True"):
                value = True
            else:
                value = False
            value = ast.Constant(value=value)
        elif (value_type.tag == "none"):
            operator = value_type.attrib["operator"]
            value = ast.Constant(value=None)
        elif (value_type.tag == "attr"):
            operator = value_type.attrib["operator"]
            # get stripped attribute
            value = ast.Attribute(value=value_type.text.strip())
        elif (value_type.tag == "constant"):
            operator = value_type.attrib["operator"]
            # pass the ast.Constant type as result
            value = ast.Constant
        elif (value_type.tag == "function_call"):
            # support only "eq" operator for now
            operator = "eq"
            value = ast.Call(func=value_type.text.strip())

        return (operator, value)

    ################################################################################
    """ support functions for searching of vulnerabilities """

    def process_attributes_chain(self, node):
        """
            go recursively through a nested Attribute node (a.b.c.d.e.f)
            returns one string: "a.b.c.d.e.f"
        """
        result = ""

        # ast.Attribute contains "value" (can be another node) and "attr" (name of the current node)
        if (isinstance(node, ast.Attribute)):
            # go recursively through "value" and concat it with previous node using "." as separator
            result = ".".join((result, self.process_attributes_chain(node.value)))
            # and after add current "attr" to the result
            result = ".".join((result, node.attr))
        # ast.Name contains "id" (just name; actually, it is the first element in the chain) - return it
        elif (isinstance(node, ast.Name)):
            return node.id

        # remove first "." from result - it appears because result starts as ""
        return result.lstrip(".")

    def is_obj_equal_target(self, obj, target):
        """ check if the object is equal to the target """
        result = False

        # if exactly the same object was called
        # Example:
        #     Import in code: import Crypto
        #     In code the next attribute was used: Crypto.Cipher.AES.MODE_ECB
        # then just compare with the target
        if (obj == target):
            result = True
        # if exactly the same object was called by its alias
        # Example:
        #     Import in code: from Crypto.Cipher.AES import MODE_ECB as mode
        #     In aliases: "mode": "Crypto.Cipher.AES.MODE_ECB"
        #     In code the next object was used: mode
        # then get real path by alias and compare it with the target
        elif (obj in self.data["aliases"] and self.data["aliases"][obj] == target):
            result = True
        # if called is an object(attr/method) of alias of imported object
        # Example:
        #     Import in code: from Crypto.Cipher import AES
        #     In aliases: "AES": "Crypto.Cipher.AES"
        #     In code the next object was used: AES.MODE_ECB
        # then resolve alias to full path (Crypto.Cipher.AES.MODE_ECB) and compare with target
        elif (obj.find(".") != -1):
            # split the object into the alias of imported object and rest part
            alias, rest_of_object = obj.split(".", 1)

            # check if there is such an alias, replace it with a real path and compare result with the target
            if (alias in self.data["aliases"] and ".".join((self.data["aliases"][alias], rest_of_object)) == target):
                result = True

        return result

    def is_name_ok(self, name, operator, expected_value):
        """ check if name has expected value """
        result = False

        if (isinstance(name, str) and isinstance(expected_value, str)):
            # if we search exactly the same name
            if (operator == "eq" and self.is_obj_equal_target(name, expected_value)):
                result = True
            # if we search exactly NOT the same name
            elif (operator == "neq" and not self.is_obj_equal_target(name, expected_value) and name != expected_value):
                result = True
            # if name contains specific value (case-insensitive)
            elif (operator == "contains" and name.lower().find(expected_value.lower()) != -1):
                result = True

        return result

    def is_object_ok(self, obj, operator, expected):
        """ check if object has expected value """
        result = False

        if (operator == "not"):
            # if we want to compare passed object with a type
            if (isinstance(expected, type)):
                if (not isinstance(obj, expected)):
                    result = True
            elif (isinstance(expected, ast.Constant) and expected.value is None):
                if (isinstance(obj, ast.Constant) and obj.value is not None):
                    result = True
                elif (not isinstance(obj, ast.Constant)):
                    result = True
                    # if values have different types
                    # elif (type(obj.value) != type(expected.value)):
                    #    result = True
            # if object and expected value have different types
            elif (type(obj) != type(expected)):
                result = True
        else:
            # if we want to compare passed object with a type
            # if type of object and an expected are the same
            # now it is only works with Constant type
            if (isinstance(expected, type)):
                if (isinstance(obj, expected) and operator == "is"):
                    result = True
            # if passed object is a Constant
            elif (isinstance(obj, ast.Constant) and isinstance(expected, ast.Constant)):
                # if passed object and expected are strings (case-insensitive operations)
                if (isinstance(obj.value, (str, bytes)) and isinstance(expected.value, (str, bytes))):
                    object_value = obj.value.decode(encoding="utf-8", errors="ignore") if isinstance(obj.value, bytes) else obj.value
                    expected_value = expected.value

                    if (operator == "contains" and object_value.lower().find(expected_value.lower()) != -1):
                        result = True
                    elif (operator == "eq" and object_value.lower() == expected_value.lower()):
                        result = True
                    elif (operator == "neq" and object_value.lower() != expected_value.lower()):
                        result = True
                    elif (operator == "starts" and object_value.startswith(expected_value)):
                        result = True
                # if passed object and expected are ints
                # use this type of comparison to avoid: isinstance(True, int) equals "True"
                elif (type(obj.value).__name__ == "int" and type(expected.value).__name__ == "int"):
                    if (operator == "gt" and obj.value > expected.value):
                        result = True
                    elif (operator == "lt" and obj.value < expected.value):
                        result = True
                    elif (operator == "eq" and obj.value == expected.value):
                        result = True
                    elif (operator == "neq" and obj.value != expected.value):
                        result = True
                # if passed object and expected are booleans
                elif (isinstance(obj.value, bool) and isinstance(expected.value, bool)):
                    if (operator == "eq" and obj.value == expected.value):
                        result = True
                    if (operator == "neq" and obj.value != expected.value):
                        result = True
                # if passed object and expected are None
                elif (obj.value is None and operator == "is" and expected.value is None):
                    result = True

            # if passed object is an Attribute or a Name
            elif (isinstance(obj, (ast.Attribute, ast.Name)) and isinstance(expected, ast.Attribute)):

                # get the full path to the object
                processed_object = self.process_attributes_chain(obj)

                # processed_object is equal to the expected
                if (self.is_obj_equal_target(processed_object, expected.value)):
                    if (operator == "eq"):
                        result = True
                else:
                    if (operator == "neq"):
                        result = True
            # if passed object is a Function Call
            elif (isinstance(obj, ast.Call) and isinstance(expected, ast.Call)):
                called = ""

                # it can be simple id like so: print
                if (isinstance(obj.func, ast.Name)):
                    called = obj.func.id
                # or it can be chain of attributes: sys.stdout.write
                elif (isinstance(obj.func, ast.Attribute)):
                    called = self.process_attributes_chain(obj.func)

                # only check if called object is equal to an expected function call
                if (self.is_obj_equal_target(called, expected.func) and operator == "eq"):
                    result = True

        return result

    ################################################################################
    """ functions for searching of vulnerabilities """

    def search_in_comment(self, string):
        """ search text in comments """
        # result is a set
        # because of that we can avoid repeating of found vulnerabilities
        # For example:
        # if we are trying to find "password" and "pass" keywords as a mark of precense of a hardcoded password in comments
        # the keyword "password" will trigger check twice, but with the same result (position where keyword "password" starts)
        # however, set() will store only one occurence
        result = set()

        # go through all the comments (comment_pos is a row and column numbers)
        for comment_pos in self.data["comments"]:
            # go through all search_values to avoid several loops for one check

            # looking for all occurences of text (case-insensitive)
            for item in re.finditer(string.lower(), self.data["comments"][comment_pos].lower()):
                # get position of found text
                row = comment_pos[0]
                column = comment_pos[1] + item.start()
                # add to the results
                result.add((row, column))

        return result if len(result) != 0 else None

    def search_in_string_literal(self, node, string, operator):
        """ search for specific value in a string """
        result = set()

        # if node is a string constant
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            # get position of node
            row = node.lineno
            column = node.col_offset + 1

            # support two operators of search (case-insensitive search)
            if (operator == "eq"):
                if (node.value.lower() == string.lower()):
                    result.add((row, column))
            if (operator == "starts"):
                if (node.value.lower().startswith(string.lower())):
                    result.add((row, column))
            elif (operator == "contains"):
                for item in re.finditer(string.lower(), node.value.lower()):
                    # adjust position
                    # found substring is placed at: token_position + position_in_substring (have to add 1 because string starts from 0)
                    column = column + item.start() + 1
                    result.add((row, column))

        return result if len(result) != 0 else None

    def search_if_block_is_empty(self, node, block_name):
        """ check if block is empty - contains only pass expressions """
        result = set()

        # block_name is a simple string like "except" or "def"
        # extract from self.block_to_node node class by string: "except" turns to ast.ExceptHandler
        # check if current node is the right one
        if (block_name in self.block_to_node and isinstance(node, self.block_to_node[block_name]) and hasattr(node, "body")):
            # extract from body of the node unique node classes
            body_unique_nodes = set(type(expr) for expr in node.body)
            # if unique nodes contains only Pass nodes (set() saves only one of them) - block is empty
            if (len(body_unique_nodes) == 1 and body_unique_nodes.pop() == ast.Pass):
                # get position of node
                row = node.lineno
                column = node.col_offset

                result.add((row, column))

        return result if len(result) != 0 else None

    def search_usage_of_attribute(self, node, attr_to_find):
        """ search for usage of attribute """
        result = set()

        # if node is an attribute
        if (isinstance(node, ast.Attribute)):
            # get position of node
            row = node.lineno
            column = node.col_offset + 1

            # get chain of attributes: Crypto.Cipher.AES.MODE_ECB
            used_attr = self.process_attributes_chain(node)

            if (self.is_obj_equal_target(used_attr, attr_to_find)):
                result.add((row, column))

        return result if len(result) != 0 else None

    def search_function_call(self, node, function_name, function_name_operator):
        """ search just function call """
        result = set()

        # if node is a function call
        if (isinstance(node, ast.Call)):
            # get position of node
            row = node.lineno
            column = node.col_offset + 1

            called_func = None
            # it can be simple id like so: print
            if (isinstance(node.func, ast.Name)):
                called_func = node.func.id
            # or it can be chain of attributes: sys.stdout.write
            elif (isinstance(node.func, ast.Attribute)):
                called_func = self.process_attributes_chain(node.func)

            if (called_func is not None and self.is_name_ok(called_func, function_name_operator, function_name)):
                result.add((row, column))

        return result if len(result) != 0 else None

    def search_function_call_without_arg(self, node, function_name, function_name_operator, param_name, param_pos):
        """ search function call without specific arg """
        result = set()

        # if node is a function call
        if (isinstance(node, ast.Call)):
            called_func = None
            # it can be simple id like so: print
            if (isinstance(node.func, ast.Name)):
                called_func = node.func.id
            # or it can be chain of attributes: sys.stdout.write
            elif (isinstance(node.func, ast.Attribute)):
                called_func = self.process_attributes_chain(node.func)

            # if called function is equal to function_name
            if (called_func is not None and self.is_name_ok(called_func, function_name_operator, function_name)):
                # get position of node
                row = node.lineno
                column = node.col_offset + 1

                # get names of all keywords
                all_keywords = [keyword.arg for keyword in node.keywords if isinstance(keyword, ast.keyword)]

                # if there are less positional arguments than position of current argument
                # and current parameter was not found in keywords
                if ((param_pos < 1 or param_pos > len(node.args)) and param_name not in all_keywords):
                    # vulnerability is found
                    result.add((row, column))

        return result if len(result) != 0 else None

    def search_function_call_with_arg(self, node, function_name, function_name_operator, param_name, param_pos, param_operator, param_value):
        """ search function call with specific arg """
        result = set()

        # if node is a function call
        if (isinstance(node, ast.Call)):
            called_func = None
            # it can be simple id like so: print
            if (isinstance(node.func, ast.Name)):
                called_func = node.func.id
            # or it can be chain of attributes: sys.stdout.write
            elif (isinstance(node.func, ast.Attribute)):
                called_func = self.process_attributes_chain(node.func)

            # if called function is equal to function_name
            if (called_func is not None and self.is_name_ok(called_func, function_name_operator, function_name)):
                # get position of node
                row = node.lineno
                column = node.col_offset + 1

                # for later check if parameter exists
                param = None

                # go through all keywords first
                for keyword in node.keywords:
                    # if keywords contain keyword with a param_name
                    if (isinstance(keyword, ast.keyword) and keyword.arg == param_name):
                        # assign value of argument
                        param = keyword.value
                        break
                # if have not found param in keywords - search in positional arguments
                if (param is None):
                    # go through all positional arguments
                    for pos, arg in enumerate(node.args, start=1):
                        # if found positional argument
                        if (pos == param_pos):
                            param = arg
                            break

                # if passed parameter has expected value
                if (param is not None and self.is_object_ok(param, param_operator, param_value)):
                    result.add((row, column))

        return result if len(result) != 0 else None

    def search_tuple_list_set_multiple_assignment(self, node, name, name_operator, values_operator, values):
        """ search assignment, where the value is a tuple, list or set """
        result = set()

        # if node is an Assign, contains one target (which is a Name or an Attribute) and an assigned value is a List, Tuple or Set
        if (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], (ast.Name, ast.Attribute)) and isinstance(node.value, (ast.List, ast.Tuple, ast.Set))):
            # get position of node
            row = node.lineno
            column = node.col_offset + 1

            # get the target object
            target_obj = node.targets[0]
            # get the full path to the target
            target = self.process_attributes_chain(target_obj)

            # if target is ok
            if (self.is_name_ok(target, name_operator, name)):
                # get a set of assigned values
                assigned_values = set(elem.value for elem in node.value.elts if isinstance(elem, ast.Constant))
                # convert search values to a set
                search_values = set(values)

                # if search_values are a subset of assigned values
                if (values_operator == "contains" and search_values.issubset(assigned_values)):
                    result.add((row, column))
                elif (values_operator == "missing" and len(search_values.intersection(assigned_values)) == 0):
                    # vulnerability was found
                    result.add((row, column))

        return result if len(result) != 0 else None

    def search_attribute_assignment(self, node, name, name_operator, value, value_operator):
        """ search assignment: attribute = constant """
        result = set()

        # if node is an Assign and an assignment has just one target
        if (isinstance(node, ast.Assign) and len(node.targets) == 1):
            # get position of node
            row = node.lineno
            column = node.col_offset + 1

            # lists for targets and values
            targets = []
            values = []

            # if it is a simple singular assignment: a = 4 or a.b.c.d = 3
            if (isinstance(node.targets[0], (ast.Attribute, ast.Name))):
                # add one element in each list
                targets.append(node.targets[0])
                values.append(node.value)
            # if it is a simple multiple assignment: a, a.d.c = 3, "password"
            elif (isinstance(node.targets[0], ast.Tuple) and isinstance(node.value, ast.Tuple)):
                # add all elements to the targets and values lists respectively
                targets = node.targets[0].elts
                values = node.value.elts

            # go through created lists of targets and values
            for target_number, target_obj in enumerate(targets):
                # get value from values list
                value_obj = values[target_number]

                # if target is an Attribute or Name
                if (isinstance(target_obj, (ast.Attribute, ast.Name))):
                    # get the full path to the target
                    target = self.process_attributes_chain(target_obj)

                    if (self.is_name_ok(target, name_operator, name) and 
                        self.is_object_ok(value_obj, value_operator, value)):
                        # vulnerability is found
                        result.add((row, column))

        return result if len(result) != 0 else None

    def search_dict_assignment(self, node, name, name_operator, key, key_operator, value, value_operator):
        """ search assignment: dict[key] = constant or dict = {key : constant} """
        result = set()

        if (isinstance(node, ast.Assign) and len(node.targets) == 1):
            # get position of node
            row = node.lineno
            column = node.col_offset + 1

            # lists of keys and values to check for an expected assigment
            keys = []
            values = []

            target = None

            # if node is an Assign, contains one target which is key in a dict: a["key"] = value
            if (isinstance(node.targets[0], ast.Subscript)):
                # get the full path to the target
                target = self.process_attributes_chain(node.targets[0].value)

                # get slice type of a dict
                slice_obj = node.targets[0].slice
                # if Index (a["key"])
                if (isinstance(slice_obj, ast.Index)):
                    # append "key"
                    keys.append(slice_obj.value)
                    # append value
                    values.append(node.value)
                elif (isinstance(slice_obj, ast.Constant)):
                    # append "key"
                    keys.append(slice_obj)
                    # append value
                    values.append(node.value)

            # if node is an Assign, contains one target (name of a dict) and a dict: a = {"key": value}
            elif (isinstance(node.targets[0], (ast.Name, ast.Attribute)) and isinstance(node.value, ast.Dict)):
                # get the full path to the target
                target = self.process_attributes_chain(node.targets[0])

                # get keys and values lists
                keys = node.value.keys
                values = node.value.values

            if (self.is_name_ok(target, name_operator, name)):
                # go through all the keys of the dict

                for key_number, k in enumerate(keys):
                    key_passed_check = False

                    # if key is a string
                    if (isinstance(k, ast.Constant) and isinstance(k.value, str)):
                        # get value of key
                        key_in_code = k.value

                        # if we search exact key name
                        if (key_operator == "eq" and key_in_code.lower() == key.lower()):
                            key_passed_check = True
                        # if key contains key_name
                        elif (key_operator == "contains" and key_in_code.lower().find(key.lower()) != -1):
                            key_passed_check = True

                        # get value for appropriate key
                        value_in_code = values[key_number]

                        # if key is fine and object is ok
                        if (key_passed_check and self.is_object_ok(value_in_code, value_operator, value)):
                            # vulnerability is found
                            result.add((row, column))

        return result if len(result) != 0 else None
