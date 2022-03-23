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
