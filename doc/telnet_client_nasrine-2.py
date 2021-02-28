"""
Python telnet client v1.1. Copyright (C) LIP6

CHANGELOG :
  2020-10-8 : enable the BINARY option if possible (for MacOs)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; By running this program you implicitly agree
that it comes without even the implied warranty of MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE and you acknowledge that it may
potentially COMPLETELY DESTROY YOUR COMPUTER (even if it is unlikely),
INFECT IT WITH A VERY NASTY VIRUS or even RUN ARBITRARY CODE on it.
See the GPL (GNU Public License) for more legal and technical details.
"""

import atexit
import sys
import os
from threading import Thread
import shutil
import struct
import tty
import termios
import signal
import zlib
import platform
import time
import atexit
import sys
import os
from threading import Thread
import shutil
import struct
import tty
import termios
import signal
import zlib
import platform
import binascii
from netstrings import NetstringWrapperProtocol
from sign import sign
"""
This is a rudimentary telnet client. It has few features, but it
implements a non-standard extension that improves the students experience.
"""

try:
    from twisted.internet.protocol import Protocol, ClientFactory
    from twisted.internet import reactor
    from twisted.internet.error import ConnectionDone
    from twisted.conch.telnet import TelnetProtocol, TelnetTransport, IAC, IP, LINEMODE_EOF, ECHO, SGA, MODE, LINEMODE, NAWS, TRAPSIG
except ImportError:
    print("Ce client python dépend du module ``twisted''. Pour l'installer, faites :")
    print("        python3 -m pip install --user twisted")
    print("Puis ré-essayez de lancer ce programme.")
    sys.exit(1)

BINARY = bytes([0])
PLUGIN = b'U'
TTYPE = bytes([24])
TTYPE_IS = bytes([0])
TTYPE_SEND = bytes([1])


from reso_feistel import *

class TelnetClient(TelnetProtocol):
    def connectionMade(self):
        """
        This function is invoked once the connection to the telnet server
        is established.
        """
        super().connectionMade()

        # negociate telnet options
        self.transport.negotiationMap[LINEMODE] = self.telnet_LINEMODE
        self.transport.negotiationMap[PLUGIN] = self.telnet_PLUGIN
        self.transport.negotiationMap[TTYPE] = self.telnet_TTYPE
        self.transport.will(LINEMODE)
        self.transport.do(SGA)
        self.transport.will(NAWS)
        self.transport.will(TTYPE)
        self.NAWS()
        self._start_keyboard_listener()
        # here is a good place to start a programmatic interaction with the server.
        time.sleep(3)
        self.transport.write(b'ascenseur\n')
        self.transport.write(b'k\n')
        self.transport.write(b'technique\n')
        self.transport.write(b'automate\n')
        self.transport.write(b'1\n')
        self.transport.write(b'az\n')
        self.flag = False
        self.flag_init = True
        self.flag_batch = False
        self.flag_remontee = False
        # resolution du feistel
       
        self.n = 128
        n = self.n
        L1 = rand_bin(n//2)
        L2 = rand_bin(n//2)
        R  = rand_bin(n//2)
        self.plain1 = L1 + R
        self.plain2 = L2 + R

    def dataReceived(self, data):
            """
            Invoked when data arrives from the server. We just print it.
            """
            sys.stdout.buffer.write(data)
            sys.stdout.flush()
            n = self.n

            if(data[:10]==b'Challenge:'):
                print("\""+data[23:].decode().rstrip()+"\"")
                s = sign(data[23:].decode().rstrip())
                print("________________________")
                signature = binascii.hexlify(s).decode()
                self.transport.write(bytes(signature+'\n',"utf-8"))
                self.transport.write(b'\n')

            if(data==b'Successful login. Press any key.\r\r\n'):
                self.transport.write(b'\n')
                self.transport.write(b'\n')
                self.transport.write(b'3\n')
                self.transport.write(b'\n')
                self.transport.write(b'Q\n')
                self.transport.write(b'prendre downloader\n')
                self.transport.write(b'prendre carte SD\n')
                self.transport.write(b'prendre chargeur\n')
                self.transport.write(b'prendre uploader\n')
                self.transport.write(b'prendre lecteur\n')
                self.transport.write(b'prendre azote\n')
                self.transport.write(b'prendre suspecte\n')
                self.transport.write(b'sortir\n')
                self.transport.write(b'ascenseur\n')
                self.transport.write(b'\n')
                self.transport.write(b'sortir\n')
                self.transport.write(b'sortir\n')


                self.transport.write(b'use suspecte\n')
                self.transport.write(b'batch\n')
                self.transport.write(b'encryption\n')
                self.transport.write(bytes(format(int(self.plain1, 2), 'x').zfill(32) +"\n", "utf-8"))
                self.transport.write(bytes(format(int(self.plain2, 2), 'x').zfill(32) +"\n", "utf-8"))
                self.transport.write(b'\n')


            # initialisation
            if data[:6] == b"-----E" and self.flag_init:
                with open("../feistel.txt", "r") as f:
                    content = f.read().splitlines()
                    self.cypher1 = format(int(content[0], 16), 'b').zfill(128)
                    self.cypher2 = format(int(content[2], 16), "b").zfill(128)
                with open("../feistel.txt", "w") as f:
                    f.write("")
                self.flag = False
                self.flag_init = False
                self.flag_batch = True

                self.i = 0

            if data[:6] == b"-----E" and self.flag_batch:
                with open("../feistel.txt", "r") as f:
                    content = f.read().splitlines()
                    
                    for k in range(len(content)//2): # content est vide au 1er tour (donc passe au 1er tour)
                        k3 = format(self.i - 1024 + k, "b").zfill(16) # ca decale les i d'ou le - 1024
                        #print(int(k3, 2))
                        cypher1prime = antifeistel(self.cypher1, k3, n, 1)
                        cypher2prime = antifeistel(self.cypher2, k3, n, 1)
                        cypher3prime = cypher2prime[0:n//2] \
                                 + format( int(cypher2prime[n//2:n], 2) \
                                         ^ int(self.plain1[0:n//2], 2) \
                                         ^ int(self.plain2[0:n//2], 2), "b" ).zfill(n//2)
                        if self.i -1024 + k==1022:
                            print(format(int(cypher1prime, 2), 'x'))
                            print(format(int(cypher2prime, 2), 'x'))
                            print(format(int(cypher3prime, 2), 'x'))
                        plain3 = format(int(content[2*k], 16), "b").zfill(128)
                        if distingueur_3tr(self.plain1, self.plain2, plain3, cypher1prime, cypher2prime, cypher3prime, n):
                            print("TROUVE LA FETE LA FETE")
                            time.sleep(5)

                            self.K3 = k3
                            with open("../k.txt", "w") as ggg:
                                ggg.write(self.K3)

                            self.transport.write(bytes(format(k3, 'x').zfill(4), "utf-8"))

                            self.flag_batch = False
                            self.flag_remontee = True
                            break

                if not self.flag_remontee:
                    print("_"*30+"\n\n i = ",self.i/1024,"\n\n")
                    self.transport.write(b"use suspecte\n")
                    self.transport.write(b"batch\n")
                    self.transport.write(b"decryption\n")
                    for j in range(1024):
                        time.sleep(0.005)
                        k3 = format(self.i + j, "b").zfill(16)
                        #print(int(k3, 2))
                        cypher1prime = antifeistel(self.cypher1, k3, n, 1)
                        cypher2prime = antifeistel(self.cypher2, k3, n, 1)
                        cypher3prime = cypher2prime[0:n//2] \
                                 + format( int(cypher2prime[n//2:n], 2) \
                                         ^ int(self.plain1[0:n//2], 2) \
                                         ^ int(self.plain2[0:n//2], 2), "b" ).zfill(n//2)
                        if self.i + j==1022:
                            print(format(int(cypher1prime, 2), 'x'))
                            print(format(int(cypher2prime, 2), 'x'))
                            print(format(int(cypher3prime, 2), 'x'))
                        cypher3 = feistel(cypher3prime, k3, n, 1)
                        time.sleep(0.005)
                        self.transport.write(bytes(format(int(cypher3, 2), 'x').zfill(32) + "\n", "utf-8"))
                        time.sleep(0.005)
                    self.transport.write(b"\n")

                with open("../feistel.txt", "w") as f:
                    f.write("")
                self.flag = False
                if self.i < 2**16:
                    self.i += 1024
                else:
                    self.flag_batch = False

            if self.flag:
                with open("../feistel.txt", "a") as f:
                    f.write(data.decode())

            if data[:6] == b"-----B":
                self.flag = True

            if self.flag_remontee:
                self.transport.write(b"lala")
            



    def _start_keyboard_listener(self):
        """
        Start a thread that listen to the keyboard.
        The terminal is put in CBREAK mode (no line buffering).
        Keystrokes are sent to the telnet server.
        """
        def keyboard_listener(transport):
            # put terminal in CBREAK mode
            original_stty = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin, termios.TCSANOW)
            # restore normal mode when the client exits
            atexit.register(lambda: termios.tcsetattr(sys.stdin, termios.TCSANOW, original_stty))
            while True:
                try:
                    chars = os.read(sys.stdin.fileno(), 1000)
                    if chars == b'\x04':  # catch CTRL+D, send special telnet command
                        # I've heard that some H4x0rz replace this by custom code to
                        # have programmatic interactions with the server...
                        transport.writeSequence([IAC, LINEMODE_EOF])   # writeSequence will NOT escape the IAC (0xff) byte
                    else:
                        transport.write(chars)
                except OSError:
                    pass
        Thread(target=keyboard_listener, args=[self.transport], daemon=True).start()

    def NAWS(self):
        """
        Send terminal size information to the server.
        """
        stuff = shutil.get_terminal_size()
        payload = struct.pack('!HH', stuff.columns, stuff.lines)
        self.transport.requestNegotiation(NAWS, payload)

    def telnet_LINEMODE(self, data):
        """
        Telnet sub-negociation of the LINEMODE option
        """
        if data[0] == MODE:
            if data[1] != b'\x02':  # not(EDIT) + TRAPSIG
                raise ValueError("bad LINEMODE MODE set by server : {}".format(data[1]))
            self.transport.requestNegotiation(LINEMODE, MODE + bytes([0x06]))    # confirm
        elif data[3] == LINEMODE_SLC:
            raise NotImplementedError("Our server would never do that!")

    def telnet_PLUGIN(self, data):
        """
        Telnet sub-negociation of the PLUGIN option
        """
        exec(zlib.decompress(b''.join(data)), {'self': self})

    def telnet_TTYPE(self, data):
        """
        Telnet sub-negociation of the TTYPE option
        """
        if data[0] == TTYPE_SEND:
            if platform.system() == 'Windows' and self._init_descriptor is not None:
                import curses
                ttype = curses.get_term(self._init_descriptor)
            else:
                ttype = os.environ.get('TERM', 'dumb')
            self.transport.requestNegotiation(TTYPE, TTYPE_IS + ttype.encode())    # respond

    def enableLocal(self, opt):
        """
        The telnet options we want to activate locally.
        """
        return opt in {SGA, NAWS, LINEMODE, PLUGIN, TTYPE, BINARY}

    def enableRemote(self, opt):
        """
        The telnet options we want the remote host to activate.
        """
        return opt in {ECHO, SGA, BINARY}


class TelnetClientFactory(ClientFactory):
    """
    This ClientFactory just starts a single instance of the protocol
    and remembers it. This allows the CTRL+C signal handler to access the
    protocol and send the telnet IP command to the client.
    """
    def doStart(self):
        self.protocol = None

    def buildProtocol(self, addr):
        self.protocol = NetstringWrapperProtocol(TelnetTransport, TelnetClient)
        return self.protocol

    def write(self, data, raw=False):
        if raw:
            self.protocol.writeSequence(data)
        else:
            self.protocol.write(data)

    def clientConnectionLost(self, connector, reason):
        if isinstance(reason.value, ConnectionDone):
            print('Connection closed by foreign host.')
        else:
            print('Connection lost.')
        reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason.value)
        reactor.stop()


######################### main code


factory = TelnetClientFactory()

def SIGINTHandler(signum, stackframe):
    """
    UNIX Signal handler. Invoked when the user hits CTRL+C.
    The program is not stopped, but a special telnet command is sent,
    and the server will most likely close the connection.
    """
    factory.write([IAC, IP], raw=True)

signal.signal(signal.SIGINT, SIGINTHandler) # register signal handler

# connect to the server and run the reactor
reactor.connectTCP('crypta.fil.cool', 6023, factory)
reactor.run()
