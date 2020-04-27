# Core Flight System : Framework : Tool : Ground System

This repository contains NASA's Lab Ground System (cFS-GroundSystem), which is a framework component of the Core Flight System.

This lab application is a non-flight utility ground system to interact with the cFS. It is intended to be located in the `tools/cFS-GroundSystem` subdirectory of a cFS Mission Tree.  The Core Flight System is bundled at https://github.com/nasa/cFS (which includes cFS-GroundSystem as a submodule), which includes build and execution instructions.

See Guide-GroundSystem.txt for more information.

## Version History

##### Development Build: 2.1.7  
  - Commands and Telemetry definitions now match code
  - See https://github.com/nasa/cFS-GroundSystem/pull/74

##### Development Build: 2.1.6
  - Cmd code (and checksum) are always in the same place
  - See https://github.com/nasa/cFS-GroundSystem/pull/69

##### Development Build: 2.1.5
  - Updated build instructions for Python 3
  - See https://github.com/nasa/cFS-GroundSystem/pull/64

##### Development Build: 2.1.4
  - Finish conversion to python 3
  - cmdutil now accepts --word as alias to --long
  - See https://github.com/nasa/cFS-GroundSystem/pull/54

##### Development Build: 2.1.3
  - Minor updates to work with python 3
  - No longer compatible with python 2.7
  - Note issue #50 is to update the related documentation
  - See https://github.com/nasa/cFS-GroundSystem/pull/47

##### Development Build: 2.1.2
  - Minor updates (see https://github.com/nasa/cFS-GroundSystem/pull/39)

##### Development Build: 2.1.1
  - Minor updates (see https://github.com/nasa/cFS-GroundSystem/pull/36)

### ***OFFICIAL RELEASE 2.1.0***
  - Minor updates (see https://github.com/nasa/cFS-GroundSystem/pull/26)
  - Released as part of cFE 6.7.0, Apache 2.0

### ***OFFICIAL RELEASE 2.0.90a***
  - Released as part of cFE 6.6.0a, Apache 2.0

## Known issues

As a lab application, extensive testing is not performed prior to release and only minimal functionality is included.

## Getting Help

For best results, submit issues:questions or issues:help wanted requests at https://github.com/nasa/cFS.

Official cFS page: http://cfs.gsfc.nasa.gov
