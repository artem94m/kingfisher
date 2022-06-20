<p align="center">
    <img src="https://raw.githubusercontent.com/artem94m/kingfisher/main/static/images/kingfisher_logo.png" alt="Kingfisher" title="Kingfisher" width="800"/>
</p>

## About
Kingfisher is a simple Python 3 static code analyzer. It uses Python built-in modules "ast" and "tokenize" to parse and process source code.

## Requirements
1. Windows/Linux OS
2. Python 3.8 or newer
3. Installed modules:
    - xmlschema (https://pypi.org/project/xmlschema/)
    - defusedxml (https://pypi.org/project/defusedxml/)
    - reportlab (https://pypi.org/project/reportlab/)

## Installation
1. Install software and modules described above
2. Extract "kingfisher-main" folder wherever you want

## Usage
1. Change current directory to "kingfisher-main"
2. Run "python kingfisher.py" to get info about usage. It will print something like this:
    
    ```
    usage: kingfisher.py [-h] -scan SCAN_PATH [-report_folder REPORT_PATH] [-project PROJECT_NAME]

    Kingfisher - Python 3 Simple Static Code Analyzer

    optional arguments:
        -h, --help            show this help message and exit
        -scan SCAN_PATH       the path to a file/folder for scanning
        -report_folder REPORT_PATH
                              the path to a reports folder (default: reports)
        -project PROJECT_NAME
                              name of the scanned project (default: will be extracted from a file or folder name)
    ```

3. As you can see, there is only one required argument - SCAN_PATH. It can be a relative or an absolute path to a project folder or a project file. 

   You can run test scan (demo files in local folder: kingfisher-main\data\tests) like this: 

    ```
    python kingfisher.py -scan tests
    ```

   If you want to scan just one file:

    ```
    python kingfisher.py -scan C:\tests\example.py
    ```

   or

    ```
    python kingfisher.py -scan /var/www/example.py
    ```

   Or a folder:

    ```
    python kingfisher.py -scan C:\tests\project
    ```

   or

    ```
    python kingfisher.py -scan /var/www/project
    ```

4. If REPORT_PATH is not specified, the results of the scan will be saved in local report folder: kingfisher-main\reports. Reports are generated in PDF format. Example of report file with results of scanning of local "tests" folder is placed in kingfisher-main\reports folder.

5. If PROJECT_NAME is not specified, the filename of a report will contain name of the scanned folder or file. The filename of a report will also contain a timestamp (YYYY-mm-dd_HH-MM-SS) when the report was generated.

6. Information about scanning will be printed in the console and also saved in local logs folder (kingfisher-main\logs). Log files are created for every day separately.

## Checks
All available checks are stored in XML-format in a local folder: kingfisher-main\checks. Their content partly was taken from the website https://vulncat.fortify.com/en/weakness.

Before every scanning all the checks from the folder go through validation against a schema (kingfisher-main\data\check_schema.xsd). If check did not pass the validation process - it will be ignored during scanning.

You can add new checks or edit existing ones according to the schema.

Every check contains main tag `<check>` with an attribute "status". "Status" can have only two values: "enabled" and "disabled". This status enables/disables check for scanning.

In `<check>` tag there are next tags: `<name>`, `<description>`, `<explanation>`, `<severity>`, `<recommendations>`, `<links>`, `<patterns>`.

Tag `<name>` and `<description>` are self-descriptive and contains just one paragraph of text.

> **_NOTE:_**  The `<name>` tag must be unique for every check!

Tag `<explanation>` contains more detailed description of the vulnerability, sometimes with examples of vulnerable code. For correct generation of reports paragraphs inside `<explanation>` should be separated by double new line (\n\n):

```
Command injection vulnerabilities take two forms:

- An attacker can change the command that the program executes: the attacker explicitly controls what the command is.

- An attacker can change the environment in which the command executes: the attacker implicitly controls what the command means.
```

Examples of code also should be separated other paragraphs by double new line (\n\n) and prepended by keyword KF_CODE_EXAMPLE:

```
KF_CODE_EXAMPLE
...
home = os.getenv('APPHOME')
cmd = home.join(INITCMD)
os.system(cmd)
...
do_something()
```

You can use "..." to fill the gaps in the code.

Tag `<severity>` is also self-descriptive and can contain only one of four values: High, Medium, Low, Info. This value is set according to CWE (from `<links>`), if possible.

Tag `<recommendations>` is also self-descriptive and for correct generation of report recommendations in it should be separated by one new line (\n).

Tag `<links>` contains links to the different standarts. Links should be separated by one new line (\n).

Tag `<patterns>` contains patterns for recognition of the vulnerability. More details about this tag are placed below.

## Patterns
Tag `<patterns>` is the most interesting one. It supports only one tag `<pattern_simple>` and must contain at least one. This tag is used for description of simple checks.

Tag `<pattern_simple>` must contain only one of next tags: `<comment>`, `<string>`, `<block>`, `<attribute>`, `<function_call>`, `<function_call_without_arg>`, `<function_call_with_arg>`, `<assignment_var>`, `<assignment_in_dict>`, `<unique_assignment_to_set_tuple_list>`.

### Tag `<comment>`
Tag `<comment>` is used to find specific text (case-insensitive) in the comments. The tag must contain non empty string. Pattern below will trigger if there is "password" phrase (case-insensitive) in the comments in source code (probably password in comments):

```
<pattern_simple>
    <comment>password</comment>
</pattern_simple>
```

### Tag `<string>`
    
Tag `<string>` is used to find specific text in string literals in the code. It also has one required attribute "operator" which determines type of search: 
 - eq (trigger if a string literal equals to specific text)
 - contains (trigger if a string literal contains specific text)
 - starts (trigger if a string literal starts from specific text)

Pattern below will trigger if in code there is string literal which is equal to "\\" (probably hardcoded file separator):
```
<pattern_simple>
    <string operator="eq">\</string>
</pattern_simple>
```

Pattern below will trigger if in code there is string literal which starts from "http://" (probably unencrypted connection):
```
<pattern_simple>
    <string operator="starts">http://</string>
</pattern_simple>
```

Pattern below will trigger if in code there is string literal which contains "pwd=" (probably hardcoded password):
```
<pattern_simple>
    <string operator="contains">pwd=</string>
</pattern_simple>
```

### Tag `<block>`

Tag `<block>` is used to find specific block in the source code. It has one required attribute "operator" which must be equal "empty". This tag must contain non-empty string which is a name of the block. It supports only two values: except and def. Example below will trigger if there is an empty except block in the source code (definitely empty except block):
```
<pattern_simple>
    <block operator="empty">except</block>
</pattern_simple>
```

### Tag `<attribute>`
Tag `<attribute>` is used to find usage of specific attribute of the module, not the attribute of just created object. You should specify full path to the attribute - with module name and sub-packets. Example below will trigger if Crypto.Cipher.AES.MODE_ECB is used in the code (definitely not safe mode of encryption):
```
<pattern_simple>
    <attribute>Crypto.Cipher.AES.MODE_ECB</attribute>
</pattern_simple>
```

### Tag `<function_call>`

Tag `<function_call>` is used to find call of specific function. Is has to contain only one `<name>` tag which has one required attribute "operator" which determines type of search: 
 - eq (trigger if a function name equals to specific text)
 - contains (trigger if a function name contains specific text)

**NOTE**: You should specify full path to the function - with module name and sub-packets.

Example below trigger if os.system function is used in the code (probably command injection):
```
<pattern_simple>
    <function_call>
        <name operator="eq">os.system</name>
    </function_call>
</pattern_simple>
```
Operator "contains" allows to find not complete match, like call of method of object. Example below will trigger if function name contains "unsafe" substring (probably usage of unsafe method):
```
<pattern_simple>
    <function_call>
        <name operator="contains">unsafe</name>
    </function_call>
</pattern_simple>
```

### Tag `<function_call_without_arg>`

Tag `<function_call_without_arg>` is used to find call of function WITHOUT specific argument. It contains only two tags added one by one: `<name>` and `<param>`. 

Tag `<name>` describes function name - it works exactly the same like in `<function_call>` tag (see above). 

Tag `<param>` has two required attributes: name and pos (position, starting from 1). They are self-descriptive. If position of an argument can be any set is as "-1", but the name must be specified. If you know the position but not name - set "-1" as name, but specify the position. 

Example below will trigger if method "set_cookie" was called without "httponly" argument (see https://docs.djangoproject.com/en/3.2/ref/request-response/#django.http.HttpResponse.set_cookie):
```    
<pattern_simple>
    <function_call_without_arg>
        <name operator="contains">.set_cookie</name>
        <param name="httponly" pos="8"/>
    </function_call_without_arg>
</pattern_simple>
```

In next example, position of the argument is not strict, so you have to search absence of an argument by its name:
```
<pattern_simple>
    <function_call_without_arg>
        <name operator="eq">some_function</name>
        <param name="paramname" pos="-1"/>
    </function_call_without_arg>
</pattern_simple>
```

In next example, name of the argument is not strict, so you have to search absence of an argument by its position:
```
<pattern_simple>
    <function_call_without_arg>
        <name operator="eq">some_function</name>
        <param name="-1" pos="2"/>
    </function_call_without_arg>
</pattern_simple>
```

**NOTE**: scanner does not support check against usage of `**kwargs` and `*args` as arguments.


### Tag `<function_call_with_arg>`
Tag `<function_call_with_arg>` is used to find call of function WITH specific argument. It contains only two tags added one by one: `<name>` and `<param>`. 

Tag `<name>` describes function name - it works exactly the same like in `<function_call>` tag (see above). 

Tag `<param>` has two required attributes: name and pos (position, starting from 1). They are self-descriptive. If position of an argument can be any set is as "-1", but the name must be specified. If you know the position but not name - set "-1" as name, but specify the position. 

Tag `<param>` has to contain one of the next tags: `<str>`, `<int>`, `<bool>`, `<none>`, `<attr>`, `<function_call>`, `<constant>`.

#### Tag `<str>`
Tag `<str>` has one attribute "operator" which can have next values:
 - eq (trigger if param value equals specific string)
 - neq (trigger if param value is not equal specific string)
 - contains (trigger if param value contains specific string)
 - starts (trigger if param value start from specific string)
Example:
```
<pattern_simple>
    <function_call_with_arg>
        <name operator="eq">some_func</name>
        <param name="param1" pos="1">
            <str operator="eq">test</str>
        </param>
    </function_call_with_arg>
</pattern_simple>
```

#### Tag `<int>`
Tag `<int>` has one attribute "operator" which can have next values:
 - eq (trigger if param value equals specific integer)
 - neq (trigger if param value is not equal specific integer)
 - gt (trigger if param value greater than specific integer)
 - lt (trigger if param value less than specific integer)
Example:
```
<pattern_simple>
    <function_call_with_arg>
        <name operator="eq">some_func</name>
        <param name="param1" pos="1">
            <int operator="gt">123</int>
        </param>
    </function_call_with_arg>
</pattern_simple>
```

#### Tag `<bool>`
Tag `<bool>` has one attribute "operator" which can have next values:
 - eq (trigger if param value equals specific boolean (can be only True or False))
 - neq (trigger if param value is not equal specific boolean)

Example:
```
<pattern_simple>
    <function_call_with_arg>
        <name operator="eq">some_func</name>
        <param name="param1" pos="1">
            <bool operator="eq">False</bool>
        </param>
    </function_call_with_arg>
</pattern_simple>
```

#### Tag `<none>`
Tag `<none>` (must be empty) has one attribute "operator" which can have next values:
 - is (trigger if param value equals None)
 - not (trigger if param value is not equal None)

Example:
```
<pattern_simple>
    <function_call_with_arg>
        <name operator="eq">some_func</name>
        <param name="param1" pos="1">
            <none operator="is"/>
        </param>
    </function_call_with_arg>
</pattern_simple>
```

#### Tag `<attr>`
Tag `<attr>` (you should specify full path to the attribute of the module - with module name and sub-packets) has one attribute "operator" which can have next values:
 - eq (trigger if param value equals specific attribute of the module or variable name)
 - neq (trigger if param value is not equal attribute of the module or variable name)

Example:
```
<pattern_simple>
    <function_call_with_arg>
        <name operator="eq">some_func</name>
        <param name="param1" pos="1">
            <attr operator="eq">module.attr</attr>
        </param>
    </function_call_with_arg>
</pattern_simple>
```

#### Tag `<function_call>`
Tag `<function_call>` has no attributes but must contain non-empty string which describes name of called function (you should specify full path to the function - with module name and sub-packets)

Example:
```
<pattern_simple>
    <function_call_with_arg>
        <name operator="eq">some_func</name>
        <param name="param1" pos="1">
            <function_call>eval</function_call>
        </param>
    </function_call_with_arg>
</pattern_simple>
```

#### Tag `<constant>`
Tag `<constant>` (must be empty) has one attribute "operator" which can have next values:
 - is (trigger if param value is a constant)
 - not (trigger if param value is NOT a constant)

Constant can be simple types such as a number, string or None, but also immutable container types (tuples and frozensets) if all of their elements are constant.

Example:
```
<pattern_simple>
    <function_call_with_arg>
        <name operator="eq">some_func</name>
        <param name="param1" pos="1">
            <constant operator="is"/>
        </param>
    </function_call_with_arg>
</pattern_simple>
```

**NOTE**: scanner does not support check against usage of chain of assignment.

This code will **NOT** trigger first pattern:
```
var = "'unsafe-eval'"
CSP_DEFAULT_SRC = ("'self'", "'unsafe-inline'", var, 'cdn.example.net')
``` 

This code **WILL** trigger first pattern:
```
CSP_DEFAULT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'", 'cdn.example.net')
```

### Tag `<assignment_var>`

Tag `<assignment_var>` is used to find assignment of specific value to a specific variable. It contains only two tags added one by one: `<name>` and `<value>`. 
Tag `<name>` describes variable name - it works exactly the same like in `<function_call>` tag (see above). 
Tag `<value>` has to contain one of the next tags: `<str>`, `<int>`, `<bool>`, `<none>`, `<attr>`, `<function_call>`, `<constant>` (see details above at `<function_call_with_arg>` tag's description).
Example below will trigger if there is a variable whose name contains substring "password" (case-insensitive) and it was assigned with empty string:
```
<pattern_simple>
    <assignment_var>
        <name operator="contains">password</name>
        <value>
            <str operator="eq"></str>
        </value>
    </assignment_var>
</pattern_simple>
```

### Tag `<assignment_in_dict>`
Tag `<assignment_in_dict>` is used to find assignment of specific value to a specific key of a specific dict. It contains three tags added one by one: `<name>`, `<key>` and `<value>`. 

Tag `<name>` describes dict name - it works exactly the same like in `<function_call>` tag (see above). 

Tag `<key>` describes key in dict. It has one required attribute "operator" which works like the same operator for the `<name>` tag. In source code key must be a string.

Tag `<value>` has to contain one of the next tags: `<str>`, `<int>`, `<bool>`, `<none>`, `<attr>`, `<function_call>`, `<constant>` (see details above at `<function_call_with_arg>` tag's description).

Example below will trigger if there is a dict with any name (every name contains "") which has a key whose name contains substring "password" (case-insensitive) and it was assigned with empty string:
```
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

### Tag `<unique_assignment_to_set_tuple_list>`
Tag `<unique_assignment_to_set_tuple_list>` is used to check if specific unique string values were assigned/missed in a set, tuple or list. This tag contains only two tags added one by one: `<name>` and `<values>`. 

Tag `<name>` describes name - it works exactly the same like in `<function_call>` tag (see above). 

Tag `<values>` has one required attribute "operator", which determines type of search: 
 - contains (trigger if a set, tuple or list contains specific string values)
 - missing (trigger if a set, tuple or list missing specific string values)

Tag `<values>` has to contain at least one tag `<value>` with specified attribute "type" which must be equal "str".
    
Example below will trigger if CSP contains "'unsafe-eval'" string (probably misconfigured Django Content Security Policy):
```
<pattern_simple>
    <unique_assignment_to_set_tuple_list>
        <name operator="contains">csp_</name>
        <values operator="contains">
            <value type="str">'unsafe-eval'</value>
        </values>
    </unique_assignment_to_set_tuple_list>
</pattern_simple>
```

Next example will trigger if MIDDLEWARE collection does not have specific middleware class(probably, disabled Django Clickjacking Protection):
```
<pattern_simple>
    <unique_assignment_to_set_tuple_list>
        <name operator="contains">middleware</name>
        <values operator="missing">
            <value type="str">django.middleware.clickjacking.XFrameOptionsMiddleware</value>
        </values>
    </unique_assignment_to_set_tuple_list>
</pattern_simple>
```

For more examples look in kingfisher-main/check folder. Exact `<patterns>` tag's structure see in kingfisher-main/data/check_schema.xsd