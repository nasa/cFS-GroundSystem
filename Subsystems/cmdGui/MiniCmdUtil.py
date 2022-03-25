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

## This file is a Python implementation of a subset of functions in cmdUtil
## to support the GroundSystem GUI

import mmap
import socket
from collections import namedtuple


class MiniCmdUtil:
    # Class objects
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    type_signature = namedtuple("TypeSignature", 'byteLen, signed, endian')
    dataTypes = {
        ("b", "int8", "byte"): type_signature(1, True, None),
        ("m", "uint8"): type_signature(1, False, None),
        ("h", "int16", "half"): type_signature(2, True, None),
        ("n", "uint16"): type_signature(2, False, None),
        ("l", "int32", "long", "word"): type_signature(4, True, None),
        ("o", "uint32"): type_signature(4, False, None),
        ("q", "int64"): type_signature(8, True, None),
        ("p", "uint64"): type_signature(8, False, None),
        ("i", "int16b"): type_signature(2, True, "big"),
        ("j", "int32b"): type_signature(4, True, "big"),
        ("k", "int64b"): type_signature(8, True, "big"),
        ("w", "uint16b"): type_signature(2, False, "big"),
        ("x", "uint32b"): type_signature(4, False, "big"),
        ("y", "uint64b"): type_signature(8, False, "big")
    }

    def __init__(self,
                 host="127.0.0.1",
                 port=1234,
                 endian="BE",
                 pkt_id=0,
                 cmd_code=0,
                 parameters=None):

        self.host = host
        self.port = int(port)
        self.endian = "big" if endian == "BE" else "little"
        self.pkt_id = int(pkt_id, 16)
        self.cmd_code = int(cmd_code)
        self.parameters = parameters
        self.payload = bytearray()
        self.packet = bytearray()
        with open("/tmp/OffsetData", "r+b") as f:
            self.mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)

        self.cmd_offset_pri = 0
        self.cmd_offset_sec = 0
        self.checksum = 0xFF
        self.cfs_cmd_sec_hdr = bytearray(2)

    def assemble_pri_header(self):
        ccsds_pri = bytearray(6)
        ccsds_pri[:2] = self.pkt_id.to_bytes(2, byteorder='big')
        ccsds_pri[2:4] = (0xC000).to_bytes(2, byteorder='big')
        total_packet_len = len(ccsds_pri) + len(self.cfs_cmd_sec_hdr)
        self.assemble_payload()
        total_packet_len += len(self.payload)
        total_packet_len += self.cmd_offset_pri + self.cmd_offset_sec
        ccsds_pri[4:] = (total_packet_len - 7).to_bytes(2, byteorder="big")
        return ccsds_pri

    def assemble_payload(self):
        if self.parameters:
            param_list = self.parameters.split(" ")
            for param in param_list:
                items = param.split("=")  # e.g. ["--uint16", "2"]
                if "--string" not in param:  # non-string param
                    data_type = items[0].strip("-")  # Remove "--" prefix
                    data_val = int(items[1])
                    for key in self.dataTypes:  # Loop thru dictionary keys
                        if data_type in key:  # Check if e.g. "uint16" in key tuple
                            # Get the TypeSignature tuple
                            type_sig = self.dataTypes[key]
                            break  # Stop checking dictionary
                    # If TypeSignature endian is None, get the
                    # user-provided/default endian. Otherwise get
                    # the TypeSignature endian
                    endian = type_sig.endian or self.endian
                    # Convert to bytes of correct length, endianess, and sign
                    data_val_b = data_val.to_bytes(type_sig.byteLen,
                                                   byteorder=endian,
                                                   signed=type_sig.signed)
                    # Add data to payload bytearray
                    self.payload.extend(data_val_b)
                else:
                    string_params = items[1].strip("\"").split(
                        ":")  # e.g. ["16", "ES_APP"]
                    # Zero init'd bytearray of length e.g. 16
                    fixed_len_str = bytearray(int(string_params[0]))
                    string_b = string_params[1].encode(
                    )  # Param string to bytes
                    # Insert param bytes into front of bytearray
                    fixed_len_str[:len(string_b)] = string_b
                    # Add data to payload bytearray
                    self.payload.extend(fixed_len_str)

    def assemble_packet(self):
        self._get_offsets()
        pri_header = self.assemble_pri_header()
        self.packet.extend(pri_header)
        pri_offset = bytearray(self.cmd_offset_pri)
        self.packet.extend(pri_offset)
        self.cfs_cmd_sec_hdr[0] = self.cmd_code
        sec_offset = bytearray(self.cmd_offset_sec)
        for b in b''.join((pri_header, pri_offset, self.cfs_cmd_sec_hdr, sec_offset,
                           self.payload)):
            self.checksum ^= b
        self.cfs_cmd_sec_hdr[1] = self.checksum
        self.packet.extend(self.cfs_cmd_sec_hdr)
        self.packet.extend(sec_offset)
        self.packet.extend(self.payload)
        self.checksum = 0xFF

    def send_packet(self):
        self.assemble_packet()
        print("Data to send:")
        for i, v in enumerate(self.packet):
            print(f"0x{format(v, '02X')}", end=" ")
            if (i + 1) % 8 == 0:
                print()
        print()
        bytes_sent = self.sock.sendto(self.packet, (self.host, self.port))
        return bytes_sent > 0

    def _get_offsets(self):
        try:
            self.cmd_offset_pri = self.mm[1]
            self.cmd_offset_sec = self.mm[2]
        except ValueError:
            pass
