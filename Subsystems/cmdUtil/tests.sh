echo TEST: Empty
./cmdUtil
echo
echo TEST: Missing parameter
./cmdUtil --pktid
echo
echo TEST: Trailing characters
./cmdUtil --pktid=6t
echo
echo TEST: Field does not exist
./cmdUtil -v --protocol=raw --pktid=0xABCD
echo
echo TEST: Bad protocol
./cmdUtil -v -Qsilly
echo
echo TEST: Bad endian
./cmdUtil -v -ELEB
echo
echo TEST: Param too big for mask
./cmdUtil --pktid=0x1FFFF
echo
echo TEST: Param to big for convert x3
./cmdUtil --pktid=0x123456789
./cmdUtil --pktid=4294967296
./cmdUtil --pktid=-2147483648
echo
echo TEST: Param too big w/ shift
./cmdUtil --pktver=8
echo
echo TEST: Payload too big x2
./cmdUtil --uint8=0xFFF
./cmdUtil --int8=200
echo
echo TEST: Payload trailing
./cmdUtil --int8=16yyy
echo
echo TEST: Big and little endian float
./cmdUtil --protocol=raw -EBE -f32.6
./cmdUtil --protocol=raw -ELE -f32.6
echo
echo TEST: Big and little endian double
./cmdUtil --protocol=raw -EBE -d32.6
./cmdUtil --protocol=raw -ELE -d32.6
echo
echo TEST: String
./cmdUtil -Qraw -s10:alpha
echo
echo TEST: Examples from --help
./cmdUtil --host=localhost --port=1234 --pktid=0x1803 --pktfc=3 --int16=100 --string=16:ES_APP
./cmdUtil -ELE -C2 -A6 -n2 
./cmdUtil --endian=LE --protocol=raw --uint64b=0x1806C000000302DD --uint16=2
./cmdUtil --pktver=1 --pkttype=0 --pktsec=0 --pktseqflg=2 --pktlen=0xABC --pktcksum=0
./cmdUtil -Qcfsv2 --pktedsver=0xA --pktendian=1 --pktpb=1 --pktsubsys=0x123 --pktsys=0x4321 --pktfc=0xB
echo
echo TEST: The reset of the types and strange offset
./cmdUtil -ELE -Qraw -m0xAA -h0x2233 -n0x4455 -l0x12345678 -o0x87654321 -q0x7FFFAAAABBBBCCCC -b0x11
./cmdUtil -EBE -Qraw -m0xAA -h0x2233 -n0x4455 -l0x12345678 -o0x87654321 -q0x7FFFAAAABBBBCCCC -b0x11
./cmdUtil -ELE -Qraw -i0x7788 -j0x1122 -k0x3344556677889900 -w0xaabb -x0xabcdef01 -y0x9876543212345678
./cmdUtil -EBE -Qraw -i0x7788 -j0x1122 -k0x3344556677889900 -w0xaabb -x0xabcdef01 -y0x9876543212345678
echo
echo TEST: Packet fields, individually with max value
./cmdUtil --pktid=0xFFFF
./cmdUtil --pktver=0x7
./cmdUtil --pkttype=1
./cmdUtil --pktsec=1
./cmdUtil --pktapid=0x7FF
./cmdUtil --pktseqflg=3
./cmdUtil --pktseqcnt=0x3fff
./cmdUtil --pktlen=0xffff
./cmdUtil --protocol=ccsdsext --pktedsver=0x1F
./cmdUtil --protocol=ccsdsext --pktendian=1
./cmdUtil --protocol=ccsdsext --pktpb=1
./cmdUtil --protocol=ccsdsext --pktsubsys=0x1FF
./cmdUtil --protocol=ccsdsext --pktsys=0xFFFF
./cmdUtil --protocol=cfsv2 --pktfc=0x7F
./cmdUtil --protocol=cfsv2 --pktcksum=0xFF


