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

## This file is a Python implementation of a subset of functions in cmdUtil
## to support the GroundSystem GUI

import mmap
import socket
from collections import namedtuple


class MiniCmdUtil:
    ## Class objects
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    TypeSignature = namedtuple("TypeSignature", 'byteLen, signed, endian')
    dataTypes = {
        ("b", "int8", "byte"): TypeSignature(1, True, None),
        ("m", "uint8"): TypeSignature(1, False, None),
        ("h", "int16", "half"): TypeSignature(2, True, None),
        ("n", "uint16"): TypeSignature(2, False, None),
        ("l", "int32", "long", "word"): TypeSignature(4, True, None),
        ("o", "uint32"): TypeSignature(4, False, None),
        ("q", "int64"): TypeSignature(8, True, None),
        ("p", "uint64"): TypeSignature(8, False, None),
        ("i", "int16b"): TypeSignature(2, True, "big"),
        ("j", "int32b"): TypeSignature(4, True, "big"),
        ("k", "int64b"): TypeSignature(8, True, "big"),
        ("w", "uint16b"): TypeSignature(2, False, "big"),
        ("x", "uint32b"): TypeSignature(4, False, "big"),
        ("y", "uint64b"): TypeSignature(8, False, "big")
    }

    def __init__(self,
                 host="127.0.0.1",
                 port=1234,
                 endian="BE",
                 pktID=0,
                 cmdCode=0,
                 parameters=None):

        self.host = host
        self.port = int(port)
        self.endian = "big" if endian == "BE" else "little"
        self.pktID = int(pktID, 16)
        self.cmdCode = int(cmdCode)
        self.parameters = parameters
        self.payload = bytearray()
        self.packet = bytearray()
        with open("/tmp/OffsetData", "r+b") as f:
            self.mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)

        self.cmdOffsetPri = 0
        self.cmdOffsetSec = 0
        self.checksum = 0xFF
        self.cfsCmdSecHdr = bytearray(2)

    def assemblePriHeader(self):
        ccsdsPri = bytearray(6)
        ccsdsPri[:2] = self.pktID.to_bytes(2, byteorder='big')
        ccsdsPri[2:4] = (0xC000).to_bytes(2, byteorder='big')
        totalPacketLen = len(ccsdsPri) + len(self.cfsCmdSecHdr)
        self.assemblePayload()
        totalPacketLen += len(self.payload)
        totalPacketLen += self.cmdOffsetPri + self.cmdOffsetSec
        ccsdsPri[4:] = (totalPacketLen - 7).to_bytes(2, byteorder="big")
        return ccsdsPri

    def assemblePayload(self):
        if self.parameters:
            paramList = self.parameters.split(" ")
            for param in paramList:
                items = param.split("=")  ## e.g. ["--uint16", "2"]
                if "--string" not in param:  ## non-string param
                    dataType = items[0].strip("-")  ## Remove "--" prefix
                    dataVal = int(items[1])
                    for key in self.dataTypes:  ## Loop thru dictionary keys
                        if dataType in key:  ## Check if e.g. "uint16" in key tuple
                            ## Get the TypeSignature tuple
                            typeSig = self.dataTypes[key]
                            break  ## Stop checking dictionary
                    ## If TypeSignature endian is None, get the
                    ## user-provided/default endian. Otherwise get
                    ## the TypeSignature endian
                    endian = typeSig.endian or self.endian
                    ## Convert to bytes of correct length, endianess, and sign
                    dataValB = dataVal.to_bytes(typeSig.byteLen,
                                                byteorder=endian,
                                                signed=typeSig.signed)
                    ## Add data to payload bytearray
                    self.payload.extend(dataValB)
                else:
                    stringParams = items[1].strip("\"").split(
                        ":")  ## e.g. ["16", "ES_APP"]
                    ## Zero init'd bytearray of length e.g. 16
                    fixedLenStr = bytearray(int(stringParams[0]))
                    stringB = stringParams[1].encode(
                    )  ## Param string to bytes
                    ## Insert param bytes into front of bytearray
                    fixedLenStr[:len(stringB)] = stringB
                    ## Add data to payload bytearray
                    self.payload.extend(fixedLenStr)

    def assemblePacket(self):
        self._getOffsets()
        priHeader = self.assemblePriHeader()
        self.packet.extend(priHeader)
        priOffset = bytearray(self.cmdOffsetPri)
        self.packet.extend(priOffset)
        self.cfsCmdSecHdr[0] = self.cmdCode
        secOffset = bytearray(self.cmdOffsetSec)
        for b in b''.join((priHeader, priOffset, self.cfsCmdSecHdr, secOffset,
                           self.payload)):
            self.checksum ^= b
        self.cfsCmdSecHdr[1] = self.checksum
        self.packet.extend(self.cfsCmdSecHdr)
        self.packet.extend(secOffset)
        self.packet.extend(self.payload)
        self.checksum = 0xFF

    def sendPacket(self):
        self.assemblePacket()
        print("Data to send:")
        for i, v in enumerate(self.packet):
            print(f"0x{format(v, '02X')}", end=" ")
            if (i + 1) % 8 == 0:
                print()
        print()
        bytesSent = self.sock.sendto(self.packet, (self.host, self.port))
        return bytesSent > 0

    def _getOffsets(self):
        try:
            self.cmdOffsetPri = self.mm[1]
            self.cmdOffsetSec = self.mm[2]
        except ValueError:
            pass
