/************************************************************************
 * NASA Docket No. GSC-18,719-1, and identified as “core Flight System: Bootes”
 *
 * Copyright (c) 2020 United States Government as represented by the
 * Administrator of the National Aeronautics and Space Administration.
 * All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License. You may obtain
 * a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 ************************************************************************/

/*
 * Udp packet send routine
 */

#include "SendUdp.h"

#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/*
** SendUdp
*/
int SendUdp(char *hostname, char *portNum, unsigned char *packetData, int packetSize)
{
    int              sd;
    int              rc;
    int              port;
    unsigned int     i;
    struct addrinfo  hints;
    struct addrinfo *result;
    struct addrinfo *rp;
    char             hbuf[1025] = "UNKNOWN";

    if (hostname == NULL)
    {
        return -1;
    }

    /*
    ** Check port
    */
    port = atoi(portNum);
    if (port == -1)
    {
        return -2;
    }

    /*
    **Criteria for selecting socket address
    */
    memset(&hints, 0, sizeof(hints));
    hints.ai_family   = AF_INET;    /*IPv4*/
    hints.ai_socktype = SOCK_DGRAM; /*Datagram socket*/
    hints.ai_flags    = AI_CANONNAME;
    hints.ai_protocol = 0; /*Any Protocol*/

    rc = getaddrinfo(hostname, portNum, &hints, &result);
    if (rc != 0)
    {
        return -3;
    }

    /* Loop through potential addresses until successful socket/connect */
    for (rp = result; rp != NULL; rp = rp->ai_next)
    {
        sd = socket(rp->ai_family, rp->ai_socktype, rp->ai_protocol);

        if (sd == -1)
            continue;

        if (connect(sd, rp->ai_addr, rp->ai_addrlen) != -1)
            break; /* Success */

        close(sd);
    }

    if (rp == NULL)
    {
        freeaddrinfo(result);
        return -4;
    }

    getnameinfo(rp->ai_addr, rp->ai_addrlen, hbuf, sizeof(hbuf), NULL, 0, NI_NUMERICHOST);
    printf("sending data to '%s' (IP : %s); port %d\n", rp->ai_canonname, hbuf, port);

    freeaddrinfo(result);

    printf("Data to send:\n");
    i = 0;
    while (i < packetSize)
    {
        printf("0x%02X ", packetData[i] & 0xFF);
        if (++i % 8 == 0)
        {
            puts("");
        }
    }
    puts("");

    /*
    ** send the event
    */
    rc = send(sd, (char *)packetData, packetSize, 0);

    close(sd);

    if (rc != packetSize)
    {
        return -6;
    }

    return 0;
}
