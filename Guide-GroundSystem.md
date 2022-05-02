# cFS Ground System Version 2.1.12

## cFS Ground System Info

The GroundSystem directory contains the new Ground System project for the cFS, that incorporates the main window to launch commands and telemetry systems, and other utilities like FDL/FUL and FT managers to send and receive files. The main window runs alongside the Routing Service (`RoutingService.py`). The Routing Service handles all incoming data and publishes (PUB/SUB) the data to specific ZeroMQ channels so that the different ground system utilities can receive (subscribe) only the desired data.

This ground system supports commanding and receiving telemetry from multiple spacecraft using UDP.

The Ground System contains the main window that lets you launch the different utilities.

To start receiving data from the cFS, you need to enable telemetry first. To enable telemetry:

- click the "Start Command System" button from the main window,
- then from the Command System Main Page click the "Enable Tlm" button (you will need to enter the target/destination IP address as an input to this command).

Note: The Main Window needs to be opened at all times so that the telemetry messages can be forwarded to the Telemetry System.

The Ground System will automatically detect the spacecraft when it starts sending the telemetry, and it will be added to the IP addresses list. You can select the spacecraft from the list, and start Telemetry System to receive its data. If 'All' spacecraft are selected, you can start Telemetry System to display the packet count from multiple spacecraft (if it detected more than one).

Future enhancements:

1. Detect different spacecraft based on telemetry header (spacecraft `id`) data instead of using the spacecraft IP address.
2. Add instructions for Windows.

## Install and run

Before launching the Ground System make sure that:
- PyQt5 is installed,
- PyZMQ is installed,
- cmdUtil is compiled.

Installing and running cFS Ground System on Ubuntu:

1. ```sudo apt-get install python3-pyqt5```
1. ```sudo apt-get install python3-zmq```
1. ```sudo apt-get install libcanberra-gtk-module```
1. ```make -C Subsystems/cmdUtil```
1. ```python3 GroundSystem.py```

The historically included instructions for running on macOS or CentOS are included at the bottom of this document for reference. Please note that instructions have not been maintained. Welcoming instruction contributions if any of these are your platform of choice.

### Install Ground System executable
This works for both macOS and Ubuntu systems.
```
The requirements.txt file is located directly inside the cFS-GroundSystem/
$ pip3 install -r requirements.txt
$ pip3 install -e relative/path/to/cFS-GroundSystem
$ cFS-GroundSystem
```
## Adding new flight software application to ground system command GUI

This section was made to help developers who are adding core Flight Software (cFS) Applications to the Python-based Ground System that comes with this cFS distribution.

The `CHeaderParser.py` program that should be found in:

```GroundSystem/Subsystems/cmdGui```

Is an interactive, command-line based program to help walk developers through the process of adding custom cFS applications to the Ground System. Along with `CHeaderParser.py` is a configuration file that CHeaderParser uses to find the proper header files for your "new" cFS application. This file is named `CHeaderParser-hdr-paths.txt`, and should be placed in the same directory as `CHeaderParser.py`.

Expected file structure:

```
cFE-6.4.x-OSS-release/cfe/tools/cFS-GroundSystem/Subsystems/cmdGui/CHeaderParser.py
cFE-6.4.x-OSS-release/cfe/tools/cFS-GroundSystem/Subsystems/cmdGui/CHeaderParser-hdr-paths.txt
cFE-6.4.x-OSS-release/cfe/tools/cFS-GroundSystem/Subsystems/cmdGui/CommandFiles/
cFE-6.4.x-OSS-release/cfe/tools/cFS-GroundSystem/Subsystems/cmdGui/ParameterFiles/
cFE-6.4.x-OSS-release/cfe/tools/cFS-GroundSystem/Subsystems/cmdGui/command-pages.txt
```

Steps to adding application commands to the Ground System:

1. Edit `CHeaderParser-hdr-paths.txt`:
   1. Locate any header files that contain command code definitions or command structure definitions. These files typically end in `*app_msg.h` or `*app_msgdefs.h` but could be named anything.
   1. Add each one of the paths to a new line in `CHeaderParser-hdr-paths.txt`.
   1. Comment out any paths/lines that aren't needed with `#` (at the beginning of the line).

1. Run CHeaderParser:
   1. Call CHeaderParser using python: `python3 CHeaderParser.py`
   1. The program will prompt you to enter a filename for the application. This will create a pickle file for your application named `CommandFiles/<user_defined_name>`. Notice that this file will be stored in the `CommandFiles` directory. This same filename will be used in `command-pages.txt` later.
   1. Type `yes` if any commands in your application have parameters. The program will then look through the provided header files for `definitions.pick` which-ever definitions describe related command codes (one at a time, the program will prompt you for the next command code after all parameters have been added for the current command).
   1. Select the appropriate command structure for the selected command. The program will show all structures that it could find in the provided header files. Enter the index of the command structure (the corresponding index should be above the command structure).
   1. Select any parameters from the structure that apply. Once you have selected all applicable lines from the command structure, enter `-1` to finish. This will create a pickle file for the command/parameters named `ParameterFiles/<command_name>`. Notice that this file will be stored in the `ParameterFiles` directory.

1. Update `command-pages.txt` (CSV):
   1. Column 1 - Title of your application (whatever you want it called).
   1. Column 2 - filename of your application (chosen in Step 2.ii) under `CommandFiles` directory.
   1. Column 3 - Message ID for Application Commands (typically defined in `mission_msgids.h`).
   1. Column 4 - Endianess (default little endian: `LE`).
   1. Column 5 - PyGUI Page (default: `UdpCommands.py`).
   1. Column 6 - Command Send Address (default: `127.0.0.1`).
   1. Column 7 - Command Send Port (default: `1234`).

   Notes:
   - USE ONLY SPACES, NO TABS (Remember, it's Python).
   - Don't leave any empty lines in `command-pages.txt`, this could cause errors when running `GroundSystem.py` and `CommandSystem.py`.

After completing these steps, restart the Ground System and the changes should have taken effect.

## Common issues and troubleshooting

### Issue: Cannot Send Command, receiving the "[Errno 8] Exec format error"

Traceback:
```
Calling cmdUtil from Parameter.py Traceback (most recent call last): File "Parameter.py", line 100, in ProcessSendButton subprocess.Popen(cmd_args, stdout=subprocess.PIPE) File "/usr/lib/python3.7/subprocess.py", line 642, in __init__ errread, errwrite) File "/usr/lib/python3.7/subprocess.py", line 1234, in _execute_child raise child_exception OSError: [Errno 8] Exec format error
```
Fix: This problem is most likely caused by calling `cmdUtil` without compiling it.  This issue has also been found to occur when the `cmdUtil` executable has been compressed/decompressed. To fix this problem, use the `Makefile` inside of the `cmdUtil` directory to compile or recompile (in the case after decompressing).
```
$ cd Subsystems/cmdUtil $ make $ cd ../.. $ python3 GroundSystem.py
```
## Historically included instructions for running on macOS or CentOS

These are NOT kept up-to-date, but included for historical reference (may be easier than starting from scratch)

### Installing and running cFS Ground System on macOS, using Homebrew
```
$ brew install pyqt
$ brew install zeromq
$ ( cd Subsystems/cmdUtil/ && make )
$ python GroundSystem.py
```
### Installing and running cFS Ground System on CentOS 6

#### Update yum
```
$ su
$ <type password="">
$ yum -y update</type>
```
#### Install pip and python-development ####
If you are on a 64-bit CentOS / RHEL based system:
```
$ wget <http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm>
$ rpm -ivh epel-release-6-8.noarch.rpm
```
If you are on a 32-bit CentOS / RHEL based system:
```
$ wget <http://download.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm>
$ rpm -ivh epel-release-6-8.noarch.rpm
$ yum install -y python-pip
$ yum install -y python-devel
```
#### Install zeroMQ and pyZMQ messaging system ####
```
$ yum install -y uuid-devel
$ yum install -y pkgconfig
$ yum install -y libtool
$ yum install -y gcc-c++
$ wget <http://download.zeromq.org/zeromq-4.0.5.tar.gz>
$ tar xzvf zeromq-4.0.5.tar.gz
$ cd zeromq-4.0.5
$ ./configure
$ make
$ make install
$ echo /usr/local/lib > /etc/ld.so.conf.d/local.conf
$ ldconfig
$ pip install pyzmq
```
#### Install pyQT4 ####
```
$ yum install -y PyQt4
$ yum install -y qt qt-demos qt-designer qt4 qt4-designer
```
#### Running Ground System ###
```
$ python GroundSystem.py
```

