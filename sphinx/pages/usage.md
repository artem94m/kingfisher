# Usage

## Run a scan
1. Go to **kingfisher-main** directory
2. Run `python kingfisher.py` to get info about usage. It will print something like this:
    
    ```text
    usage: kingfisher.py [-h] -scan_path SCAN_PATH [-reports_path REPORTS_PATH] [-project PROJECT] [-v]

    Kingfisher - Python 3 Simple Static Code Analyzer

    optional arguments:
    -h, --help                   show this help message and exit
    -scan_path SCAN_PATH         path to a file/folder for scanning
    -reports_path REPORTS_PATH   path to store the report (default: kingfisher-main/reports)
    -project PROJECT             project name must comply next regex: r'[a-zA-Z0-9_.-]{1,50}' (default: will be extracted from SCAN_PATH)
    -v                           enable verbose mode
    ```

3. As you can see, there is only one required argument - `SCAN_PATH`. It can be a relative or an absolute path to a project folder or a project file. 

   You can run test scan (demo files are placed in the local folder: **kingfisher-main/code_with_vulns**) like this: 

    ```text
    python kingfisher.py -scan_path code_with_vulns
    ```

   If you want to scan just one file:

    ```text
    python kingfisher.py -scan_path C:\tests\example.py
    ```

   or

    ```text
    python kingfisher.py -scan_path /var/www/example.py
    ```

   Or a folder:

    ```text
    python kingfisher.py -scan_path C:\tests\project
    ```

   or

    ```text
    python kingfisher.py -scan_path /var/www/project
    ```

4. If `REPORTS_PATH` is not specified, by default, the results of the scan will be saved in PDF-file in the local folder: **kingfisher-main/reports**. Example of the report file with the results of scanning of the local **code_with_vulns** folder is placed in the folder.

5. If `PROJECT` is not specified, the name of the project will be extracted from `SCAN_PATH` (name of the file or folder). The filename of a report will also contain a timestamp (YYYY-mm-dd_HH-MM-SS) when the scan has started.

## Log files
Information about the scanning process will be printed into the console output and also saved in the local logs folder (**kingfisher-main/logs**). Log files are created for every day separately. Parameter `store_logs_for` in **config.py** controls how long log-files should be preserved.

## Adding/editing checks
You also can add new or edit existing checks. The default checks are placed in **kingfisher-main/checks/default** folder, custom ones should be placed in **kingfisher-main/checks/custom** folder.

The **kingfisher-main/checks/default** folder contains checks, which are partly based on the checks for Python from the website [Fortify Taxonomy](https://vulncat.fortify.com/en/weakness).

Every check is an .xml-file which is valid according to the **kingfisher-main/checks/valid_check_schema.xsd** schema and it's name starts with the `check_` substring. 
If any check did not pass the validation process - it will be ignored during the scanning.

During the first scan, checks from the both folder will be cached (**kingfisher-main/checks/default_cache** and **kingfisher-main/checks/custom_cache** folders) for better performance during next scans.

Syntax of checks is described [here](checks).
