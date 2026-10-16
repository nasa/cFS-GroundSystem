#
#  NASA Docket No. GSC-19,200-1, and identified as "cFS Draco"
#
#  Copyright (c) 2023 United States Government as represented by the
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

import unittest
from unittest.mock import MagicMock

from CHeaderParser import find_data_type_new, prompt_array_size


class TestCHeaderParser(unittest.TestCase):

    def test_find_data_type_new(self):
        self.assertEqual(find_data_type_new('char', 'name[10]'), '--string')
        self.assertEqual(find_data_type_new('boolean', 'flag'), '--uint8')
        self.assertEqual(find_data_type_new('int32', 'count'), '--int32')
        self.assertEqual(find_data_type_new('uint16', 'port'), '--uint16')
        self.assertIsNone(find_data_type_new('custom_struct_t', 'data'))

    def test_prompt_array_size_already_valid_numeric_string(self):
        mock_input = MagicMock()
        result = prompt_array_size("my_array", initial_val="64", input_func=mock_input)
        self.assertEqual(result, "64")
        mock_input.assert_not_called()

    def test_prompt_array_size_boundary_values(self):
        mock_input = MagicMock()
        self.assertEqual(prompt_array_size("arr_zero", initial_val="0", input_func=mock_input), "0")
        self.assertEqual(prompt_array_size("arr_max", initial_val="128", input_func=mock_input), "128")
        mock_input.assert_not_called()

    def test_prompt_array_size_out_of_bounds_then_valid(self):
        # Reproduces Issue #241: entering an integer out of range should not cause
        # AttributeError: 'int' object has no attribute 'isdigit' on subsequent checks
        inputs = iter(["200", "64"])
        result = prompt_array_size(
            "OS_MAX_PATH_LEN",
            initial_val="OS_MAX_PATH_LEN",
            input_func=lambda _: next(inputs)
        )
        self.assertEqual(result, "64")

    def test_prompt_array_size_non_numeric_then_valid(self):
        inputs = iter(["not_a_number", "45"])
        result = prompt_array_size(
            "OS_MAX_PATH_LEN",
            initial_val="OS_MAX_PATH_LEN",
            input_func=lambda _: next(inputs)
        )
        self.assertEqual(result, "45")


if __name__ == '__main__':
    unittest.main()
