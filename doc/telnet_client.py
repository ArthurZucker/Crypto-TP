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
import binascii
"""
This is a rudimentary telnet client. It has few features, but it
implements a non-standard extension that improves the students experience.
"""
from netstrings import NetstringWrapperProtocol
from sign import sign
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
        self.transport.write(b'porte\n')
        self.transport.write(b'\n')
        self.transport.write(b'technique\n')
        self.transport.write(b'automate\n')
        self.transport.write(b'1\n')
        self.transport.write(b'az\n')

    def dataReceived(self, data):
        """
        Invoked when data arrives from the server. We just print it.
        """
        sys.stdout.buffer.write(data)
        sys.stdout.flush()
        self
        if(data==b'Press any key.\r\r\n'):
            self.transport.write(b'\n')
        if(data[:10]==b'Challenge:'):
            print("\""+data[23:].decode().rstrip()+"\"")
            s = sign(data[23:].decode().rstrip())
            print("________________________")
            signature = binascii.hexlify(s).decode()
            self.transport.write(bytes(signature+'\n',"utf-8"))

        if(data==b'Successful login. Press any key.\r\r\n'):
            self.transport.write(b'\n')
            self.transport.write(b'3\n')
            self.transport.write(b'3\n')
            self.transport.write(b'\n')
            self.transport.write(b'Q\n')
            self.transport.write(b'sortir\n')
            self.transport.write(b'ascenseur\n')
            self.transport.write(b'\n')
            self.transport.write(b'sortir\n')
            self.transport.write(b'sortir\n')


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
        #self.protocol = TelnetTransport(TelnetClient)
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
#reactor.connectTCP('crypta.fil.cool', 23, factory)
reactor.connectTCP('crypta.fil.cool', 6023, factory)
reactor.run()
