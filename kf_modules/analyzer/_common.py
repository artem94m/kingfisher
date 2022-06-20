from ast import Attribute, Call, Constant, Name


def process_attributes_chain(node):
    """Goes recursively through a nested Attribute node (a.b.c.d.e.f)

        Supports only Attribute and Name nested nodes.
        If a different type of node found - returns None.
        Otherwise returns one string: "a.b.c.d.e.f".
    """
    full_attr = None
    parts_of_chain = []

    processed = False
    while (not processed):
        # ast.Attribute contains "value" (can be another node) and "attr" (name of the current node)
        if (isinstance(node, Attribute)):
            # add current node id to the chain
            parts_of_chain.append(node.attr)
            # go to the next nested node to process
            node = node.value
        # other types of nested nodes
        else:
            # ast.Name is the last in the chain and contains only id
            if (isinstance(node, Name)):
                parts_of_chain.append(node.id)
            # found something unusual - node is not a chain of Attribute instances - clear collected parts
            else:
                parts_of_chain.clear()
            # stop the processing
            processed = True

    # if chain was parsed correctly
    if (parts_of_chain):
        # reverse parts (we have collected them starting from the last) and join by dots
        full_attr = ".".join(reversed(parts_of_chain))

    return full_attr


def is_obj_equal_target(obj, target, aliases):
    """Checks if the object is equal to the target according to the aliases

    The 1st scenario: if exactly the same object was used
        Example of code:
            import Crypto
            ...
            <Usage of Crypto.Cipher.AES.MODE_ECB>
            ...
        Vulnerable attribute:
            Crypto.Cipher.AES.MODE_ECB
        Solution:
            Compare obj and target

    The 2nd scenario: if exactly the same object was used by it's alias
        Example of code:
            from Crypto.Cipher.AES import MODE_ECB as mode
            ...
            <Usage of mode>
            ...
        Vulnerable attribute:
            Crypto.Cipher.AES.MODE_ECB
        Solution:
            The "aliases" dict contains next key/value (alias/original_obj): "mode" => "Crypto.Cipher.AES.MODE_ECB"
            Get original_obj of the obj by alias and compare it with the target

    The 3rd scenario: if used object is an obj's attribute
        Example of code:
            from Crypto.Cipher import AES
            ...
            <Usage of AES.MODE_ECB>
            ...
        Vulnerable attribute:
            Crypto.Cipher.AES.MODE_ECB
        Solution:
            The "aliases" dict contains next key/value (alias/original_obj): "AES" => "Crypto.Cipher.AES"
            1. Split obj by dot into alias and rest_of_obj
            2. Search alias in aliases
            3. If it is there:
                1. Replace alias with the original_obj
                2. Compare original_obj.rest_of_obj with the target
    """
    result = False

    if (isinstance(obj, str) and isinstance(target, str)):
        # the 1st scenario
        if (obj == target):
            result = True
        # the 2nd scenario
        elif (obj in aliases and aliases[obj] == target):
            result = True
        # the 3rd scenario
        elif (obj.find(".") != -1):
            # split the object into the alias of imported object and rest part
            alias, rest_of_object = obj.split(".", 1)

            # check if there is such an alias
            if (alias in aliases):
                # replace it with a real path and construct full object
                original_obj = aliases[alias]
                full_obj = ".".join([original_obj, rest_of_object])

                if (full_obj == target):
                    result = True

    return result


def is_obj_fit_target(obj, operator, target, aliases):
    """Checks if the obj fit the target:
            obj <operator> target == True
    """
    result = False

    if (isinstance(obj, str) and isinstance(target, str)):
        if (operator == "eq" and is_obj_equal_target(obj, target, aliases)):
            result = True
        elif (operator == "neq" and not is_obj_equal_target(obj, target, aliases)):
            result = True
        # if name contains specific value (case-insensitive)
        elif (operator == "contains"):
            obj_low = obj.lower()
            target_low = target.lower()

            if (obj_low.find(target_low) != -1):
                result = True

    return result


class IsObjValueMeetConditions():
    """Class to check if the obj value fits the expected object:
            obj <operator> exp_value == True
    """
    def __init__(self, obj, operator, expected_obj, aliases):
        self.result = False

        # "is" and "not" operators are special
        # they work only with <none> and <constant> tags
        # so process them separately
        if (operator == "is"):
            self.result = self.process_is_operator(obj, expected_obj)
        elif (operator == "not"):
            self.result = self.process_not_operator(obj, expected_obj)
        else:
            if (isinstance(obj, Constant) and isinstance(expected_obj, Constant)):
                self.result = self.process_constants_comparison(obj, operator, expected_obj)
            elif (isinstance(obj, (Attribute, Name)) and isinstance(expected_obj, Attribute)):
                self.result = self.process_attributes_comparison(obj, operator, expected_obj, aliases)
            elif (isinstance(obj, Call) and isinstance(expected_obj, Call)):
                self.result = self.process_calls_comparison(obj, operator, expected_obj, aliases)

    def process_is_operator(self, obj, expected_obj):
        result = False

        # check if the obj is instance of expected_obj type
        # expected_obj can be only Constant type
        if (isinstance(expected_obj, type)):
            expected_type = expected_obj
            if (isinstance(obj, expected_type)):
                result = True
        # compare two None values
        elif (isinstance(obj, Constant) and obj.value is None and
                isinstance(expected_obj, Constant) and expected_obj.value is None):
            result = True

        return result

    def process_not_operator(self, obj, expected_obj):
        result = True

        # check if the obj is an instance of expected_obj type
        # expected_obj can be only Constant type
        if (isinstance(expected_obj, type) and isinstance(obj, expected_obj)):
            result = False
        # check if the obj is None
        elif (isinstance(expected_obj, Constant) and expected_obj.value is None and
                isinstance(obj, Constant) and obj.value is None):
            result = False

        return result

    def process_constants_comparison(self, obj, operator, expected_obj):
        result = False

        # obj can be str or bytes, but expected_obj can be only str
        # (case-insensitive operations)
        if (isinstance(obj.value, (str, bytes)) and isinstance(expected_obj.value, str)):
            # prepare obj and expected_obj for comparison
            if (isinstance(obj.value, bytes)):
                # both are lowercased bytes
                object_value_low = obj.value.lower()
                expected_value_low = expected_obj.value.encode(encoding="utf-8").lower()
            else:
                # both are lowercased strings
                object_value_low = obj.value.lower()
                expected_value_low = expected_obj.value.lower()

            if ((operator == "contains" and object_value_low.find(expected_value_low) != -1) or
                    (operator == "eq" and object_value_low == expected_value_low) or
                    (operator == "neq" and object_value_low != expected_value_low) or
                    (operator == "starts" and object_value_low.startswith(expected_value_low))):
                result = True
        # use this type of comparison to avoid: isinstance(True, int) equals "True"
        elif (type(obj.value).__name__ == "int" and type(expected_obj.value).__name__ == "int"):
            if ((operator == "gt" and obj.value > expected_obj.value) or
                    (operator == "lt" and obj.value < expected_obj.value) or
                    (operator == "eq" and obj.value == expected_obj.value) or
                    (operator == "neq" and obj.value != expected_obj.value)):
                result = True
        elif (isinstance(obj.value, bool) and isinstance(expected_obj.value, bool)):
            if ((operator == "eq" and obj.value == expected_obj.value) or
                    (operator == "neq" and obj.value != expected_obj.value)):
                result = True

        return result

    def process_attributes_comparison(self, obj, operator, expected_obj, aliases):
        result = False

        full_obj = process_attributes_chain(obj)

        if (is_obj_equal_target(full_obj, expected_obj.value, aliases)):
            if (operator == "eq"):
                result = True
        else:
            if (operator == "neq"):
                result = True

        return result

    def process_calls_comparison(self, obj, operator, expected_obj, aliases):
        result = False

        full_func = process_attributes_chain(obj.func)

        if (is_obj_equal_target(full_func, expected_obj.func, aliases) and operator == "eq"):
            result = True

        return result
