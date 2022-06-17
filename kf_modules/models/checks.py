from ast import Attribute, Call, Constant

from defusedxml.ElementTree import tostring

import global_storage


class Checks(list):
    """Class to store list of Check
    """
    def get(self, check_name):
        """Returns Check with the specified name
        """
        result = None

        for check in self.__iter__():
            if (check.name == check_name):
                result = check
                break

        return result

    def __contains__(self, other_check):
        """Tests (by name of the check) if the other check is already existing in the list
        """
        result = False

        for existing_check in self.__iter__():
            if (existing_check.name == other_check.name):
                result = True
                break

        return result


class Check():
    """Class to store info about the check
    """
    def __init__(self, element_tree, hash_of_check):
        # SHA1 of the xml-file which contains the check
        self.xml_hash = hash_of_check

        # is check enabled to use
        self.is_enabled = False

        # name of the check
        self.name = ""
        # short description
        self.description = ""
        # long description
        self.explanation = ""
        # severity of the vulnerability
        self.severity = ""
        # the recommendations to remediate
        self.recommendations = ""
        # links to prove the vulnerability
        self.links = ""
        # patterns of the vulnerability
        self.patterns = []

        self.init_from_element_tree(element_tree)

    @property
    def is_valid(self):
        """Checks if the check itself has all the required attributes set
        """
        result = False

        if (self.name and self.description and self.explanation and
                self.severity and self.recommendations and self.links and self.patterns):
            result = True

        return result

    def init_from_element_tree(self, element_tree):
        """Inits all the checks attributes from the element tree
        """
        root = element_tree.getroot()

        # parse status of the check (if it is enabled)
        if (root.tag == "check" and "status" in root.attrib):
            self.is_enabled = True if root.attrib["status"] == "enabled" else False

            # parse other required attributes (sub-elements) of the check
            text_attributes_of_check = ("name", "description", "explanation", "severity", "recommendations", "links")
            for cur_element in list(root):
                if (cur_element.tag in text_attributes_of_check):
                    setattr(self, cur_element.tag, cur_element.text)

                # parse check patterns
                if (cur_element.tag == "patterns"):
                    for pattern_element in list(cur_element):
                        parsed_pattern = Pattern(pattern_element)

                        if (parsed_pattern.is_valid):
                            self.patterns.append(parsed_pattern)
                        else:
                            global_storage.logger.debug("Pattern is invalid: \n"
                                                        f"{tostring(pattern_element, encoding='unicode')}")


class Pattern():
    """Class to store info about a single pattern
    """
    # implemented types of pattern
    simple_types = ("comment",
                    "string",
                    "block",
                    "attribute",
                    "function_call",
                    "function_call_without_arg",
                    "function_call_with_arg",
                    "assignment_var",
                    "assignment_in_dict",
                    "unique_assignment_to_set_tuple_list")

    def __init__(self, pattern):
        # name of the pattern to apply against the check
        self.func_to_call = ""
        # params to pass to the function
        self.params = {}

        if (pattern.tag == "pattern_simple"):
            # <pattern_simple> contains ONLY one sub-element with a pattern type
            # extracting it
            pattern_type = list(pattern).pop()

            if (pattern_type.tag in Pattern.simple_types):
                # get parser according to the pattern_type
                parser = getattr(self, f"parse_{pattern_type.tag}_pattern")
                # parse the pattern
                parser(pattern_type)

    def parse_comment_pattern(self, pattern):
        """Parses <comment> pattern
        """
        self.func_to_call = "analyze_comment"
        self.params = {
            "text": clean(pattern.text),
        }

    def parse_string_pattern(self, pattern):
        """Parses <string> pattern
        """
        self.func_to_call = "analyze_string"
        self.params = {
            "text": clean(pattern.text),
            "operator": pattern.attrib["operator"],
        }

    def parse_block_pattern(self, pattern):
        """Parses <block> pattern
        """
        self.func_to_call = "analyze_block"
        self.params = {
            "block_name": clean(pattern.text),
            "operator": pattern.attrib["operator"],
        }

    def parse_attribute_pattern(self, pattern):
        """Parses <attribute> pattern
        """
        self.func_to_call = "analyze_attribute"
        self.params = {
            "attribute_name": clean(pattern.text),
        }

    def parse_function_call_pattern(self, pattern):
        """Parses <function_call> pattern
        """
        self.func_to_call = "analyze_function_call"

        name_tag = pattern.find("name")

        if (name_tag is not None):
            self.params = {
                "function_name": clean(name_tag.text),
                "operator": name_tag.attrib["operator"],
            }

    def parse_function_call_without_arg_pattern(self, pattern):
        """Parses <function_call_without_arg> pattern
        """
        self.func_to_call = "analyze_function_call_without_arg"

        name_tag = pattern.find("name")
        param_tag = pattern.find("param")

        if (name_tag is not None and param_tag is not None):
            self.params = {
                "function_name": clean(name_tag.text),
                "function_name_operator": name_tag.attrib["operator"],
                "param_name": clean(param_tag.attrib["name"]),
                "param_pos": int(clean(param_tag.attrib["pos"])),
            }

    def parse_function_call_with_arg_pattern(self, pattern):
        """Parses <function_call_with_arg> pattern
        """
        self.func_to_call = "analyze_function_call_with_arg"

        name_tag = pattern.find("name")
        param_tag = pattern.find("param")

        if (name_tag is not None and param_tag is not None):
            # <param> contains ONLY one sub-element with a value type
            # extracting it
            value_type = list(param_tag).pop()
            param_operator, param_value = self.extract_operator_and_value(value_type)

            if (param_operator is not None and param_value is not None):
                self.params = {
                    "function_name": clean(name_tag.text),
                    "function_name_operator": name_tag.attrib["operator"],
                    "param_name": clean(param_tag.attrib["name"]),
                    "param_pos": int(clean(param_tag.attrib["pos"])),
                    "param_operator": param_operator,
                    "param_value": param_value,
                }

    def parse_assignment_var_pattern(self, pattern):
        """Parses <assignment_var> pattern
        """
        self.func_to_call = "analyze_assignment_var"

        name_tag = pattern.find("name")
        value_tag = pattern.find("value")

        if (name_tag is not None and value_tag is not None):
            # <value> contains ONLY one sub-element with a value type
            # extracting it
            value_type = list(value_tag).pop()
            value_operator, value_itself = self.extract_operator_and_value(value_type)

            if (value_operator is not None and value_itself is not None):
                # "name" can be empty - it is a correct value when "name_operator"
                # equals "contains", because every "name" contains nothing (empty string - "")
                self.params = {
                    "name": "" if name_tag.text is None else clean(name_tag.text),
                    "name_operator": name_tag.attrib["operator"],
                    "value": value_itself,
                    "value_operator": value_operator,
                }

    def parse_assignment_in_dict_pattern(self, pattern):
        """Parses <assignment_in_dict> pattern
        """
        self.func_to_call = "analyze_assignment_in_dict"

        name_tag = pattern.find("name")
        key_tag = pattern.find("key")
        value_tag = pattern.find("value")

        if (name_tag is not None and key_tag is not None and value_tag is not None):
            # <value> contains ONLY one sub-element with a value type
            # extracting it
            value_type = list(value_tag).pop()
            value_operator, value_itself = self.extract_operator_and_value(value_type)

            if (value_operator is not None and value_itself is not None):
                # "name" and "key" can be empty - it is a correct value when "name_operator"
                # and "key_operator" are equal "contains", because every "name" or "key"
                # contains nothing (empty string - "")
                self.params = {
                    "name": "" if name_tag.text is None else clean(name_tag.text),
                    "name_operator": name_tag.attrib["operator"],
                    "key": "" if key_tag.text is None else clean(key_tag.text),
                    "key_operator": key_tag.attrib["operator"],
                    "value": value_itself,
                    "value_operator": value_operator,
                }

    def parse_unique_assignment_to_set_tuple_list_pattern(self, pattern):
        """Parses <unique_assignment_to_set_tuple_list> pattern
        """
        self.func_to_call = "analyze_unique_assignment_to_set_tuple_list"

        name_tag = pattern.find("name")
        values_tag = pattern.find("values")

        if (name_tag is not None and values_tag is not None):
            # "name" can be empty - it is a correct value when "name_operator"
            # equals "contains", because every "name" contains nothing (empty string - "")
            self.params = {
                "name": "" if name_tag.text is None else clean(name_tag.text),
                "name_operator": name_tag.attrib["operator"],
                # process <value> tags from the <values> tag
                "values": [clean(value_tag.text) for value_tag in list(values_tag)],
                "values_operator": values_tag.attrib["operator"],
            }

    def extract_operator_and_value(self, value_type):
        """Extracts operator and value from specific value type
        """
        operator, value = None, None

        if (value_type.tag == "str"):
            operator = value_type.attrib["operator"]
            # value_type.text is None when tag has no text
            extracted_value = "" if value_type.text is None else clean(value_type.text)
            # convert value into ast.Constant
            value = Constant(value=extracted_value)
        elif (value_type.tag == "int"):
            operator = value_type.attrib["operator"]
            extracted_value = int(clean(value_type.text))
            value = Constant(value=extracted_value)
        elif (value_type.tag == "bool"):
            operator = value_type.attrib["operator"]
            # bool value, according to .xsd-schema, can be only "True" or "False"
            extracted_value = True if clean(value_type.text) == "True" else False
            value = Constant(value=extracted_value)
        elif (value_type.tag == "none"):
            operator = value_type.attrib["operator"]
            value = Constant(value=None)
        elif (value_type.tag == "constant"):
            operator = value_type.attrib["operator"]
            # pass the ast.Constant type itself as a result
            value = Constant
        elif (value_type.tag == "attr"):
            operator = value_type.attrib["operator"]
            extracted_value = clean(value_type.text)
            # we convert ast.Attribute nodes in analyzer.py into string like this:
            # Attribute(value=Name(id='snake', ctx=Load()), attr='colour', ctx=Load()) => "snake.colour"
            # so here we are creating ast.Attribute with a "converted" value (are not recreating Name(...))
            value = Attribute(value=extracted_value)
        elif (value_type.tag == "function_call"):
            # support only "eq" operator for now
            operator = "eq"
            extracted_value = clean(value_type.text)
            # we convert function name in ast.Call nodes in analyzer.py into string like in example above
            # that is why we are creating ast.Call with a "converted" func name (are not recreating Name(...))
            value = Call(func=extracted_value)

        return (operator, value)

    @property
    def is_valid(self):
        """Checks if the pattern itself has all the required attributes set
        """
        result = False

        if (self.func_to_call and self.params):
            result = True

        return result


def clean(value):
    """Wrapper for str.strip() function
    """
    return value.strip()
