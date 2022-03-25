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

from setuptools import setup
from _version import __version__ as _version

setup(
    name='cFS-GroundSystem',
    packages=['Subsystems', 'Subsystems.tlmGUI', 'Subsystems.cmdGui', 'Subsystems.cmdUtil'],
    include_package_data=True,
    version=_version,
    entry_points={
        'console_scripts': [
            'cFS-GroundSystem=GroundSystem:main'
        ]
    },
)
