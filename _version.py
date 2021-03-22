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
#

# Development Build Macro Definitions
_cFS_GrndSys_build_number = 41
_cFS_GrndSys_build_baseline = "v2.2.0-rc1"

# Version Number Definitions
# ONLY APPLY for OFFICIAL release builds
_cFS_GrndSys_MAJOR = 2
_cFS_GrndSys_MINOR = 1
_cFS_GrndSys_REVISION = 0
_cFS_GrndSys_MISSIONREV = 0

# Development Build format for __version__
# Baseline git tag + Number of commits since baseline
__version__ = "+dev".join((_cFS_GrndSys_build_baseline,str(_cFS_GrndSys_build_number)))

# Development Build format for __version_string__
_version_string = " cFS-GroundSystem DEVELOPMENT BUILD\n " + __version__

# Use the following templates for Official Releases ONLY

    # Official Release format for __version__
    # __version__ = ".".join(map(str,(_cFS_GrndSys_MAJOR, _cFS_GrndSys_MINOR, _cFS_GrndSys_REVISION, _cFS_GrndSys_MISSIONREV)))

    # Official Release format for _version_string
    # _version_string = " cFS-GroundSystem v" + __version__

# END TEMPLATES
