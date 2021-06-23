# Command to start the test application
#  CFE_ES_START_APP_CC = 4
#
# typedef struct CFE_ES_StartAppCmd_Payload
# {
#      char Application[CFE_MISSION_MAX_API_LEN]; //CFE_MISSION_MAX_API_LEN = 20
#      char AppEntryPoint[CFE_MISSION_MAX_API_LEN];
#      char AppFileName[CFE_MISSION_MAX_PATH_LEN]; //CFE_MISSION_MAX_PATH_LEN = 64
#      CFE_ES_MemOffset_t StackSize; //uint32
#      CFE_ES_ExceptionAction_Enum_t ExceptionAction; //uint8
#      undocumented SPARE uint8
#      CFE_ES_TaskPriority_Atom_t Priority; //uint16
# } CFE_ES_StartAppCmd_Payload_t;

./cmdUtil --pktid=0x1806 --cmdcode=4 --endian=LE --string="20:CFE_TEST_APP" --string="20:CFE_TestMain" \
          --string="64:cfe_testcase" --uint32=16384 --uint8=0 --uint8=0 --uint16=100
