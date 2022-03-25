#!/usr/bin/env python3

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

#
# Send UDP messages for debugging (not used by Ground System)
#
import time
import socket

#
# Main
#
if __name__ == "__main__":
    num = 0
    while True:
        num += 1
        time.sleep(1)
        # send_host = "10.1.57.37"
        send_host = "127.0.0.1"
        # send_host = "192.168.1.4"
        send_port = 1235
        datagram = b'Test tlm message'
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        send_socket.sendto(datagram, (send_host, send_port))
        print(f'Sent msg #{num} to {send_host}:{send_port}')
