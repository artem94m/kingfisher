from hashlib import sha1
from os import R_OK, access, getcwd, makedirs, path, scandir
from pickle import dump as pickle_dump, load as pickle_load

from defusedxml import ElementTree as DefusedET

import global_storage

from kf_modules.models.checks import Check, Checks

from xmlschema import XMLSchema


class ChecksParser():
    def __init__(self):
        """Parse checks
        """
        global_storage.logger.info("Collecting checks...")

        folders_with_checks = [
            path.join(getcwd(), "checks", "default"),
            path.join(getcwd(), "checks", "custom"),
        ]

        check_schema_path = path.join(getcwd(), "checks", "valid_check_schema.xsd")

        self.checks = Checks()
        self.check_schema = self.parse_xml_schema(check_schema_path)

        if (self.check_schema is not None):
            for folder_path in folders_with_checks:
                if (path.exists(folder_path) and path.isdir(folder_path)):
                    if (access(folder_path, R_OK)):
                        self.parse_checks_from_folder(folder_path)
                    else:
                        global_storage.logger.error(f"Folder {folder_path} is not accessible for reading!")
                else:
                    global_storage.logger.error(f"Folder {folder_path} does not exist!")

    def parse_xml_schema(self, xsd_file_path):
        """Checks if the specified .xsd-file is valid
        """
        result = None

        if (path.exists(xsd_file_path) and path.isfile(xsd_file_path)):
            if (self.is_xml_file_safe(xsd_file_path)):
                try:
                    # try to load an .xsd-file
                    schema = XMLSchema(xsd_file_path)
                except Exception as error:
                    global_storage.logger.error(f"Schema {xsd_file_path} is corrupted: {error}")
                else:
                    result = schema
            else:
                global_storage.logger.error(f"Check schema {xsd_file_path} is not safe to parse!")
        else:
            global_storage.logger.error(f"Check schema {xsd_file_path} does not exists!")

        return result

    def is_xml_file_safe(self, xml_file_path):
        """Checks if the .xml-file is safe for parsing
        """
        result = False

        try:
            DefusedET.parse(xml_file_path, forbid_dtd=True, forbid_entities=True, forbid_external=True)
        except Exception as error:
            global_storage.logger.error(f"Cannot parse {xml_file_path}: {error}")
        else:
            result = True

        return result

    def parse_checks_from_folder(self, folder_path):
        """Parses checks from the specific folder
        """
        for entry in scandir(folder_path):
            if (entry.is_file() and entry.name.startswith("check_") and entry.name.endswith(".xml")):
                check_path = path.join(folder_path, entry.name)

                cached_folder_path = f"{folder_path}_cache"
                cached_check_name, _ = path.splitext(entry.name)
                cached_check_path = path.join(cached_folder_path, f"{cached_check_name}.pickle")

                check = None
                if (self.is_cache_valid(check_path, cached_check_path)):
                    check = self.load_from_cache(cached_check_path)
                else:
                    check = self.parse_one_check(check_path)
                    if (isinstance(check, Check) and check.is_valid):
                        self.dump_to_cache(check, cached_check_path)
                    else:
                        global_storage.logger.warning(f"Check {check_path} is not valid!")

                if (isinstance(check, Check) and check.is_valid and check.is_enabled):
                    if (check not in self.checks):
                        self.checks.append(check)
                    else:
                        global_storage.logger.warning(f"Check {check_path} with name {check.name} has been "
                                                      " already parsed! Ignoring...")

    def is_cache_valid(self, check_path, cached_check_path):
        """Checks if the cached check is still valid
        """
        result = False

        if (path.exists(check_path) and path.exists(cached_check_path)):
            cached_check = self.load_from_cache(cached_check_path)

            if (self.hash_of_file(check_path) == cached_check.xml_hash):
                result = True

        return result

    def load_from_cache(self, cached_check_path):
        """Loads the check from cache
        """
        result = None

        try:
            with open(cached_check_path, "rb") as fd_cache:
                result = pickle_load(fd_cache)
        except Exception as error:
            global_storage.logger.warning(f"Cannot load check from {cached_check_path}: {error}")

        return result

    def dump_to_cache(self, check, cached_check_path):
        """Dumps the check to cache
        """
        try:
            # create folder for cache if it does not exist
            makedirs(path.dirname(cached_check_path), exist_ok=True)

            with open(cached_check_path, "wb") as fd_cache:
                pickle_dump(check, fd_cache)
        except Exception as error:
            global_storage.logger.warning(f"Cannot dump check to {cached_check_path}: {error}")

    def hash_of_file(self, file_path):
        """Returns SHA1-hash of the file
        """
        hash_sha1 = sha1()

        with open(file_path, "rb") as fd:
            chunk = fd.read(4096)

            while (chunk):
                hash_sha1.update(chunk)
                chunk = fd.read(4096)

        return hash_sha1.hexdigest()

    def parse_one_check(self, check_path):
        """Parses one check
        """
        result = None

        if (self.is_xml_file_safe(check_path)):
            if (self.is_xml_valid_against_schema(check_path)):
                hash_of_check = self.hash_of_file(check_path)
                element_tree = DefusedET.parse(check_path, forbid_dtd=True, forbid_entities=True, forbid_external=True)

                result = Check(element_tree, hash_of_check)
        else:
            global_storage.logger.error(f"Check {check_path} is not safe!")

        return result

    def is_xml_valid_against_schema(self, xml_file_path):
        """Checks if the .xml-file is valid against the schema
        """
        result = False

        try:
            # try to check the .xml-file against the schema
            result = self.check_schema.is_valid(xml_file_path)
        except Exception as error:
            global_storage.logger.warning(f"Error during the validation {xml_file_path} against the schema: {error}")

        return result

    def get_checks(self):
        """Returns list with checks
        """
        result = []

        if (self.checks):
            result = self.checks
        else:
            global_storage.logger.error("No checks found to use.")

        return result
