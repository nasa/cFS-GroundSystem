# Changelog

## Development Build: equuleus-rc1+dev18
- Fix misleading wording in Commands-Telemetry.md
- See <https://github.com/nasa/cFS-GroundSystem/pull/249>

## Development Build: equuleus-rc1+dev14
- Update LogOverflowCounter Description
- Update incorrect variable descriptions in tlm.txt
- Add missing description fields to cfe-es-hk-tlm.txt
- See <https://github.com/nasa/cFS-GroundSystem/pull/233>, <https://github.com/nasa/cFS-GroundSystem/pull/235>, and <https://github.com/nasa/cFS-GroundSystem/pull/236>

## Development Build: equuleus-rc1+dev6
- making version string PEP 440-compliant
- See <https://github.com/nasa/cFS-GroundSystem/pull/245>

## Development Build: equuleus-rc1+dev2
- updating cFS_GroundSystem to use new versioning system
- See <https://github.com/nasa/cFS-GroundSystem/pull/239>

## Development Build: v3.0.0-rc4+dev43
- Add input so users can specify the parameter description
- See <https://github.com/nasa/cFS-GroundSystem/pull/206>

## Development Build: v3.0.0-rc4+dev39
- Update CI_LAB commands in GroundSystem Tool
- naming error
- See <https://github.com/nasa/cFS-GroundSystem/pull/230> and <https://github.com/nasa/cFS-GroundSystem/pull/217>

## Development Build: v3.0.0-rc4+dev33
- Update TO_LAB commands in GroundSystem Tool
- Create CHANGELOG.md
- See <https://github.com/nasa/cFS-GroundSystem/pull/224> and <https://github.com/nasa/cFS-GroundSystem/pull/225>

## Development Build: v3.0.0-rc4+dev25
- Remove 'return;' from last line of void functions.
- See <https://github.com/nasa/cFS-GroundSystem/pull/222>

## Development Build: v3.0.0-rc4+dev19
- Update Copyright Headers
- Standardize version information 
- See <https://github.com/nasa/cFS-GroundSystem/pull/209> and <https://github.com/nasa/cFS/445>

## Development Build: v3.0.0-rc4+dev12
- Apply header guard standard
- See <https://github.com/nasa/cFS/pull/432>

## Development Build: v3.0.0-rc4+dev7
- Free Address Info to fix resource leak
- Converted most variable,function, and method names into snake_case
- Set new build baseline for cFS-Caelum-rc4: v3.0.0-rc4
- See <https://github.com/nasa/cFS-GroundSystem/pull/201> and <https://github.com/nasa/cFS/pull/390> 


## Development Build: v2.2.0-rc1+dev63
- Add Virtualenv and Pipenv .gitignore support
- Fix doc, comment, and message typos 
- See <https://github.com/nasa/cFS-GroundSystem/pull/195> and <https://github.com/nasa/cFS/pull/348>

## Development Build: v2.2.0-rc1+dev58
- Update tlm for ES Blockstats/memstats and TBL HK
- Assign variables before referencing them
- See <https://github.com/nasa/cFS-GroundSystem/pull/192> and <https://github.com/nasa/cfs/pull/313>

## Development Build: v2.2.0-rc1+dev52
- Add test start command script for cmdUtil
- Implement Coding Standard in CodeQL
- See <https://github.com/nasa/cFS-GroundSystem/pull/183> and <https://github.com/nasa/cFS/pull/270>

## Development Build: v2.2.0-rc1+dev46
- Changes executable command from 'startg' to 'cFS-GroundSystem'
- Changes version to be the version stated in version.py
- Adds executable installation instructions to Guide-GroundSystem.md
- See <https://github.com/nasa/cFS-GroundSystem/pull/178> and <https://github.com/nasa/cFS/pull/248>

## Development Build: v2.2.0-rc1+dev41
- Corrects values in sb and tbl hk-tlm.txt to allow the TBL and SB tlm pages to open.
- Adds a contributing guide that links to the main cFS contributing guide.
- See <https://github.com/nasa/cfs-groundsystem/pull/171>

## Development Build: v2.2.0-rc1+dev33
- Fix #163, Add Testing Tools to the Security Policy
- See <https://github.com/nasa/cfs-groundsystem/pull/167>

## Development Build: v2.2.0-rc1+dev18
- Documentation: Add `Security.md` with instructions to report vulnerabilities
- **Breaking change**, CmdUtil, Rounds header up to match <https://github.com/nasa/cFE/pull/1077>
- **Breaking change**, GUI, Rounds header up to match <https://github.com/nasa/cFE/pull/1077>
- See <https://github.com/nasa/cFS-GroundSystem/pull/150>

## Development Build: v2.2.0-rc1+dev11
- Updated CHeaderParser.py to address specific issues.
- See <https://github.com/nasa/cFS-GroundSystem/pull/135>

## Development Build: v2.2.0-rc1+dev8
- Replaces old code that caused a cast-align warning when strict. Refactored and removed unnecessary code while also following recommended model for getaddrinfo. Removed old windows support/defines/etc (likely not tested for years, no longer supported).
- Reduce the size of the strncpy so that it ensures there's a null byte at the end of the string buffer.
- See <https://github.com/nasa/cFS-GroundSystem/pull/133>

## Development Build: v2.2.0+dev2
 - Fixes multiple typos
- See <https://github.com/nasa/cFS-GroundSystem/pull/127>

## Development Build: v2.1.0+dev85
- Remove unused code/packages to fix LGTM warnings
- See <https://github.com/nasa/cFS-GroundSystem/pull/120>

## Development Build: v2.1.0+dev76
- Fixes more lgtm warnings
- Allows users to change the byte offsets for sending commands and parsing telemetry, to support different header versions or other implementations of cFS
- Adds a file to store version information and reports version upon ground-system startup.
- See <https://github.com/nasa/cFS-GroundSystem/pull/109>

## Development Build: 2.1.12
- Change all individual UI elements to table widgets. Update backend code accordingly
- Temporary fix for implicit declaration of endian functions on some systems (RH/CentOs). No build errors on CentOS
- See <https://github.com/nasa/cFS-GroundSystem/pull/107>

## Development Build: 2.1.11
- Default behavior is the same except adds checksum and doesn't actually require fields. Adds all the packet fields, overrides, more supported data types, etc.
- See <https://github.com/nasa/cFS-GroundSystem/pull/101>

## Development Build: 2.1.10
- Change documentation for table loading guide to markdown
- See <https://github.com/nasa/cFS-GroundSystem/pull/94>

## Development Build: 2.1.9
- Upgrading PyQt4 to PyQt5 and includes a lot of cleanup/refactoring, and changes to the GUI itself
- See <https://github.com/nasa/cFS-GroundSystem/pull/90>

## Development Build: 2.1.8
- No warnings when building with GCC9
- Event messages now display both Event type and ID.
- See <https://github.com/nasa/cFS-GroundSystem/pull/86>

## Development Build: 2.1.7
- Commands and Telemetry definitions now match code
- See <https://github.com/nasa/cFS-GroundSystem/pull/74>

## Development Build: 2.1.6
- Cmd code (and checksum) are always in the same place
- See <https://github.com/nasa/cFS-GroundSystem/pull/69>

## Development Build: 2.1.5
- Updated build instructions for Python 3
- See <https://github.com/nasa/cFS-GroundSystem/pull/64>

## Development Build: 2.1.4
- Finish conversion to python 3
- cmdutil now accepts --word as alias to --long
- See <https://github.com/nasa/cFS-GroundSystem/pull/54>

## Development Build: 2.1.3
- Minor updates to work with python 3
- No longer compatible with python 2.7
- Note issue #50 is to update the related documentation
- See <https://github.com/nasa/cFS-GroundSystem/pull/47>

## Development Build: 2.1.2
- Minor updates (see <https://github.com/nasa/cFS-GroundSystem/pull/39>)

## Development Build: 2.1.1
- Minor updates (see <https://github.com/nasa/cFS-GroundSystem/pull/36>)

## **_OFFICIAL RELEASE 2.1.0 - Aquila_**
- Minor updates (see <https://github.com/nasa/cFS-GroundSystem/pull/26>)
- Released as part of cFE 6.7.0, Apache 2.0

## **_OFFICIAL RELEASE 2.0.90a_**
- Released as part of cFE 6.6.0a, Apache 2.0

## Known issues
As a lab application, extensive testing is not performed prior to release and only minimal functionality is included.

## Getting Help
For best results, submit issues:questions or issues:help wanted requests at <https://github.com/nasa/cFS>.

Official cFS page: <http://cfs.gsfc.nasa.gov>
