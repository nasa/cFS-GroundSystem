#
#  NASA Docket No. GSC-18,719-1, and identified as “core Flight System: Bootes”
#
#  Copyright (c) 2020 United States Government as represented by the
#  Administrator of the National Aeronautics and Space Administration.
#  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import glob
import pickle
import re
from html.parser import HTMLParser


class HTMLDocsParser(HTMLParser):
    #
    # Initializes allData variable
    #
    def reset(self):
        self.all_data = []
        HTMLParser.reset(self)

    #
    # Appends HTML file content to allData variable
    #
    def handle_data(self, data):
        if data.strip():  # excludes new lines
            self.all_data.append(data.strip())

    #
    # Determines UNIX data type of parameter
    #
    @staticmethod
    def find_data_type_new(data_type_orig, param_ln):
        if param_ln:  # assumes all string types have length enclosed in brackets
            return '--string'
        if data_type_orig in ('uint8', 'boolean'):
            return '--byte'
        if data_type_orig == 'uint16':
            return '--half'
        if data_type_orig == 'uint32':
            return '--word'
        if data_type_orig == 'uint64':
            return '--double'
        return ''

    #
    # Determines character array size for string types
    #
    @staticmethod
    def find_string_len(kywd):
        hdr_files = glob.glob('../../../build/cpu1/inc/*.h')
        hdr_files += glob.glob('../../fsw/cfe-core/src/inc/cfe_*.h')
        hdr_files += glob.glob('../../fsw/mission_inc/cfe_mission_cfg.h')
        val = ''
        found = False
        k = 0

        while not found and k < len(hdr_files):
            with open(hdr_files[k]) as hdr_obj:
                file_lines = hdr_obj.readlines()
                l = 0
                while not found and l < len(file_lines):
                    if f'#define {kywd}' in file_lines[l]:
                        found = True
                        val = file_lines[l].split()[2]
                    l += 1
            k += 1
        return val


if __name__ == '__main__':

    #
    # Initializes HTMLDocsParser class
    #
    parser = HTMLDocsParser()

    #
    # Searches for and reads in HTML files
    #
    file_list = glob.glob(
        '../../docs/cFE UsersGuide/Doxygen/struct_c_f_e__*.html')

    for html_file in file_list:  # loops through HTML files
        with open(html_file) as file_obj:  # opens HTML file
            reader = file_obj.read()  # reads HTML file
            parser.feed(reader)  # feeds file contents to parser
            all_data = parser.all_data

            data_types_orig = []  # uint8, uint16, uint32, char, boolean
            param_names = []  # parameter name
            param_len = []  # original parameter length
            param_desc = []  # parameter description
            data_types_new = []  # --string, --byte, --half, --word, --double
            string_len = []  # evaluated parameter length

            try:
                i = all_data.index("Data Fields") + 1
                j = all_data.index("Detailed Description")
                # iterates through lines between Data Fields and Detailed Description
                while i < j:
                    # skips header parameters
                    if any([x in all_data[i + 1] for x in ('Header', 'Hdr')]):
                        # if 'Header' in data[i + 1] or 'Hdr' in data[i + 1]:
                        i += 1
                        while not any(
                            [x in all_data[i]
                             for x in ('uint', 'char')]) and i < j:
                            # while 'uint' not in data[i] and 'char' not in data[
                            #         i] and i < j:
                            i += 1

                    else:
                        data_types_orig.append(all_data[i])  # stores data type
                        i += 1
                        param_names.append(all_data[i])  # stores parameter name
                        i += 1
                        param_len = ''
                        if '[' in all_data[i]:
                            param_len = all_data[
                                i]  # stores string length if provided
                            i += 1
                        param_len.append(param_len)
                        desc_string = ''
                        while not any([x in all_data[i] for x in ('uint', 'char')]) and i < j:
                            desc_string = f'{desc_string} {all_data[i]}'
                            i += 1
                        param_desc.append(desc_string.lstrip()
                                          )  # stores parameter description

                        # determines new data type of parameter
                        data_type_new = parser.find_data_type_new(
                            data_types_orig[-1], param_len[-1])
                        data_types_new.append(data_type_new)

                        # finds size of character array if type --string
                        keyword = ''
                        if data_type_new == '--string':
                            keyword = re.sub(r'\[|\]|\(|\)', '',
                                             param_len[-1])  # removes brackets
                            while not keyword.isdigit():
                                keyword = parser.find_string_len(keyword)
                                keyword = re.sub(r'\[|\]|\(|\)', '', keyword)
                        if keyword == '0':
                            keyword = input(
                                f'{param_len[-1]} not found. Please enter value manually: '
                            )
                        string_len.append(keyword)

                print("DATA TYPES:", data_types_orig)
                print("PARAM NAMES: ", param_names)
                print("PARAM STRING LEN:", param_len)
                print("PARAM DESC: ", param_desc)
                print("UNIX DATA TYPES:", data_types_new)
                print("STRING LENGTH:", string_len, "\n")

            except ValueError:
                print("Data Fields not found in HTML file")

            # write data to a file
            file_split = re.split(r'/|\.', html_file)
            pickle_file = 'ParameterFiles/' + file_split[-2]
            with open(pickle_file, 'wb') as pickle_obj:
                pickle.dump([
                    data_types_orig, param_names, param_len, param_desc,
                    data_types_new, string_len
                ], pickle_obj)

            # resets data list for next HTML file
            parser.all_data = []
