/*
**      GSC-18128-1, "Core Flight Executive Version 6.6"
**
**      Copyright (c) 2006-2019 United States Government as represented by
**      the Administrator of the National Aeronautics and Space Administration.
**      All Rights Reserved.
**
**      Licensed under the Apache License, Version 2.0 (the "License");
**      you may not use this file except in compliance with the License.
**      You may obtain a copy of the License at
**
**        http://www.apache.org/licenses/LICENSE-2.0
**
**      Unless required by applicable law or agreed to in writing, software
**      distributed under the License is distributed on an "AS IS" BASIS,
**      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
**      See the License for the specific language governing permissions and
**      limitations under the License.
**
**      Udp packet send routine
*/

#include "SendUdp.h"

#ifdef WIN32
    #pragma warning (disable:4786)
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #include <windows.h>
    typedef int socklen_t;
#else
    #include <sys/types.h>
    #include <sys/socket.h>
    #include <arpa/inet.h>
    #include <netdb.h>
    #include <unistd.h>
    #include <ctype.h>
    #include <stdio.h>
    #include <string.h>
    #include <stdlib.h>
    #define SOCKET int
    #define closesocket(fd) close(fd)
#endif

/*
** SendUdp
*/
int SendUdp(char *hostname, char *portNum, char *packetData, int packetSize) {
    SOCKET              sd;
    int                 rc;
    int                 port;
    int                 errcode;
    unsigned int        i;
    struct sockaddr_in  cliAddr;
    struct addrinfo     hints;
    struct addrinfo     *result;

    #ifdef WIN32
        WSADATA  wsaData;
        WSAStartup(WINSOCK_VERSION, &wsaData);
    #endif

    if (hostname == NULL) {
        return -1;
    }
	
    /*
    ** Check port
    */
    port = atoi(portNum);
    if (port == -1) {
        return -2;
    }
    
    /*
    **Criteria for selecting socket address 
    */
    memset(&hints, 0, sizeof(struct addrinfo));
    hints.ai_family   = AF_INET; /*IPv4*/
    hints.ai_socktype = SOCK_DGRAM; /*Datagram socket*/
    hints.ai_flags    = AI_CANONNAME; 
    hints.ai_protocol = 0; /*Any Protocol*/
	
    errcode = getaddrinfo(hostname, portNum, &hints, &result);
    if (errcode != 0) {
        return -3;
    }

    printf("sending data to '%s' (IP : %s); port %d\n", result->ai_canonname,
        inet_ntoa(((struct sockaddr_in*)result->ai_addr)->sin_addr), port);

    /*
    ** Create Socket
    */
    sd = socket(AF_INET, SOCK_DGRAM, 0);

    if(sd < 0){
        return -4;
    }

    /*
    ** bind any port
    */
    cliAddr.sin_family = AF_INET;
    cliAddr.sin_addr.s_addr = htonl(INADDR_ANY);
    cliAddr.sin_port = htons(0);

    rc = bind(sd, (struct sockaddr *) &cliAddr, sizeof(cliAddr));
    if (rc < 0) {
        printf("%s: cannot bind port\n", portNum);
        return -5;
    }

    printf("Data to send:\n");
    i = 0;
    while (i < packetSize) {
        printf("0x%02X ", packetData[i] & 0xFF);
        if (++i % 8 == 0) {
            puts("");
        }
    }
    puts("");

    /*
    ** send the event
    */
    rc = sendto(sd, (char*)packetData, packetSize, 0, 
           result->ai_addr, result->ai_addrlen); 


    if (rc < 0) {
        freeaddrinfo(result);
        closesocket(sd);
        return -6;
    }

    freeaddrinfo(result);
    closesocket(sd);
    return 0;
}
