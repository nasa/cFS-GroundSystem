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
 * Command utility. This program will build a Command packet
 * with variable parameters and send it on a UDP network socket.
 * this program is primarily used to command a cFS flight software system.
 */

/* System define for endian functions */
#define _BSD_SOURCE
#define _DEFAULT_SOURCE

/*
 * System includes
 */
#include <stdio.h>
#include <stdlib.h>
#include <endian.h>
#include <getopt.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <errno.h>
#include "SendUdp.h"

/*
 * Defines
 */

/* Max sizes */
#define MAX_HOSTNAME_SIZE 32   /* Maximum host name string size */
#define MAX_PORT_SIZE     16   /* Maximum port number string size */
#define MAX_ENDIAN_SIZE   3    /* Maximum endian string size */
#define MAX_PACKET_SIZE   1024 /* Max packet size, ref: CCSDS max = 65542, IPv4 UDP max = 65507 */

/* Protocol names - for interpreting protocol argument */
#define PROTOCOL_CCSDS_PRI "ccsdspri" /* CCSDS Primary header only */
#define PROTOCOL_CCSDS_EXT "ccsdsext" /* CCSDS Primary and Extended header only */
#define PROTOCOL_CFS_V1    "cfsv1"    /* CCSDS Primary header and cFS command secondary header */
#define PROTOCOL_CFS_V2    "cfsv2"    /* CCSDS Primary, Extended header, and cFS command secondary header */
#define PROTOCOL_RAW       "raw"      /* No predefined header */

/* Endian strings - related to MAX_ENDIAN_SIZE, don't exceed */
#define ENDIAN_BIG    "BE"
#define ENDIAN_LITTLE "LE"

/* Destination default values */
#define DEFAULT_HOSTNAME "127.0.0.1" /* Local host */
#define DEFAULT_PORT     "1234"      /* Default cFS cpu1 port */

/*
 * Packet default values
 * NOTE: Defaulting for backwards compatibility, make sure values match protocol or override in cmd line
 */
#define DEFAULT_PROTOCOL  PROTOCOL_CFS_V1 /* cFS version 1 default */
#define DEFAULT_BIGENDIAN true            /* Default to big endian */

#ifdef DEBUG
#define DEFAULT_VERBOSE true /* Print all messages if DEBUG defined */
#else
#define DEFAULT_VERBOSE false /* Quiet by default */
#endif

/*
 * Parameter datatype structure
 */
typedef struct
{
    char     HostName[MAX_HOSTNAME_SIZE];  /* Host name like "localhost" or "192.168.0.121" */
    char     PortNum[MAX_PORT_SIZE];       /* Port number */
    uint16_t CCSDS_Pri[3];                 /* CCSDS Primary Header (always big endian)
                                            * index  mask    ------------ description ----------------
                                            *   0   0xE000 : Packet Version number: CCSDS Version 1 = b000
                                            *   0   0x1000 : Packet Type:           0 = TLM, 1 = CMD
                                            *   0   0x0800 : Sec Hdr Flag:          0 = absent, 1 = present
                                            *   0   0x07FF : Application Process Identifier
                                            *   1   0xC000 : Sequence Flags:        b00 = continuation
                                            *                                       b01 = first segment
                                            *                                       b10 = last segment
                                            *                                       b11 = unsegmented
                                            *   1   0x3FFF : Packet Sequence Count or Packet Name
                                            *   2   0xFFFF : Packet Data Length: (total packet length) - 7
                                            */
    uint16_t CCSDS_Ext[2];                 /* CCSDS Extended Header (always big endian)
                                            * index  mask    ------------ description ----------------
                                            *   0   0xF800 : EDS Version for packet definition used
                                            *   0   0x0400 : Endian:        Big = 0, Little (Intel) = 1
                                            *   0   0x0200 : Playback flag: 0 = original, 1 = playback
                                            *   0   0x01FF : APID Qualifier (Subsystem Identifier)
                                            *   1   0xFFFF : APID Qualifier (System Identifier)
                                            */
    uint16_t CFS_CmdSecHdr;                /* cFS standard secondary command header (always big endian)
                                            * index  mask    ------------ description ----------------
                                            *   0   0x8000 : Reserved
                                            *   0   0x7F00 : Command Function Code
                                            *   1   0x00FF : Command Checksum
                                            */
    bool          BigEndian;               /* Endian default, false means little endian */
    bool          Verbose;                 /* Verbose option */
    bool          IncludeCCSDSPri;         /* Include CCSDS Primary Header */
    bool          IncludeCCSDSExt;         /* Include CCSDS Secondary Header */
    bool          IncludeCFSSec;           /* Include cFS Command Secondary Header */
    bool          OverridePktType;         /* Override packet type field */
    bool          OverridePktSec;          /* Override packet secondary header exists field */
    bool          OverridePktSeqFlg;       /* Override packet sequence flags */
    bool          OverridePktLen;          /* Override packet length field */
    bool          OverridePktEndian;       /* Override packet endian field */
    bool          OverridePktCksum;        /* Override packet checksum */
    unsigned char Packet[MAX_PACKET_SIZE]; /* Data packet to send */
} CommandData_t;

/*
 * getopts parameter passing options string
 */
static const char *optString = "A:B:C:D:E:F:G:H:I:J:L:P:Q:R:S:T:U:V:Y:b:d:f:h:i:j:k:l:m:n:o:p:q:s:vw:x:y:?";

/*
 * getopts_long long form argument table
 */
static struct option longOpts[] = {{"pktapid", required_argument, NULL, 'A'},
                                   {"pktpb", required_argument, NULL, 'B'},
                                   {"cmdcode", required_argument, NULL, 'C'},
                                   {"pktfc", required_argument, NULL, 'C'},
                                   {"pktedsver", required_argument, NULL, 'D'},
                                   {"endian", required_argument, NULL, 'E'},
                                   {"pktseqflg", required_argument, NULL, 'F'},
                                   {"pktname", required_argument, NULL, 'G'},
                                   {"pktseqcnt", required_argument, NULL, 'G'},
                                   {"host", required_argument, NULL, 'H'},
                                   {"pktid", required_argument, NULL, 'I'},
                                   {"pktendian", required_argument, NULL, 'J'},
                                   {"pktlen", required_argument, NULL, 'L'},
                                   {"port", required_argument, NULL, 'P'},
                                   {"protocol", required_argument, NULL, 'Q'},
                                   {"pktcksum", required_argument, NULL, 'R'},
                                   {"pktsec", required_argument, NULL, 'S'},
                                   {"pkttype", required_argument, NULL, 'T'},
                                   {"pktsubsys", required_argument, NULL, 'U'},
                                   {"pktver", required_argument, NULL, 'V'},
                                   {"pktsys", required_argument, NULL, 'Y'},
                                   {"byte", required_argument, NULL, 'b'},
                                   {"int8", required_argument, NULL, 'b'},
                                   {"double", required_argument, NULL, 'd'},
                                   {"float", required_argument, NULL, 'f'},
                                   {"half", required_argument, NULL, 'h'},
                                   {"int16", required_argument, NULL, 'h'},
                                   {"int16b", required_argument, NULL, 'i'},
                                   {"int32b", required_argument, NULL, 'j'},
                                   {"int64b", required_argument, NULL, 'k'},
                                   {"long", required_argument, NULL, 'l'},
                                   {"word", required_argument, NULL, 'l'},
                                   {"int32", required_argument, NULL, 'l'},
                                   {"uint8", required_argument, NULL, 'm'},
                                   {"uint16", required_argument, NULL, 'n'},
                                   {"uint32", required_argument, NULL, 'o'},
                                   {"uint64", required_argument, NULL, 'p'},
                                   {"int64", required_argument, NULL, 'q'},
                                   {"string", required_argument, NULL, 's'},
                                   {"verbose", no_argument, NULL, 'v'},
                                   {"uint16b", required_argument, NULL, 'w'},
                                   {"uint32b", required_argument, NULL, 'x'},
                                   {"uint64b", required_argument, NULL, 'y'},
                                   {"help", no_argument, NULL, '?'},
                                   {0, 0, 0, 0}};

/*******************************************************************************
 * Display program usage, and exit.
 */
void DisplayUsage(char *Name)
{
    char endian[] = ENDIAN_LITTLE;

    if (DEFAULT_BIGENDIAN)
        strcpy(endian, ENDIAN_BIG);

    printf("%s -- Command Client.\n", Name);
    printf("  - General options:\n");
    printf("    -v, --verbose: Extra output\n");
    printf("    -?, --help: print options and exit\n");
    printf("  - Destination options:\n");
    printf("    -H, --host: Destination hostname or IP address (Default = %s)\n", DEFAULT_HOSTNAME);
    printf("    -P, --port: Destination port (default = %s)\n", DEFAULT_PORT);
    printf("  - Packet format options:\n");
    printf("    -E, --endian: Default endian for unnamed fields/payload: [%s|%s] (default = %s)\n", ENDIAN_BIG,
           ENDIAN_LITTLE, endian);
    printf("    -Q, --protocol: Sets allowed named fields and header layout (default = %s)\n", DEFAULT_PROTOCOL);
    printf("        %8s = no predefined fields/layout\n", PROTOCOL_RAW);
    printf("        %8s = CCSDS Pri header only\n", PROTOCOL_CCSDS_PRI);
    printf("        %8s = CCSDS Pri and Ext headers\n", PROTOCOL_CCSDS_EXT);
    printf("        %8s = CCSDS Pri and cFS Cmd Sec headers\n", PROTOCOL_CFS_V1);
    printf("        %8s = CCSDS Pri, Ext, and cFS Cmd Sec headers\n", PROTOCOL_CFS_V2);
    printf("  - CCSDS Primary Header named fields (protocol=[%s|%s|%s|%s])\n", PROTOCOL_CCSDS_PRI, PROTOCOL_CCSDS_EXT,
           PROTOCOL_CFS_V1, PROTOCOL_CFS_V2);
    printf("    -I, --pktid: macro for setting first 16 bits of CCSDS Primary header\n");
    printf("    -V, --pktver: Packet version number (range=0-0x7)\n");
    printf("    -T, --pkttype: !OVERRIDE! Packet type (default is cmd, 0=tlm, 1=cmd)\n");
    printf("    -S, --pktsec: !OVERRIDE! Secondary header flag (default set from protocol, 0=absent, 1=present)\n");
    printf("    -A, --pktapid: Application Process Identifier (range=0-0x7FF)\n");
    printf("    -F, --pktseqflg: !OVERRIDE! Sequence Flags (default unsegmented, 0=continuation, 1=first, 2=last, "
           "3=unsegmented)\n");
    printf("    -G, --pktseqcnt, --pktname: Packet sequence count or Packet name (range=0-0x3FFF)\n");
    printf("    -L, --pktlen: !OVERRIDE! Packet data length (default will calculate value, range=0-0xFFFF)\n");
    printf("  - CCSDS Extended Header named fields (protocol=[%s|%s])\n", PROTOCOL_CCSDS_EXT, PROTOCOL_CFS_V2);
    printf("    -D, --pktedsver: EDS version (range=0-0x1F)\n");
    printf("    -J, --pktendian: !OVERRIDE! Endian (default uses endian, 0=big, 1=little(INTEL))\n");
    printf("    -B, --pktpb: Playback field (0=original, 1=playback)\n");
    printf("    -U, --pktsubsys: APID Qualifier Subsystem (range=0-0x1FF)\n");
    printf("    -Y, --pktsys: APID Qualifier System (range=0-0xFFFF)\n");
    printf("  - cFS Command Secondary Header named fields (protocol=[%s|%s])\n", PROTOCOL_CFS_V1, PROTOCOL_CFS_V2);
    printf("    -C, --pktfc, --cmdcode: Command function code (range=0-0x7F)\n");
    printf("    -R, --pktcksum: !OVERRIDE! Packet checksum (default will calculate value, range=0-0xFF)\n");
    printf("  - Raw values converted to selected endian where applicable\n");
    printf("    -b, --int8, --byte: Signed 8 bit int (range=-127-127)\n");
    printf("    -m, --uint8: Unsigned 8 bit int (range=0-0xFF)\n");
    printf("    -h, --int16, --half: Signed 16 bit int (range=-32767-32767)\n");
    printf("    -n, --uint16: Unsigned 16 bit int (range=0-0xFFFF)\n");
    printf("    -l, --int32, --long, --word: Signed 32 bit int (range=-2147483647-2147483647)\n");
    printf("    -o, --uint32: Unsigned 32 bit int (range=0-0xFFFFFFFF)\n");
    printf("    -q, --int64: Signed 64 bit int (range=-9223372036854775807-9223372036854775807)\n");
    printf("    -p, --uint64: Unsigned 64 bit int (range=0-0xFFFFFFFFFFFFFFFF)\n");
    printf("    -d, --double: Double format (caution - host format w/ converted endian, may not match target)\n");
    printf("    -f, --float: Float format (caution - host format w/ converted endian, may not match target)\n");
    printf("    -s, --string: Fixed length string, NNN:String where NNN is fixed length (0 padded)\n");
    printf("  - Raw values always big endian (even if endian=%s)\n", ENDIAN_LITTLE);
    printf("    -i, --int16b: Big endian signed 16 bit int (range=-32767-32767)\n");
    printf("    -j, --int32b: Big endian signed 32 bit int (range=-2147483647-2147483647)\n");
    printf("    -k, --int64b: Big endian signed 64 bit int (range=-9223372036854775807-9223372036854775807)\n");
    printf("    -w, --uint16b: Big endian unsigned 16 bit int (range=0-0xFFFF)\n");
    printf("    -x, --uint32b: Big endian unsigned 32 bit int (range=0-0xFFFFFFFF)\n");
    printf("    -y, --uint64b: Big endian unsigned 64 bit int (range=0-0xFFFFFFFFFFFFFFFF)\n");
    printf(" \n");
    printf("Examples:\n");
    printf("  ./cmdUtil --host=localhost --port=1234 --pktid=0x1803 --pktfc=3 --int16=100 --string=16:ES_APP\n");
    printf("  ./cmdUtil -ELE -C2 -A6 -n2 # Processor reset on little endian, using defaults\n");
    printf("  ./cmdUtil --endian=LE --protocol=raw --uint64b=0x1806C000000302DD --uint16=2\n");
    printf("  ./cmdUtil --pktver=1 --pkttype=0 --pktsec=0 --pktseqflg=2 --pktlen=0xABC --pktcksum=0\n");
    printf(
        "  ./cmdUtil -Qcfsv2 --pktedsver=0xA --pktendian=1 --pktpb=1 --pktsubsys=0x123 --pktsys=0x4321 --pktfc=0xB\n");
    printf(" \n");
    exit(EXIT_SUCCESS);
}

/*******************************************************************************
 * Set the header booleans based on protocol selection
 */
void SetProtocol(CommandData_t *cmd, const char *protocol)
{

    if (protocol == NULL || cmd == NULL)
    {
        fprintf(stderr, "ERROR: %s:%u - null input, exiting\n", __func__, __LINE__);
        exit(EXIT_FAILURE);
    }

    /* Clear any default setting */
    cmd->IncludeCCSDSPri = false;
    cmd->IncludeCCSDSExt = false;
    cmd->IncludeCFSSec   = false;

    if (strcmp(protocol, PROTOCOL_CCSDS_PRI) == 0)
    {
        cmd->IncludeCCSDSPri = true;
    }
    else if (strcmp(protocol, PROTOCOL_CCSDS_EXT) == 0)
    {
        cmd->IncludeCCSDSPri = true;
        cmd->IncludeCCSDSExt = true;
    }
    else if (strcmp(protocol, PROTOCOL_CFS_V1) == 0)
    {
        cmd->IncludeCCSDSPri = true;
        cmd->IncludeCFSSec   = true;
    }
    else if (strcmp(protocol, PROTOCOL_CFS_V2) == 0)
    {
        cmd->IncludeCCSDSPri = true;
        cmd->IncludeCCSDSExt = true;
        cmd->IncludeCFSSec   = true;
    }
    else if (strcmp(protocol, PROTOCOL_RAW) != 0)
    {
        fprintf(stderr, "ERROR: %s:%u - Invalid protocol: %s\n", __func__, __LINE__, protocol);
        exit(EXIT_FAILURE);
    }

    if (cmd->Verbose)
        printf("%s:%u - Protocol selected: %s\n", __func__, __LINE__, protocol);
}

/*******************************************************************************
 * Process string protocol field
 *  - updates orig masked bits with big endian in masked/shifted
 *  - in = input string(unshifted)
 *  - mask = value mask, also used to calculate shift
 *  - fieldexists = process helper, returns if false
 */
void ProcessField(uint16_t *orig, const char *in, const uint16_t mask, bool fieldexists)
{
    long int     templong;
    unsigned int shift = 0;
    char *       tail  = NULL;

    /* Check for null pointer */
    if (in == NULL)
    {
        fprintf(stderr, "ERROR: %s:%u - Null string input\n", __func__, __LINE__);
        exit(EXIT_FAILURE);
    }

    /* Check for bad mask */
    if (mask == 0)
    {
        fprintf(stderr, "ERROR: %s:%u - Zero mask returns 0\n", __func__, __LINE__);
        exit(EXIT_FAILURE);
    }

    /* Check if protocol includes field */
    if (!fieldexists)
    {
        fprintf(stderr, "ERROR: %s:%u - Field does not exist for selected protocol: %s\n", __func__, __LINE__, in);
        exit(EXIT_FAILURE);
    }

    /* Find shift from mask (already checked for non-zero) */
    while (((mask >> shift) & 0x1) == 0)
    {
        shift++;
    }

    errno    = 0;
    templong = strtoul(in, &tail, 0);
    if (errno != 0)
    {
        fprintf(stderr, "ERROR: %s:%u - String conversion (%s): %s\n", __func__, __LINE__, in, strerror(errno));
        exit(EXIT_FAILURE);
    }

    if (strlen(tail))
    {
        fprintf(stderr, "ERROR: %s:%u - Trailing characters (%s) in parameter %s\n", __func__, __LINE__, tail, in);
        exit(EXIT_FAILURE);
    }

    templong <<= shift;
    if ((templong & ~mask) != 0)
    {
        fprintf(stderr, "ERROR: %s:%u - Parameter 0x%lX (%s<<%u) exceeds mask 0x%X\n", __func__, __LINE__, templong, in,
                shift, mask);
        exit(EXIT_FAILURE);
    }

    *orig = htobe16((be16toh(*orig) & ~mask) | (templong & mask));
}

/******************************************************************************
 * Copy data into packet buffer
 */
void CopyData(unsigned char *pkt, unsigned int *startbyte, char *in, unsigned int nbytes)
{

    /* Ensure space */
    if ((*startbyte + nbytes) > MAX_PACKET_SIZE)
    {
        fprintf(stderr, "ERROR %s:%u - Exceeded packet size, startbyte = %u, nbytes = %u, max = %u\n", __func__,
                __LINE__, *startbyte, nbytes, MAX_PACKET_SIZE);
        exit(EXIT_FAILURE);
    }

    /* Copy data into packet buffer and move start byte */
    memcpy(&pkt[*startbyte], in, nbytes);
    *startbyte += nbytes;
}

/******************************************************************************
 * Calculate cFS Secondary Header Checksum
 * Note - this matches cFS checksum calc in framework
 */
unsigned char CalcChecksum(unsigned char *bbuf, unsigned int nbytes)
{
    unsigned char checksum = 0xFF;

    for (unsigned int i = 0; i < nbytes; i++)
        checksum ^= bbuf[i];

    return checksum;
}

/******************************************************************************
 * Constructs packets given inputs and sends over UDP
 */
int main(int argc, char *argv[])
{
    int                    opt       = 0;
    int                    longIndex = 0;
    unsigned int           startbyte = 0;
    unsigned int           pktnbytes = 0;
    unsigned int           i;
    char                   sbuf[MAX_PACKET_SIZE];
    char *                 tail = NULL;
    long long int          templl;
    long long unsigned int tempull;
    int8_t                 tempint8;
    uint8_t                tempuint8;
    int16_t                tempint16;
    uint16_t               tempuint16;
    int32_t                tempint32;
    uint32_t               tempuint32;
    int64_t                tempint64;
    uint64_t               tempuint64;
    double                 tempd;
    float                  tempf;
    bool                   forcebigendian;
    CommandData_t          cmd;
    int                    status;

    /*
     * Initialize the cmd struct
     */
    memset(&(cmd), 0, sizeof(cmd));

    /* Set defaults */
    strncpy(cmd.HostName, DEFAULT_HOSTNAME, MAX_HOSTNAME_SIZE - 1);
    strncpy(cmd.PortNum, DEFAULT_PORT, MAX_PORT_SIZE - 1);
    cmd.BigEndian = DEFAULT_BIGENDIAN;
    cmd.Verbose   = DEFAULT_VERBOSE;
    SetProtocol(&cmd, DEFAULT_PROTOCOL);

    /* Process general options first, protocol is critical for checking */
    while ((opt = getopt_long(argc, argv, optString, longOpts, &longIndex)) != -1)
    {
        switch (opt)
        {
            case 'H': /* host */
                strncpy(cmd.HostName, optarg, MAX_HOSTNAME_SIZE - 1);
                if (strcmp(cmd.HostName, optarg) != 0)
                {
                    fprintf(stderr, "ERROR: %s:%u - Trucating host name: %s -> %s\n", __func__, __LINE__, optarg,
                            cmd.HostName);
                    exit(EXIT_FAILURE);
                }
                break;

            case 'P': /* port */
                strncpy(cmd.PortNum, optarg, MAX_PORT_SIZE - 1);
                if (strcmp(cmd.PortNum, optarg) != 0)
                {
                    fprintf(stderr, "ERROR: %s:%u - Trucating port number: %s -> %s\n", __func__, __LINE__, optarg,
                            cmd.HostName);
                    exit(EXIT_FAILURE);
                }
                break;

            case 'v': /* verbose */
                cmd.Verbose = true;
                break;

            case 'E': /* endian */
                if (strcmp(optarg, ENDIAN_LITTLE) == 0)
                {
                    cmd.BigEndian = false;
                }
                else if (strcmp(optarg, ENDIAN_BIG) == 0)
                {
                    cmd.BigEndian = true;
                }
                else
                {
                    fprintf(stderr, "ERROR: %s:%u - Unrecognized endian selection: %s\n", __func__, __LINE__, optarg);
                    exit(EXIT_FAILURE);
                }
                break;

            case 'Q': /* protocol */
                SetProtocol(&cmd, optarg);
                break;

            case '?': /* help */
                DisplayUsage(argv[0]);
                break;

            default:
                break;
        }
    }

    /* Reset op list for protocol field processing */
    optind = 1;

    /* Process protocol field options */
    while ((opt = getopt_long(argc, argv, optString, longOpts, &longIndex)) != -1)
    {
        switch (opt)
        {
            /* CCSDS Primary fields */
            case 'I': /* pktid */
                ProcessField(&cmd.CCSDS_Pri[0], optarg, 0xFFFF, cmd.IncludeCCSDSPri);
                break;

            case 'V': /* pktver */
                ProcessField(&cmd.CCSDS_Pri[0], optarg, 0xE000, cmd.IncludeCCSDSPri);
                break;

            case 'T': /* pkttype */
                ProcessField(&cmd.CCSDS_Pri[0], optarg, 0x1000, cmd.IncludeCCSDSPri);
                cmd.OverridePktType = true;
                break;

            case 'S': /* pktsec */
                ProcessField(&cmd.CCSDS_Pri[0], optarg, 0x0800, cmd.IncludeCCSDSPri);
                cmd.OverridePktSec = true;
                break;

            case 'A': /* pktapid */
                ProcessField(&cmd.CCSDS_Pri[0], optarg, 0x07FF, cmd.IncludeCCSDSPri);
                break;

            case 'F': /* pktseqflg */
                ProcessField(&cmd.CCSDS_Pri[1], optarg, 0xC000, cmd.IncludeCCSDSPri);
                cmd.OverridePktSeqFlg = true;
                break;

            case 'G': /* pktseqcnt */
                ProcessField(&cmd.CCSDS_Pri[1], optarg, 0x3FFF, cmd.IncludeCCSDSPri);
                break;

            case 'L': /* pktlen */
                ProcessField(&cmd.CCSDS_Pri[2], optarg, 0xFFFF, cmd.IncludeCCSDSPri);
                cmd.OverridePktLen = true;
                break;

            /* CCSDS Extended fields */
            case 'D': /* pktedsver */
                ProcessField(&cmd.CCSDS_Ext[0], optarg, 0xF800, cmd.IncludeCCSDSExt);
                break;

            case 'J': /* pktendian */
                ProcessField(&cmd.CCSDS_Ext[0], optarg, 0x0400, cmd.IncludeCCSDSExt);
                cmd.OverridePktEndian = true;
                break;

            case 'B': /* pktpb */
                ProcessField(&cmd.CCSDS_Ext[0], optarg, 0x0200, cmd.IncludeCCSDSExt);
                break;

            case 'U': /* pktsubsys */
                ProcessField(&cmd.CCSDS_Ext[0], optarg, 0x01FF, cmd.IncludeCCSDSExt);
                break;

            case 'Y': /* pktsys */
                ProcessField(&cmd.CCSDS_Ext[1], optarg, 0xFFFF, cmd.IncludeCCSDSExt);
                break;

            /* CFS Secondary fields */
            case 'C': /* pktfc */
                ProcessField(&cmd.CFS_CmdSecHdr, optarg, 0x7F00, cmd.IncludeCFSSec);
                break;

            case 'R': /* pktcksum */
                ProcessField(&cmd.CFS_CmdSecHdr, optarg, 0x00FF, cmd.IncludeCFSSec);
                cmd.OverridePktCksum = true;
                break;

            default:
                break;
        }
    }

    /* Print arguments (useful when debugging internal call) */
    if (cmd.Verbose)
    {
        printf("Call echo:\n");
        for (i = 0; i < argc; i++)
        {
            printf(" %s", argv[i]);
        }
        printf("\n");
    }

    /* Calculate data start byte, these get copied over later */
    if (cmd.IncludeCCSDSPri)
        startbyte += sizeof(cmd.CCSDS_Pri);
    if (cmd.IncludeCCSDSExt)
        startbyte += sizeof(cmd.CCSDS_Ext);
    if (cmd.IncludeCFSSec)
        startbyte += sizeof(cmd.CFS_CmdSecHdr);

    /* Round up to account for padding */
    startbyte += startbyte % 8;

    if (cmd.Verbose)
    {
        printf("Payload start byte = %u\n", startbyte);
    }

    /* Reset op list for payload processing */
    optind = 1;

    /* Process payload options */
    while ((opt = getopt_long(argc, argv, optString, longOpts, &longIndex)) != -1)
    {
        errno          = 0;
        forcebigendian = false;
        switch (opt)
        {
            /* Payload parameters in configured endian */
            case 'b': /* int8 */
                templl   = strtoll(optarg, &tail, 0);
                tempint8 = templl;
                if (tempint8 != templl)
                {
                    fprintf(stderr, "ERROR %s:%u - Parameter not int8 %lld -> %d\n", __func__, __LINE__, templl,
                            tempint8);
                    exit(EXIT_FAILURE);
                }
                CopyData(cmd.Packet, &startbyte, (char *)&tempint8, sizeof(tempint8));
                break;

            case 'm': /* uint8 */
                tempull   = strtoull(optarg, &tail, 0);
                tempuint8 = tempull;
                if (tempuint8 != tempull)
                {
                    fprintf(stderr, "ERROR %s:%u - Parameter not uint8 %llu -> %u\n", __func__, __LINE__, tempull,
                            tempuint8);
                    exit(EXIT_FAILURE);
                }
                CopyData(cmd.Packet, &startbyte, (char *)&tempuint8, sizeof(tempuint8));
                break;

            case 'i': /* int16b */
                forcebigendian = true;

            case 'h': /* int16 */
                templl    = strtoll(optarg, &tail, 0);
                tempint16 = templl;
                if (tempint16 != templl)
                {
                    fprintf(stderr, "ERROR %s:%u - Parameter not int16 %lld -> %d\n", __func__, __LINE__, templl,
                            tempint16);
                    exit(EXIT_FAILURE);
                }

                /* Endian conversion */
                if (cmd.BigEndian || forcebigendian)
                    tempint16 = htobe16(tempint16);
                else
                    tempint16 = htole16(tempint16);

                CopyData(cmd.Packet, &startbyte, (char *)&tempint16, sizeof(tempint16));
                break;

            case 'w': /* uint16b */
                forcebigendian = true;

            case 'n': /* uint16 */
                tempull    = strtoull(optarg, &tail, 0);
                tempuint16 = tempull;
                if (tempuint16 != tempull)
                {
                    fprintf(stderr, "ERROR %s:%u - Parameter not uint16 %llu -> %u\n", __func__, __LINE__, tempull,
                            tempuint16);
                    exit(EXIT_FAILURE);
                }

                /* Endian conversion */
                if (cmd.BigEndian || forcebigendian)
                    tempuint16 = htobe16(tempuint16);
                else
                    tempuint16 = htole16(tempuint16);

                CopyData(cmd.Packet, &startbyte, (char *)&tempuint16, sizeof(tempuint16));
                break;

            case 'j': /* int32b */
                forcebigendian = true;

            case 'l': /* int32 */
                templl    = strtoll(optarg, &tail, 0);
                tempint32 = templl;
                if (tempint32 != templl)
                {
                    fprintf(stderr, "ERROR %s:%u - Parameter not int32 %lld -> %d\n", __func__, __LINE__, templl,
                            tempint32);
                    exit(EXIT_FAILURE);
                }

                /* Endian conversion */
                if (cmd.BigEndian || forcebigendian)
                    tempint32 = htobe32(tempint32);
                else
                    tempint32 = htole32(tempint32);

                CopyData(cmd.Packet, &startbyte, (char *)&tempint32, sizeof(tempint32));
                break;

            case 'x': /* uint32b */
                forcebigendian = true;

            case 'o': /* uint32 */
                tempull    = strtoull(optarg, &tail, 0);
                tempuint32 = tempull;
                if (tempuint32 != tempull)
                {
                    fprintf(stderr, "ERROR %s:%u - Parameter not uint32 %llu -> %u\n", __func__, __LINE__, tempull,
                            tempuint32);
                    exit(EXIT_FAILURE);
                }

                /* Endian conversion */
                if (cmd.BigEndian || forcebigendian)
                    tempuint32 = htobe32(tempuint32);
                else
                    tempuint32 = htole32(tempuint32);

                CopyData(cmd.Packet, &startbyte, (char *)&tempuint32, sizeof(tempuint32));
                break;

            case 'k': /* int64b */
                forcebigendian = true;

            case 'q': /* int64 */
                templl    = strtoll(optarg, &tail, 0);
                tempint64 = templl;
                if (tempint64 != templl)
                {
                    fprintf(stderr, "ERROR %s:%u - Parameter not int64 %lld -> %lld\n", __func__, __LINE__, templl,
                            (long long int)tempint64);
                    exit(EXIT_FAILURE);
                }

                /* Endian conversion */
                if (cmd.BigEndian || forcebigendian)
                    tempint64 = htobe64(tempint64);
                else
                    tempint64 = htole64(tempint64);

                CopyData(cmd.Packet, &startbyte, (char *)&tempint64, sizeof(tempint64));
                break;

            case 'y': /* uint64b */
                forcebigendian = true;

            case 'p': /* uint64 */
                tempull    = strtoull(optarg, &tail, 0);
                tempuint64 = tempull;
                if (tempuint64 != tempull)
                {
                    fprintf(stderr, "ERROR %s:%u - Parameter not uint64 %llu -> %llu\n", __func__, __LINE__, tempull,
                            (unsigned long long int)tempuint64);
                    exit(EXIT_FAILURE);
                }

                /* Endian conversion */
                if (cmd.BigEndian || forcebigendian)
                    tempuint64 = htobe64(tempuint64);
                else
                    tempuint64 = htole64(tempuint64);

                CopyData(cmd.Packet, &startbyte, (char *)&tempuint64, sizeof(tempuint64));
                break;

            case 'f': /* float */
                tempf = strtof(optarg, &tail);
                memcpy(&tempint32, &tempf, sizeof(tempint32));

                /* Endian conversion */
                if (cmd.BigEndian)
                    tempint32 = htobe32(tempint32);
                else
                    tempint32 = htole32(tempint32);

                CopyData(cmd.Packet, &startbyte, (char *)&tempint32, sizeof(tempint32));
                break;

            case 'd': /* double */
                tempd = strtod(optarg, &tail);
                memcpy(&tempint64, &tempd, sizeof(tempint64));

                /* Endian conversion */
                if (cmd.BigEndian)
                    tempint64 = htobe64(tempint64);
                else
                    tempint64 = htole64(tempint64);

                CopyData(cmd.Packet, &startbyte, (char *)&tempint64, sizeof(tempint64));
                break;

            case 's': /* string */

                tempull = strtoull(optarg, &tail, 0);

                if ((tail[0] != ':') || (tempull == 0))
                {
                    fprintf(stderr, "ERROR: %s:%u - String format is NNN:string, not %s\n", __func__, __LINE__, optarg);
                    exit(EXIT_FAILURE);
                }

                /* Copy the data over (zero fills) */
                strncpy(sbuf, &tail[1], sizeof(sbuf) - 1);
                CopyData(cmd.Packet, &startbyte, sbuf, tempull);

                /* Reset tail so it doesn't trigger error */
                tail = NULL;
                break;

            default:
                break;
        }

        if (errno != 0)
        {
            fprintf(stderr, "ERROR: %s:%u - String conversion (%s): %s\n", __func__, __LINE__, optarg, strerror(errno));
            exit(EXIT_FAILURE);
        }

        if ((tail != NULL) && strlen(tail))
        {
            fprintf(stderr, "ERROR: %s:%u - Trailing characters (%s) in argument %s\n", __func__, __LINE__, tail,
                    optarg);
            exit(EXIT_FAILURE);
        }
    }

    /* Save packet length */
    pktnbytes = startbyte;

    /* Set non-overridden fields - PktType, PktSec, PktSeqFlg, PktLen, PktEndian */
    if (!cmd.OverridePktType)
        ProcessField(&cmd.CCSDS_Pri[0], "1", 0x1000, true);
    if (!cmd.OverridePktSec && cmd.IncludeCFSSec)
        ProcessField(&cmd.CCSDS_Pri[0], "1", 0x0800, true);
    if (!cmd.OverridePktSeqFlg)
        ProcessField(&cmd.CCSDS_Pri[1], "3", 0xC000, true);
    if (!cmd.OverridePktLen)
    {
        sprintf(sbuf, "%u", (uint16_t)(pktnbytes - 7));
        ProcessField(&cmd.CCSDS_Pri[2], sbuf, 0xFFFF, true);
    }
    if (!cmd.OverridePktEndian && !cmd.BigEndian)
    {
        ProcessField(&cmd.CCSDS_Ext[0], "1", 0x0400, true);
    }

    /* Copy selected header data (pre-checksum) */
    startbyte = 0;
    if (cmd.IncludeCCSDSPri)
        CopyData(cmd.Packet, &startbyte, (char *)cmd.CCSDS_Pri, sizeof(cmd.CCSDS_Pri));
    if (cmd.IncludeCCSDSExt)
        CopyData(cmd.Packet, &startbyte, (char *)cmd.CCSDS_Ext, sizeof(cmd.CCSDS_Ext));
    if (cmd.IncludeCFSSec)
        CopyData(cmd.Packet, &startbyte, (char *)&cmd.CFS_CmdSecHdr, sizeof(cmd.CFS_CmdSecHdr));

    /* Calculate checksum and insert into cFS Secondary header buffer if exists and not overridden */
    if (!cmd.OverridePktCksum && cmd.IncludeCFSSec)
    {
        sprintf(sbuf, "%u", CalcChecksum(cmd.Packet, pktnbytes));
        ProcessField(&cmd.CFS_CmdSecHdr, sbuf, 0x00FF, true);

        /* Copy secondary header buffer into packet buffer with checksum */
        startbyte = 0;
        if (cmd.IncludeCCSDSPri)
            startbyte += sizeof(cmd.CCSDS_Pri);
        if (cmd.IncludeCCSDSExt)
            startbyte += sizeof(cmd.CCSDS_Ext);
        CopyData(cmd.Packet, &startbyte, (char *)&cmd.CFS_CmdSecHdr, sizeof(cmd.CFS_CmdSecHdr));
    }

    if (cmd.Verbose)
        printf("Command checksum (cFS version): 0x%02X\n", CalcChecksum(cmd.Packet, pktnbytes));

    /* Echo command buffer */
    if (cmd.Verbose)
    {
        printf("Command Data:\n");
        for (i = 0; i < pktnbytes / 2; i++)
        {
            printf(" %02X%02X", cmd.Packet[i * 2], cmd.Packet[(i * 2) + 1]);
            if ((i > 0) && (i % 16 == 0))
                printf("\n");
        }
        if (pktnbytes % 2 != 0)
            printf(" %02X", cmd.Packet[pktnbytes]);
        printf("\n");
    }

    /* Send the packet */
    status = SendUdp(cmd.HostName, cmd.PortNum, cmd.Packet, pktnbytes);

    if (status < 0)
    {
        fprintf(stderr, "Problem sending UDP packet: %d\n", status);
        exit(EXIT_FAILURE);
    }

    return EXIT_SUCCESS;
}
