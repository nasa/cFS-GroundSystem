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

##############################################################################
# Created in Winter 2014-15
# Created by Winter Intern for NASA GSFC Code 582
#
# Edited by: Keegan Moore
# Summer Intern for NASA GSFC Code 582
# Note about edits:
#	findDataTypeNew() - kept the same
#	getFileList() - completely new utility for determining which files to use
#	__main__ - significant changes made to main code
#		- kept class functionality
#		- presents data to user rather than asking user to look in hdr file
#		- preserved pickle utility so the rest of the ground system remains
#			the same
#
##############################################################################
# Description:
#	CHeaderParser.py is designed to help automate the process of adding
# core Flight System (cFS) application commands and parameters to the
# python-based ground system that should come with this file. By prompting
# the user for necessary information, and parsing the cFS header files, this
# program will generate up to two different "pickle" files for the ground
# system to use (for information about pickle files and the pickle python
# library, see the link here: https://docs.python.org/3/library/pickle.html).
# These files will be placed in CommandFiles/ or ParameterFiles/.
#
# Usage:
#	This program requires the directory path to the application header file
# that contains both the Command Code Definitions and the Command Structures.
# This program, by default, looks in 'CHeaderParser-hdr-paths.txt' for the
# path to the files. If the user is inputting multiple header files, the user
# can enter the path to each header file on a new line.
#
# Examples:
# ~$ python CHeaderParser.py
#	The above command would look in CHeaderParser-hdr-paths.txt for its list
#	of header paths.
#
###############################################################################

import pickle
import re
import sys
from pathlib import Path

ROOTDIR = Path(sys.argv[0]).resolve().parent


#
# Translate known data types to arguments
#
def find_data_type_new(data_type_orig, param_name):
    if '[' in param_name:
        return '--string'
    if data_type_orig in ['boolean']:
        return '--uint8'
    if data_type_orig in ['int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']:
        return "--" + data_type_orig
    return None


# getFileList()
# Uses <filename> as a list of files to be parsed.
# Default filename is CHeaderParser-hdr-paths.txt
# This file is expected to be created by the user
# Returns list of paths to those files
# Added by Keegan Moore
def get_file_list(filename='CHeaderParser-hdr-paths.txt'):
    """ Gets the list of header files to be parsed from other file """

    paths = []

    # Try to open textfile list of header files
    try:
        with open(filename) as textfile:
            for l in textfile:
                # Remove whitespace before and after
                l = l.strip()
                if l and not l.startswith("#"):
                    paths.append(l)
        print(f"Using header files found in {filename}")
        # Send paths back to caller function
        return paths
    except IOError:
        print("Couldn't find default file. Check command line arguments.")

    print("No header files found. Please make sure to provide the\n"
          "default file for loading headers (CHeaderParser-hdr-paths.txt)")

    # If we got here, we couldn't find any header files, return empty list
    return []


if __name__ == '__main__':

    # Get list of files to parse
    file_list = get_file_list()

    # If list is empty, exit now
    if not file_list:
        print("ERROR: Empty file list. Nothing to be done. Exiting now.")
        sys.exit()

    # initialize command codes/descriptions lists as empty lists
    cmd_codes = []
    cmd_desc = []

    # create empty list for dumping header data
    master_hdr = []

    # Concatenate all headers into one variable for referencing
    for hdr_file in file_list:
        # open header file as single header
        with open(hdr_file) as single_hdr:
            # dump single header into master
            for single_line in single_hdr:
                master_hdr.append(single_line)

    # Reads and saves command and parameter information
    # Look through each line of the header file for command definitions
    for single_line in master_hdr:

        # Strip newline character off of single_line for easier parsing
        single_line = single_line.strip()

        if single_line.startswith("#define"):
            # We have found a possible definition
            # What makes a valid definition is one that has the following:
            # '#define' 'COMMAND_DESCRIPTION' 'VALUE' /* Maybe a comment too! */
            # but what we might see is a conditional compilation #define
            # So the next step is to remove comments and check if the possible
            # definition has the three parts of a definition like it should

            if '/*' in single_line:
                # There is a comment ('/*') somewhere in the definition
                # This program assumes there is nothing important after
                # So we get rid of it, before comparing it to the definition
                # structure
                single_line = single_line[:single_line.rfind('/*')]

            elif '//' in single_line:
                # There is a comment ('//') somewhere in the definition
                # This program assumes there is nothing important after
                # So we get rid of it, before comparing it to the definition
                # structure
                single_line = single_line[:single_line.rfind('//')]

            # Split single line into list for indexing
            definition = single_line.split()

            # Check if definition meets expected structure
            # Valid definitions should have following structure
            # '#define' 'COMMAND_DESCRIPTION' 'VALUE'
            # therefore a length of 3
            if len(definition) == 3:
                # Add command descriptions/codes to respective lists
                cmd_desc.append(definition[1])
                cmd_codes.append(definition[2])

    print(("We need to save the command into to a pickle file "
           "in 'CommandFile/'.\nPlease do not use any spaces/quotes "
           "in your filename. Ex: my_app_cmd_file"))
    cmd_file_name = input(
        "What would you like the command file to be saved as? ")

    # starting from last index (-1) going backward
    # (from example above) file_split[-2] = app_msg
    # therefore picklefile = CommandFiles/app_msg
    pickle_file = f'{ROOTDIR}/CommandFiles/{cmd_file_name}'

    # Open pickle file for storing command codes/descriptions
    with open(pickle_file, 'wb') as pickle_obj:
        #
        # FIGURE OUT WHY SHE DID THIS \\\
        #                              vvv
        pickle.dump([cmd_desc, cmd_codes, cmd_desc], pickle_obj)

    # Create a copy of command descriptions to preserve the original
    # unused_cmdDesc will be used to prompt user for parameters
    unused_cmd_desc = list(cmd_desc)

    # Create an empty list of used commands to be populated
    used_cmd_desc = []

    # Initialize looping variable
    cmd_index = 0

    # Print a list of unused commands for the user to pick from.
    print("\nUnused Commands")
    print("-----------------------------------------")
    for i, cmd in enumerate(unused_cmd_desc, start=1):
        print(f"(Command {i} of {len(unused_cmd_desc)}) {cmd}")

    while True:
        # Get user input to see if any commands from this file require parameters
        more_param_cmds = input(
            f'Do any commands in {cmd_file_name} require parameters? (yes/no): '
        )
        if more_param_cmds.lower() not in ['yes', 'y', 'no', 'n']:
            print(
                "Your response was not valid. Please enter (yes, y, no, or n)."
            )
        else:
            break

    # Check for exit condition
    if str.lower(more_param_cmds) in ['no', 'n']:
        print("You have chosen to exit. Exiting now.")
        sys.exit()

    # Continue onto creating parameter files if yes
    if str.lower(more_param_cmds) in ['yes', 'y']:

        # Continue to ask user for commands with parameters until we get -1 to exit.
        while True:
            command_choice = ""
            # Get user input
            try:
                command_choice = input(
                    "Enter a value from the list above or -1 to exit: ")
            except ValueError:
                pass

            # Check for exit condition
            if command_choice == "-1":
                print("Exiting.")
                break

            if command_choice.isdigit():
                command_choice = int(command_choice)

            # Make sure the choice is within range
            # Note that if command_choice is a string
            # it will never be in the range
            if command_choice not in range(1, len(unused_cmd_desc) + 1):
                print(
                    f"You entered {command_choice}, but that isn't an option.")
            else:
                # Choices are presented to user starting at 1, but list
                # indicies start at 0
                command_choice -= 1
                cmd_name = unused_cmd_desc[command_choice]

                # Initialize Parameter variables to empty lists
                param_names, param_desc, data_types_orig, \
                data_types_new, param_lens, string_lens = ([] for _ in range(6))

                # This empty list will hold possibly multiple lists of line numbers
                # each list representing where inside the App Header file the
                # structure can be found
                list_cmd_structs = []

                print(
                    "This program will now attempt to find the command structure for",
                    cmd_name)

                # create a copy of file_lines for parsing structures
                file_lines = list(master_hdr)

                # inside_struct will keep track of where the next
                # for loop is while it's scanning the file
                # if it is between '{' and '}', it will assume
                # it's inside of a struct
                inside_struct = False

                # line_num will keep track of what line we are looking at in the header file
                line_num = 0

                # Look through each line of the header file for command structures
                while line_num in range(len(file_lines)):

                    # check for the start of a structure
                    if '{' in file_lines[line_num]:
                        inside_struct = True

                    # if none is found, pass by and keep searching
                    else:
                        line_num += 1

                    # This empty list will hold the line numbers containing structure data
                    lines_of_struct = []

                    while inside_struct:
                        # Check for the end of the structure
                        # We will still want to know what line this is
                        if '}' in file_lines[line_num]:
                            # Clear the flag, we found the end.
                            inside_struct = False

                            # Add line number to list, even if it has a '}'
                            lines_of_struct.append(line_num)

                            # Now that we know the struct is over, add list of lines
                            # to the sets of command structures
                            list_cmd_structs.append(lines_of_struct)
                            break

                        # Add line number to list
                        lines_of_struct.append(line_num)
                        line_num += 1

                # After exiting this while loop, cmdStruct should contain a list of lists
                # The nested lists should contain line numbers to each structure in file
                for idx, line_list in enumerate(list_cmd_structs, start=1):
                    print("\nShowing structure", idx, "of",
                          len(list_cmd_structs), "below")
                    print("--------------------------------------------")
                    for line_num in line_list:
                        # Print the line from the file using the index from the list
                        print(file_lines[line_num].strip())
                    print("--------------------------------------------")

                while True:
                    struct_choice = ""

                    # Give the user the option to exit too.
                    try:
                        struct_choice = input(
                            "Enter a value from the list above or -1 to exit: "
                        )
                    except ValueError:
                        pass

                    # Check for exit condition
                    if struct_choice == "-1":
                        print("Exiting.")
                        sys.exit()

                    if struct_choice.isdigit():
                        struct_choice = int(struct_choice)

                    # Make sure the choice is valid
                    # Note that if struct_choice is a string
                    # it will never be in range
                    if struct_choice not in range(1,
                                                  len(list_cmd_structs) + 1):
                        print(
                            f"You entered '{struct_choice}', but that isn't an option."
                        )
                    else:
                        struct_choice -= 1
                        break

                # After exiting the while loop, user's structure choice should be a valid assignment
                # Take the appropriate list of lines from the list of command structures
                cmd_struct_lines = list(list_cmd_structs[struct_choice])

                # Initialize variable to get into loop
                param_line = 0

                # The following loop will iterate each time another
                # parameter is added to a command
                # After exiting the loop, the parameter variables
                # should be updated with a list of parameters for
                # the user's chosen command
                while param_line in range(len(cmd_struct_lines)):

                    # Display the command structure with indexed before each line
                    print("\n\n")
                    for line_num, line in enumerate(cmd_struct_lines):
                        # Dereference the index number in cmd_struct_lines to get the actual line number
                        actual_line = line

                        # print the line of the file with our "line number" next to it
                        print(
                            f"Line ({line_num}) -> {file_lines[actual_line].strip()}"
                        )

                    # Prompt the user for line number
                    param_line = int(
                        input(
                            "Enter the line of the parameter from the above print-out (-1 to stop): "
                        ))

                    # Check exit condition
                    if param_line == -1:
                        print("You have chosen to stop adding parameters.")
                        break

                    # Dereference the index number in cmd_struct_lines to get the actual line number
                    actual_line = cmd_struct_lines[param_line]

                    # Look at parameter line and split it into a list
                    line_split = file_lines[actual_line].split()

                    # Add original data type (C data type) to list
                    data_types_orig.append(line_split[0])

                    # Get rid of any occurance of ';' (at the end of the line)
                    param_names.append(re.sub(';', '', line_split[1]))

                    # Input to add param description
                    param_desc.append(input('Please enter parameter description: '))

                    # Determines data type for us to use
                    # returns null if no type could match
                    data_type_new = find_data_type_new(data_types_orig[-1],
                                                       param_names[-1])

                    # If no type could match, ask user for data type
                    if not data_type_new:
                        data_type_new = input(
                            (f'Data type for {param_names[-1]} not found. '
                             'Please enter new data type by hand: '))

                    data_types_new.append(data_type_new.strip())

                    # finds length if --string data type
                    if 'string' in data_type_new:

                        # Split parameter name into list, separating by '[' or ']'
                        # if paramNames[-1] == 'array[10]' then
                        # array_name_size == ['array', '10']
                        array_name_size = re.split(r'\[|\]', param_names[-1])

                        # Re-assign paramName to just the name of the array
                        # (before -> 'array[10]', after -> 'array')
                        param_names[-1] = array_name_size[0]

                        # set array size to the second element
                        array_size = array_name_size[1]

                        # Add array size to the parameter list
                        param_lens.append(array_size)

                        print("Array size:", array_size)

                        # This while loop will make sure that
                        # the user input is both
                        # - a valid integer
                        # - between 0 and 128 (inclusively)
                        while not array_size.isdigit() or int(
                                array_size) not in range(129):
                            # User input is not an integer
                            if not array_size.isdigit():
                                print("Could not translate",
                                      array_name_size[1])
                            else:
                                print(
                                    "Array size out of bounds. It must be between 0 and 128."
                                )
                            try:
                                # Try to translate user input to an integer
                                array_size = int(
                                    input(
                                        (f"Please enter the defined value for "
                                         f"{array_name_size[1]} (0 - 128): ")))
                            except ValueError:
                                pass  # Ignore non-integer and try again

                        # Add string length argument to parameter list
                        string_lens.append(array_size)

                    else:
                        string_lens.append('')
                        param_lens.append('')

                    # print the last element of list to see if it worked
                    print("dataTypeOrig:", data_types_orig[-1])
                    print("dataTypeNew:", data_types_new[-1])
                    print("paramName:", param_names[-1])
                    print("paramLen:", param_lens[-1])
                    print("stringLen:", string_lens[-1])

                    print("Added:", param_names[-1], "with type",
                          data_types_new[-1])

                    # Remove used parameter from command structure lines
                    # so that the user doesn't choose the same parameter twice
                    del cmd_struct_lines[param_line]

                    # make sure param_line stays in bounds
                    # (If the user chose the last line in this iteration,
                    # param_line would be out of bounds after deleting a line)
                    param_line = 0

                    # Start the loop over to see if user has more parameters

                # Add command to used commands, to keep track of things
                used_cmd_desc.append(unused_cmd_desc[command_choice])

                # Take this command out of the list of unused commands before restarting the loop
                del unused_cmd_desc[command_choice]

                # If we later want the list of structs to be updated, to remove
                # previously selected structs, uncomment this line
                # del list_cmd_structs[struct_choice]

                # saves parameter information in pickle file for command
                pickle_file = f'{ROOTDIR}/ParameterFiles/{cmd_name}'
                with open(pickle_file, 'wb') as pickle_obj:
                    pickle.dump([
                        data_types_orig, param_names, param_lens, param_desc,
                        data_types_new, string_lens
                    ], pickle_obj)

                # Print a list of unused commands for the user to pick from.
                print("")
                print("Unused Commands")
                print("-----------------------------------------")
                for cmd_index, cmd in enumerate(unused_cmd_desc, start=1):
                    print(f"Command ({cmd_index} of {len(unused_cmd_desc)})",
                          cmd)

            # End of 'while True:'
            # We must have received a -1 when prompting user for the next command.

    print("Thank you for using CHeaderParser.")
    print("The following commands have been added with parameters: ")
    print(used_cmd_desc)
