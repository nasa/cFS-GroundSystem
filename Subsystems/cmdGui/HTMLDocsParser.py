#
#  GSC-18128-1, "Core Flight Executive Version 6.7"
#
#  Copyright (c) 2006-2019 United States Government as represented by
#  the Administrator of the National Aeronautics and Space Administration.
#  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
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
        self.allData = []
        HTMLParser.reset(self)

    #
    # Appends HTML file content to allData variable
    #
    def handle_data(self, data):
        if data.strip():  # excludes new lines
            self.allData.append(data.strip())

    #
    # Determines UNIX data type of parameter
    #
    @staticmethod
    def findDataTypeNew(dataTypeOrig, paramLn):
        if paramLn:  # assumes all string types have length enclosed in brackets
            return '--string'
        if dataTypeOrig in ('uint8', 'boolean'):
            return '--byte'
        if dataTypeOrig == 'uint16':
            return '--half'
        if dataTypeOrig == 'uint32':
            return '--word'
        if dataTypeOrig == 'uint64':
            return '--double'
        return ''

    #
    # Determines character array size for string types
    #
    @staticmethod
    def findStringLen(kywd):
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
            allData = parser.allData

            dataTypesOrig = []  # uint8, uint16, uint32, char, boolean
            paramNames = []  # parameter name
            paramLen = []  # original parameter length
            paramDesc = []  # parameter description
            dataTypesNew = []  # --string, --byte, --half, --word, --double
            stringLen = []  # evaluated parameter length

            try:
                i = allData.index("Data Fields") + 1
                j = allData.index("Detailed Description")
                # iterates through lines between Data Fields and Detailed Description
                while i < j:
                    # skips header parameters
                    if any([x in allData[i + 1] for x in ('Header', 'Hdr')]):
                        # if 'Header' in data[i + 1] or 'Hdr' in data[i + 1]:
                        i += 1
                        while not any(
                            [x in allData[i]
                             for x in ('uint', 'char')]) and i < j:
                            # while 'uint' not in data[i] and 'char' not in data[
                            #         i] and i < j:
                            i += 1

                    else:
                        dataTypesOrig.append(allData[i])  # stores data type
                        i += 1
                        paramNames.append(allData[i])  # stores parameter name
                        i += 1
                        param_len = ''
                        if '[' in allData[i]:
                            param_len = allData[
                                i]  # stores string length if provided
                            i += 1
                        paramLen.append(param_len)
                        desc_string = ''
                        while not any([x in allData[i] for x in ('uint', 'char')]) and i < j:
                            desc_string = f'{desc_string} {allData[i]}'
                            i += 1
                        paramDesc.append(desc_string.lstrip()
                                         )  # stores parameter description

                        # determines new data type of parameter
                        dataTypeNew = parser.findDataTypeNew(
                            dataTypesOrig[-1], paramLen[-1])
                        dataTypesNew.append(dataTypeNew)

                        # finds size of character array if type --string
                        keyword = ''
                        if dataTypeNew == '--string':
                            keyword = re.sub(r'\[|\]|\(|\)', '',
                                             paramLen[-1])  # removes brackets
                            while not keyword.isdigit():
                                keyword = parser.findStringLen(keyword)
                                keyword = re.sub(r'\[|\]|\(|\)', '', keyword)
                        if keyword == '0':
                            keyword = input(
                                f'{paramLen[-1]} not found. Please enter value manually: '
                            )
                        stringLen.append(keyword)

                print("DATA TYPES:", dataTypesOrig)
                print("PARAM NAMES: ", paramNames)
                print("PARAM STRING LEN:", paramLen)
                print("PARAM DESC: ", paramDesc)
                print("UNIX DATA TYPES:", dataTypesNew)
                print("STRING LENGTH:", stringLen, "\n")

            except ValueError:
                print("Data Fields not found in HTML file")

            # write data to a file
            file_split = re.split(r'/|\.', html_file)
            pickle_file = 'ParameterFiles/' + file_split[-2]
            with open(pickle_file, 'wb') as pickle_obj:
                pickle.dump([
                    dataTypesOrig, paramNames, paramLen, paramDesc,
                    dataTypesNew, stringLen
                ], pickle_obj)

            # resets data list for next HTML file
            parser.allData = []
