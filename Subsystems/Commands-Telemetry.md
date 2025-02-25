# Commands and Telemetry:

## Telemetry ( tlmGUI/ directory ):
Telemetry is sent from the running cFE/CFS as CCSDS telemetry packets encapsulated in 
UDP/IP packets. The `enable telemetry` command tells the TO_LAB application to start 
sending packets to a UDP port on the `localhost` or a specified IP. By default, the TO_LAB application
listens to UDP port 1234 for commands, and sends telemetry to the tlmGUI at UDP port 1235.

Start the telemetry system using the Ground System's main window.

Buttons are available for individual telemetry pages. 

New pages can be added by adding to the `telemetry-pages.txt` text file. 

The format is not very forgiving, and must be:
Description, Name of the Python class, Telemetry Message ID, packet definition file

Also, a corresponding telemetry packet definition file must be added.

For example: `cfe-es-hk-tlm.txt` is for the cFE Executive Services housekeeping packet. 
That file contains the information needed to decode and display each data
field of the packet. This is comma-delimited text, and has no error checking. 

### The fields are:

1. Field Description -- This is displayed on the GUI telemetry page

2. Byte offset in packet -- This is the starting byte for the data field

3. Length of data field in packet -- For integer types it must be 1, 2, or 4
                              For strings, the number of characters (such as 16)

4. Python type -- Python type for the field
* B = unsigned byte
* H = unsigned 16-bit integer
* I = unsigned 32-bit integer
* s = String

Notes: Floating point types are not supported yet, but are planned. Also the
type should match the length from #3 above.

See all of the types here:
http://docs.python.org/3/library/struct.html#format-characters

5. Display type -- This is how the data is displayed on the page
                    Dec = Decimal
                    Hex = Hexadecimal
                    Enm = Enumerated Type ( see next four fields )
                    Str = String

6. Enumerated type 0 -- This string is displayed if the display type is Enm
and the value is 0
                                              
7. Enumerated type 1 -- This string is displayed if the display type is Enm
and the value is 1

8. Enumerated type 2 -- This string is displayed if the display type is Enm
and the value is 2

9. Enumerated type 3 -- This string is displayed if the display type is Enm
and the value is 3

### What needs to be done:

1. Expand number of enumerated types

2. Provide some sort of optional data transformation

3. Implement floats

4. Be able to record/graph data? May be beyond the scope of this. 

# Commands (cmdGUI/ directory)

This is a simple Python / QT based Command GUI for the cmdUtil utility. 
It provides a list of "command pages" with a list of commands to send to a subsystem.

Start the command system using the Ground System's main window.

The dialogs were created in the QT designer program, and converted to Python classes
using the "pyuic5" utility:

```
pyuic5 -o MyDialog.py MyDialog.ui
```

The list of pages along with the AppID and address for each page is defined in the
file `command-pages.txt`.

Each command page has a list of subsystem commands in the text files. For example, 
ES is in `cfe-es-cmds.txt`.

This first release of the program does not allow editing of the command parameters 
in the GUI. This would be really helpful for on-the-fly commanding (when you 
want to do something like delete an app, and specify the app name in a dialog.)

There is the possibility to implement multiple command interfaces using
the Python class parameter that is passed in. For example, a copy of
`UdpCommands.py` could be made, which would allow the commands to be sent
over an Xbee RF radio, or TCP connection.

The subsystem commands `cfe-es-cmds.txt` are interface-agnostic, so
they can be reused.
