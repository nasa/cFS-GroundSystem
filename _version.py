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

# Development Build Macro Definitions
_cFS_GrndSys_build_number = 18
_cFS_GrndSys_build_baseline = "7.2"
_cFS_GrndSys_build_dev_baseline = "equuleus-rc1"
_cFS_GrndSys_build_dev_cycle = "equuleus-rc2"
_cFS_GrndSys_build_codename = "Equuleus"

# Version Number Definitions see doxygen docs for definitions
_cFS_GrndSys_MAJOR = 2 # Major version number 
_cFS_GrndSys_MINOR = 1 # Minor version number 
_cFS_GrndSys_REVISION = 0 # Revision version number 


# Mission revision.
# 
# Reserved for mission use to denote patches/customizations as needed.
# Values 1-254 are reserved for mission use to denote patches/customizations as # needed. NOTE: Reserving 0 and 0xFF for cFS open-source development use 
# (pending resolution of nasa/cFS#440)
_cFS_GrndSys_MISSIONREV = 255

# Development Build format for __version__
# Baseline git tag + Number of commits since baseline
__version__ = "+".join((_cFS_GrndSys_build_baseline, _cFS_GrndSys_build_dev_baseline + "_dev" + str(_cFS_GrndSys_build_number)))

# Development Build format for __version_string__
_version_string = " cFS-GroundSystem DEVELOPMENT BUILD\n " + __version__

# Use the following templates for Official Releases ONLY

    # Official Release format for __version__
    # __version__ = ".".join(map(str,(_cFS_GrndSys_MAJOR, _cFS_GrndSys_MINOR, _cFS_GrndSys_REVISION, _cFS_GrndSys_MISSIONREV)))

    # Official Release format for _version_string
    # _version_string = " cFS-GroundSystem v" + __version__

# END TEMPLATES
