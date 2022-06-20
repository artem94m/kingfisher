# Checks syntax

## Tag `<check>`
Every check contains main tag `<check>` with an attribute `status`. The `status` attribute can have only one of two values: `enabled` and `disabled`. This status enables/disables check for the scanning.

Inner tags of the `<check>` tag: `<name>`, `<description>`, `<explanation>`, `<severity>`, `<recommendations>`, `<links>`, `<patterns>`.

Tag `<name>` and `<description>` are self-descriptive and contain just one paragraph of text.

**NOTE:**  The value of the `<name>` tag must be unique for every check! If two checks have the same name, the later will be discarded.

Tag `<explanation>` contains more detailed description of the vulnerability, sometimes with examples of vulnerable code. For correct generation of reports, paragraphs inside `<explanation>` tag should be separated by double new line (`\n\n`):

```text
Command injection vulnerabilities take two forms:

- An attacker can change the command that the program executes: the attacker explicitly controls what the command is.

- An attacker can change the environment in which the command executes: the attacker implicitly controls what the command means.
```

Examples of code also should be separated from other paragraphs and code examples by double new line (`\n\n`) and prepended by the keyword `KF_CODE_EXAMPLE`:

```python
KF_CODE_EXAMPLE
...
home = os.getenv('APPHOME')
cmd = home.join(INITCMD)
os.system(cmd)
...
do_something()
```

You can use `...` to fill the gaps in the code examples.

Tag `<severity>` is also self-descriptive and can contain only one of the four values: `High`, `Medium`, `Low`, `Info`. In default checks this value is set according to CWEs, mentioned in the `<links>` tag.

Tag `<recommendations>` is also self-descriptive. For correct generation of report every recommendation in it should be separated from others by one new line (`\n`).

Tag `<links>` contains links to the different sources, which proves the severity of the check. Every link also should be separated from others by one new line (`\n`).

Tag `<patterns>` contains patterns for recognition of the vulnerability. More details about this tag are placed below.

## Inner tag `<patterns>`
Tag `<patterns>` is the most interesting one. It supports only one inner tag `<pattern_simple>` and must contain at least one. This tag is used for description of the vulnerable code.

Tag `<pattern_simple>` must contain only one of next pattern tags: `<comment>`, `<string>`, `<block>`, `<attribute>`, `<function_call>`, `<function_call_without_arg>`, `<function_call_with_arg>`, `<assignment_var>`, `<assignment_in_dict>`, `<unique_assignment_to_set_tuple_list>`.

### Pattern tag `<comment>`
Tag `<comment>` is used to find the specific text (case-insensitive) in the comments. The tag must contain non-empty string. 

Pattern below will trigger if there is "password" phrase (case-insensitive) in the comments in source code:
```xml
<pattern_simple>
    <comment>password</comment>
</pattern_simple>
```

### Pattern tag `<string>`
    
Tag `<string>` is used to find the specific text in string literals in the code. It has one required attribute `operator` which determines type of search: 
 - `eq` (trigger if a string literal equals to the specific text)
 - `contains` (trigger if a string literal contains the specific text)
 - `starts` (trigger if a string literal starts from the specific text)

Pattern below will trigger if in code there is a string literal which is equal to `\` (hardcoded file separator):
```xml
<pattern_simple>
    <string operator="eq">\</string>
</pattern_simple>
```

Pattern below will trigger if in code there is a string literal which starts from `http://` (unencrypted connection):
```xml
<pattern_simple>
    <string operator="starts">http://</string>
</pattern_simple>
```

Pattern below will trigger if in code there is string a literal which contains `pwd=` (hardcoded password):
```xml
<pattern_simple>
    <string operator="contains">pwd=</string>
</pattern_simple>
```

### Pattern tag `<block>`

Tag `<block>` is used to find the specific block in the source code. It has one required attribute `operator` which must be equal `empty` (checks if the block is empty). This tag must contain a non-empty string which is a name of the block. It supports only two values: `except`(exception block) and `def`(declaration of a function).

Example below will trigger if there is an empty except block in the source code (empty except block):
```xml
<pattern_simple>
    <block operator="empty">except</block>
</pattern_simple>
```

### Pattern tag `<attribute>`
Tag `<attribute>` is used to find usage of the specific attribute of the module. You should specify full path to the attribute (non-empty string) - with module name and sub-packets.

Example below will trigger if `Crypto.Cipher.AES.MODE_ECB` is used in the code (not safe mode of encryption):
```xml
<pattern_simple>
    <attribute>Crypto.Cipher.AES.MODE_ECB</attribute>
</pattern_simple>
```

### Pattern tag `<function_call>`
(function_call/name)=
Tag `<function_call>` is used to find the call of the specific function. Is has to contain only one `<name>` tag which has one required attribute `operator` which determines type of search: 
 - `eq` (trigger if a function name equals to the specific text)
 - `contains` (trigger if a function name contains the specific text)

**NOTE:** You should specify full path to the function - with module name and sub-packets.

Example below trigger if `os.system` function is used in the code (command injection):
```xml
<pattern_simple>
    <function_call>
        <name operator="eq">os.system</name>
    </function_call>
</pattern_simple>
```

Operator `contains` allows to find not complete match, like call of method of object. Example below will trigger if the function name contains "unsafe" substring (probably usage of unsafe method):
```xml
<pattern_simple>
    <function_call>
        <name operator="contains">unsafe</name>
    </function_call>
</pattern_simple>
```

### Pattern tag `<function_call_without_arg>`

Tag `<function_call_without_arg>` is used to find the call of function **WITHOUT** the specific argument. It contains only two tags added one by one: `<name>` and `<param>`. 

Tag `<name>` describes function name - it works exactly the same like in `<function_call>` tag ([see above](function_call/name)). 

Tag `<param>` has two required attributes: `name` and `pos` (position, starting from 1). They are self-descriptive. 

If the position of an argument can be any - set is as `-1`, but the `name` must be specified then. 

If you know the position of the argument, but not the name - use `-1` as name, but specify the `pos` then. 

Example below will trigger if the method [`set_cookie`](https://docs.djangoproject.com/en/3.2/ref/request-response/#django.http.HttpResponse.set_cookie) was called without the `httponly` argument:
```xml
<pattern_simple>
    <function_call_without_arg>
        <name operator="contains">.set_cookie</name>
        <param name="httponly" pos="8"/>
    </function_call_without_arg>
</pattern_simple>
```

In the next example, the position of the argument is not strict, so you have to search absence of an argument by it's name:
```xml
<pattern_simple>
    <function_call_without_arg>
        <name operator="eq">some_function</name>
        <param name="paramname" pos="-1"/>
    </function_call_without_arg>
</pattern_simple>
```

In the next example, the name of the argument is not strict, so you have to search absence of an argument by it's position:
```xml
<pattern_simple>
    <function_call_without_arg>
        <name operator="eq">some_function</name>
        <param name="-1" pos="2"/>
    </function_call_without_arg>
</pattern_simple>
```

**NOTE:** scanner does not support check against usage of `**kwargs` and `*args` as arguments.

### Pattern tag `<function_call_with_arg>`
Tag `<function_call_with_arg>` is used to find the call of the function `WITH` the specific argument. It contains only two tags added one by one: `<name>` and `<param>`. 

Tag `<name>` describes the function name - it works exactly the same like in `<function_call>` tag ([see above](function_call/name)). 

Tag `<param>` has two required attributes: `name` and `pos` (position, starting from 1). They are self-descriptive. 

If the position of an argument can be any - set is as `-1`, but the `name` must be specified then. 

If you know the position of the argument, but not the name - use `-1` as name, but specify the `pos` then. 

Tag `<param>` has to contain one of the [value tags](value_tags).

### Pattern tag `<assignment_var>`
Tag `<assignment_var>` is used to find the assignment of the specific value to the specific variable. It contains only two tags added one by one: `<name>` and `<value>`. 

Tag `<name>` describes variable name - it works exactly the same like in `<function_call>` tag ([see above](function_call/name)). 

Tag `<value>` has to contain one of the [value tags](value_tags).

Example below will trigger if there is a variable whose name contains substring `password` (case-insensitive) and it was assigned with empty string (empty password):
```xml
<pattern_simple>
    <assignment_var>
        <name operator="contains">password</name>
        <value>
            <str operator="eq"></str>
        </value>
    </assignment_var>
</pattern_simple>
```

### Pattern tag `<assignment_in_dict>`
Tag `<assignment_in_dict>` is used to find the assignment of the specific value to a specific key of a specific dict. It contains three tags added one by one: `<name>`, `<key>` and `<value>`. 

Tag `<name>` describes dict name - it works exactly the same like in `<function_call>` tag ([see above](function_call/name)). 

Tag `<key>` describes key in dict. It has one required attribute `operator` which works like the same operator for the `<name>` tag([see above](function_call/name)). In source code key must be a string.

Tag `<value>` has to contain one of the [value tags](value_tags).

Example below will trigger if there is a dict with any name (every name contains empty string `""`) which has a key whose name contains substring `password` (case-insensitive) and it was assigned with an empty string:
```xml
<pattern_simple>
    <assignment_in_dict>
        <name operator="contains"></name>
        <key operator="contains">password</key>
        <value>
            <str operator="eq"></str>
        </value>
    </assignment_in_dict>
</pattern_simple>
```

### Pattern tag `<unique_assignment_to_set_tuple_list>`
Tag `<unique_assignment_to_set_tuple_list>` is used to check if the specific unique string values were assigned/missed in a set, tuple or list. This tag contains only two tags added one by one: `<name>` and `<values>`. 

Tag `<name>` describes name - it works exactly the same like in `<function_call>` tag ([see above](function_call/name)).

Tag `<values>` has one required attribute `operator`, which determines type of search: 
 - `contains` (trigger if a set, tuple or list contains the specific string values)
 - `missing` (trigger if a set, tuple or list missing the specific string values)

Tag `<values>` has to contain at least one tag `<value>` with specified attribute `type` which must be equal `str`.
    
Example below will trigger if `CSP` contains `'unsafe-eval'` string (probably misconfigured Django Content Security Policy):
```xml
<pattern_simple>
    <unique_assignment_to_set_tuple_list>
        <name operator="contains">csp_</name>
        <values operator="contains">
            <value type="str">'unsafe-eval'</value>
        </values>
    </unique_assignment_to_set_tuple_list>
</pattern_simple>
```

**NOTE:** scanner does not support check against usage of chain of assignment.

This code will **NOT** trigger the pattern:
```python
var = "'unsafe-eval'"
CSP_DEFAULT_SRC = ("'self'", "'unsafe-inline'", var, 'cdn.example.net')
``` 

This code **WILL** trigger the pattern:
```python
CSP_DEFAULT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'", 'cdn.example.net')
```

The next example will trigger if `MIDDLEWARE` collection does not have the specific middleware class(probably disabled Django Clickjacking Protection):
```xml
<pattern_simple>
    <unique_assignment_to_set_tuple_list>
        <name operator="contains">middleware</name>
        <values operator="missing">
            <value type="str">django.middleware.clickjacking.XFrameOptionsMiddleware</value>
        </values>
    </unique_assignment_to_set_tuple_list>
</pattern_simple>
```

For more examples look in **kingfisher-main/checks/default** folder. 

The exact `<check>` tag's structure see in **kingfisher-main/checks/valid_check_schema.xsd**.

(value_tags)=
## Value tags
The value tags are : `<str>`, `<int>`, `<bool>`, `<none>`, `<attr>`, `<function_call>`, `<constant>`.

### Value tag `<str>`
Tag `<str>` has one attribute `operator` which can have the next values:
 - `eq` (trigger if the param value equals the specific string)
 - `neq` (trigger if the param value is not equal the specific string)
 - `contains` (trigger if the param value contains the specific string)
 - `starts` (trigger if the param value start from the specific string)

Example:
```xml
<pattern_simple>
    <function_call_with_arg>
        <name operator="eq">some_func</name>
        <param name="param1" pos="1">
            <str operator="eq">test</str>
        </param>
    </function_call_with_arg>
</pattern_simple>
```

### Value tag `<int>`
Tag `<int>` has one attribute `operator` which can have the next values:
 - `eq` (trigger if the param value equals the specific integer)
 - `neq` (trigger if the param value is not equal the specific integer)
 - `gt` (trigger if the param value greater than the specific integer)
 - `lt` (trigger if the param value less than the specific integer)

Example:
```xml
<pattern_simple>
    <function_call_with_arg>
        <name operator="eq">some_func</name>
        <param name="param1" pos="1">
            <int operator="gt">123</int>
        </param>
    </function_call_with_arg>
</pattern_simple>
```

### Value tag `<bool>`
Tag `<bool>` has one attribute `operator` which can have the next values:
 - `eq` (trigger if the param value equals the specific boolean (can be only `True` or `False`))
 - `neq` (trigger if the param value is not equal the specific boolean)

Example:
```xml
<pattern_simple>
    <function_call_with_arg>
        <name operator="eq">some_func</name>
        <param name="param1" pos="1">
            <bool operator="eq">False</bool>
        </param>
    </function_call_with_arg>
</pattern_simple>
```

### Value tag `<none>`
Tag `<none>` (must be empty) has one attribute `operator` which can have the next values:
 - `is` (trigger if the param value equals `None`)
 - `not` (trigger if the param value is not equal `None`)

Example:
```xml
<pattern_simple>
    <function_call_with_arg>
        <name operator="eq">some_func</name>
        <param name="param1" pos="1">
            <none operator="is"/>
        </param>
    </function_call_with_arg>
</pattern_simple>
```

### Value tag `<attr>`
Tag `<attr>` (you should specify full path to the attribute of the module - with module name and sub-packets) has one attribute `operator` which can have the next values:
 - `eq` (trigger if the param value equals the specific attribute of the module or variable name)
 - `neq` (trigger if the param value is not equal the specific attribute of the module or variable name)

Example:
```xml
<pattern_simple>
    <function_call_with_arg>
        <name operator="eq">some_func</name>
        <param name="param1" pos="1">
            <attr operator="eq">module.attr</attr>
        </param>
    </function_call_with_arg>
</pattern_simple>
```

### Value tag `<function_call>`
Tag `<function_call>` has no attributes, but must contain non-empty string which describes the name of the called function (you should specify full path to the function - with module name and sub-packets).

Example:
```xml
<pattern_simple>
    <function_call_with_arg>
        <name operator="eq">some_func</name>
        <param name="param1" pos="1">
            <function_call>eval</function_call>
        </param>
    </function_call_with_arg>
</pattern_simple>
```

### Value tag `<constant>`
Tag `<constant>` (must be empty) has one attribute `operator` which can have the next values:
 - `is` (trigger if the param value is a constant)
 - `not` (trigger if the param value is **NOT** a constant)

Constant can contain simple types (`int`, `str`, `None`, `bool` and also immutable container types (`tuple` and `frozenset`) if all of their elements are constants.

Example:
```xml
<pattern_simple>
    <function_call_with_arg>
        <name operator="eq">some_func</name>
        <param name="param1" pos="1">
            <constant operator="is"/>
        </param>
    </function_call_with_arg>
</pattern_simple>
```
