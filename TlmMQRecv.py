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

import zmq


#
# Receive zeroMQ messages (used for debugging only - not used by CFS Ground System)
#
def main():
    """ main method """

    # Prepare our context and publisher
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect("ipc:///tmp/GroundSystem")
    subscriber.setsockopt(zmq.SUBSCRIBE, b"GroundSystem")

    while True:
        try:
            # Read envelope with address
            address, contents = subscriber.recv_multipart()
            print(f"[{address}] {contents}")
        except KeyboardInterrupt:
            break

    # We never get here but clean up anyhow
    subscriber.close()
    context.term()


if __name__ == "__main__":
    main()
