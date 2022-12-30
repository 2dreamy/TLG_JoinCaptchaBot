# -*- coding: utf-8 -*-

'''
Script:
    tsjson.py
Description:
    Thread-Safe JSON files read/write library.
Author:
    Jose Miguel Rios Rubio
Creation date:
    20/07/2017
Last modified date:
    30/12/2022
Version:
    1.2.1
'''

###############################################################################
### Standard Libraries

# Logging Library
import logging

# Operating System Library
from os import makedirs as os_makedirs
from os import path as os_path
from os import remove as os_remove
from os import stat as os_stat

# JSON Library
from json import dump as json_dump
from json import load as json_load

# Collections Data Types Library
from collections import OrderedDict

# Threads and Multi-tasks Library
from threading import Lock

# Error Traceback Library
from traceback import format_exc

###############################################################################
### Logger Setup

logger = logging.getLogger(__name__)

###############################################################################
### Thread-Safe JSON Class

class TSjson():
    '''
    Thread-Safe JSON files read/write class.
    '''

    def __init__(self, file_name):
        '''
        Class Constructor.
        It initializes the Mutex Lock element and get the file path.
        '''
        self.lock = Lock()
        self.file_name = file_name

    ###########################################################################
    ### Raw Read-Write-Delete Methods

    def read(self):
        '''
        Thread-Safe Read of JSON file.
        It locks the Mutex access to the file, checks if the file exists
        and is not empty, and then reads it content and try to parse as
        JSON data and store it in an OrderedDict element. At the end,
        the lock is released and the read and parsed JSON data is
        returned. If the process fails, it returns None.
        '''
        read = {}
        # Try to read the file
        try:
            with self.lock:
                # Check if file exists and is not empty
                if not os_path.exists(self.file_name):
                    return {}
                if not os_stat(self.file_name).st_size:
                    return {}
                # Read the file and parse to JSON
                with open(self.file_name, "r", encoding="utf-8") as file:
                    read = json_load(file, object_pairs_hook=OrderedDict)
        except Exception:
            logger.error(format_exc())
            logger.error("Fail to read JSON file %s", self.file_name)
            read = None
        return read


    def write(self, data):
        '''
        Thread-Safe Write of JSON file.
        It checks and creates all the needed directories to file path if
        any does not exists. Then it locks the Mutex access to the file,
        opens and overwrites the file with the provided JSON data.
        '''
        write_result_ok = False
        if not data:
            return False
        # Check for directory path and create all needed directories
        directory = os_path.dirname(self.file_name)
        if not os_path.exists(directory):
            os_makedirs(directory)
        # Try to write the file
        try:
            with self.lock:
                with open(self.file_name, "w", encoding="utf-8") as file:
                    json_dump(data, fp=file, ensure_ascii=False, indent=4)
                write_result_ok = True
        except Exception:
            logger.error(format_exc())
            logger.error("Fail to write JSON file %s", self.file_name)
        return write_result_ok


    def delete(self):
        '''
        Remove a JSON file.
        '''
        remove_ok = False
        try:
            with self.lock:
                if os_path.exists(self.file_name):
                    os_remove(self.file_name)
                remove_ok = True
        except Exception:
            logger.error(format_exc())
            logger.error("Fail to remove JSON file %s", self.file_name)
        return remove_ok

    ###########################################################################
    ### Data Content Methods

    def read_content(self):
        '''
        Read JSON file content data.
        It call to read() function to get the OrderedDict element of the
        file JSON data and then return the specific JSON data from the
        dict ("content" key).
        '''
        read = self.read()
        if read is None:
            return {}
        if read == {}:
            return {}
        return read["Content"]


    def write_content(self, data):
        '''
        Write JSON file content data.
        It checks and creates all the needed directories to file path if
        any does not exists.
        '''
        write_result_ok = False
        if not data:
            return False
        # Check for directory path and create all needed directories
        directory = os_path.dirname(self.file_name)
        if not os_path.exists(directory):
            os_makedirs(directory)
        # Try to write the file
        try:
            with self.lock:
                # Check if file exists and is not empty
                if os_path.exists(self.file_name) \
                and os_stat(self.file_name).st_size:
                    # Read the file, parse to JSON and add read data to
                    # dictionary content key
                    with open(self.file_name, "r", encoding="utf-8") as file:
                        content = json_load(
                                file,
                                object_pairs_hook=OrderedDict)
                    content["Content"].append(data)
                    # Overwrite the file with the new content data
                    with open(self.file_name, "w", encoding="utf-8") as file:
                        json_dump(
                                content, fp=file, ensure_ascii=False, indent=4)
                    write_result_ok = True
                # If the file doesn't exist or is empty
                else:
                    # Write the file with an empty content data
                    with open(self.file_name, "w", encoding="utf-8") as file:
                        file.write("\n{\n    \"Content\": []\n}\n")
                    # Read the file, parse to JSON and add read data to
                    # dictionary content key
                    with open(self.file_name, "r", encoding="utf-8") as file:
                        content = json_load(file)
                    content["Content"].append(data)
                    # Overwrite the file with the new content data
                    with open(self.file_name, "w", encoding="utf-8") as file:
                        json_dump(
                                content, fp=file, ensure_ascii=False, indent=4)
                    write_result_ok = True
        except IOError as error:
            logger.error(format_exc())
            logger.error("I/O fail (%s): %s", error.errno, error.strerror)
        except ValueError:
            logger.error(format_exc())
            logger.error("Data conversion fail")
        except Exception:
            logger.error(format_exc())
            logger.error(
                    "Fail to write content of JSON file %s",
                    self.file_name)
        return write_result_ok


    def is_in(self, data):
        '''
        Check if provided key exists in JSON file data.
        It reads all the JSON file data and check if the key is present.
        '''
        # Read the file data
        file_data = self.read()
        if file_data is None:
            return False
        if file_data == {}:
            return False
        # Search element with UID
        for _data in file_data["Content"]:
            if data == _data:
                return True
        return False


    def is_in_position(self, data):
        '''
        Check if provided key exists in JSON file data and get the
        index from where it is located.
        '''
        i = 0
        found = False
        # Read the file data
        file_data = self.read()
        if file_data is None:
            return False, -1
        if file_data == {}:
            return False, -1
        # Search and get index of element with UID
        for _data in file_data["Content"]:
            if data == _data:
                found = True
                break
            i = i + 1
        return found, i


    def remove_by_uid(self, element_value, uid):
        '''
        From the JSON file content, search and remove an element that
        has a specified Unique Identifier (UID) key.
        Note: If there are elements with same UIDs, only the first one
        detected will be removed.
        '''
        found = False
        # Read the file data
        file_content = self.read_content()
        if file_content == {}:
            return False
        # Search and remove element with UID
        for data in file_content:
            if data[uid] == element_value:
                found = True
                file_content.remove(data)
                break
        # Rewrite to file after deletion
        self.clear_content()
        if file_content:
            self.write_content(file_content[0])
        return found


    def search_by_uid(self, element_value, uid):
        '''
        From the JSON file content, search and get an element that has
        a specified Unique Identifier (UID) key.
        Note: If there are elements with same UIDs, only the first one
        detected will be detected.
        '''
        result = {}
        result["found"] = False
        result["data"] = None
        # Read the file data
        file_data = self.read()
        if file_data is None:
            return result
        if file_data == {}:
            return result
        # Search and get element with UID
        for element in file_data["Content"]:
            if not element:
                continue
            if element[uid] == element_value:
                result["found"] = True
                result["data"] = element
                break
        return result


    def update(self, data, uid):
        '''
        From the JSON file content, search and update an element that
        has a specified Unique Identifier (UID) key.
        Note: If there are elements with same UID, only the first one
        detected will be updated.
        '''
        i = 0
        found = False
        # Read the file data
        file_data = self.read()
        if file_data is None:
            return False
        if file_data == {}:
            return False
        # Search and get index of element with UID
        for msg in file_data["Content"]:
            if data[uid] == msg[uid]:
                found = True
                break
            i = i + 1
        # Update UID element data and overwrite JSON file
        if found:
            file_data['Content'][i] = data
            self.write(file_data)
        else:
            logger.error("Element with UID no found in JSON file.")
        return found


    def update_twice(self, data, uid1, uid2):
        '''
        From the JSON file content, search and update an element that
        has two specified Unique Identifier (UID) keys.
        Note: If there are elements with same UIDs, only the first one
        detected will be updated.
        '''
        i = 0
        found = False
        # Read the file data
        file_data = self.read()
        if file_data is None:
            return False
        if file_data == {}:
            return False
        # Search and get index of element with both UIDs
        for msg in file_data["Content"]:
            if (data[uid1] == msg[uid1]) and (data[uid2] == msg[uid2]):
                found = True
                break
            i = i + 1
        # Update UID element data and overwrite JSON file
        if found:
            file_data["Content"][i] = data
            self.write(file_data)
        else:
            logger.error("Element with UID no found in JSON file.")
        return found


    def clear_content(self):
        '''
        Clear data content of the JSON file.
        It locks the Mutex access to the file, and if the file exists
        and is not empty, the content is cleared to a default skelleton.
        '''
        clear_ok = False
        try:
            with self.lock:
                if not os_path.exists(self.file_name):
                    return False
                if not os_stat(self.file_name).st_size:
                    return False
                with open(self.file_name, "w", encoding="utf-8") as file:
                    file.write("\n{\n    \"Content\": [\n    ]\n}\n")
                clear_ok = True
        except Exception:
            logger.error(format_exc())
            logger.error("Fail to clear JSON file %s", self.file_name)
        return clear_ok
