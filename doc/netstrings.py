"""
Python twisted helper v1.1. Copyright (C) LIP6

CHANGELOG :
  2020-10-8 : added connectionLost() support

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

from twisted.protocols.basic import NetstringReceiver

class ProtocolTransportMixin:
    """
    Act both as a protocol (w.r.t the outside world) AND a transport.
    """
    def __init__(self, protocolFactory, *args, **kwds):
        self.inner_protocol_factory = protocolFactory
        self.inner_protocol_args = args
        self.inner_protocol_kwds = kwds
        super().__init__()

    def _connect_inner_protocol(self):
        """
        Connects the inner protocol. Give it "self" as transport.
        """
        # build the inner protocol from the factory
        self.inner_protocol = self.inner_protocol_factory(*self.inner_protocol_args, **self.inner_protocol_kwds)

        # I'm the transport for the inner protocol
        inner_transport = self
        self.inner_protocol.makeConnection(inner_transport)

    def connectionMade(self):
        """
        I've been started up. Start the inner protocol.
        """
        super().connectionMade() # make connection in potential super-class
        self._connect_inner_protocol()

    # there is no dataReceived method: subclasses have to implement it

    def connectionLost(self, reason):
        """
        I've lost the connection to the outside world. Notify the inner protocol.
        """
        super().connectionLost(reason) # lose connection in potential super-class
        self.inner_protocol.connectionLost(reason) # lose connection in inner protocol


    #### now the transport part.
    def write(self, data):
        """
        Invoked by the inner protocol when it wants to send <data> to the outside world.
        Intercept outgoing data, process, send to my own ("external") transport.
        """
        self.transport.write(data)

    def writeSequence(self, seq):
        self.write(b''.join(seq))


    def loseConnection(self):
        """
        Inner protocol wants to abort. We abort.
        """
        self.transport.loseConnection()

    def getHost(self):
        """
        Inner protocol asks about the connected party. We forward the query...
        """
        return self.transport.getHost()

    def getPeer(self):
        return self.transport.getPeer()


class NetstringWrapperProtocol(ProtocolTransportMixin, NetstringReceiver):
    """
    This protocol receives netstrings. When a complete netstring is received,
    the payload is sent to the inner protocol. When the inner protocol sends
    bytes, they are wrapped inside a netstring and sent to the outside world.

    IMPLEMENTATION DETAILS :

    The connectionMade() method is inherited from ProtocolTransportMixin (both
    parent classes implement this method, but we inherit from
    ProtocolTransportMixin first, so it wins). It starts the inner proto AND
    call super().connectionMade(), which will resolve to
    NetstringReceiver.connectionMade()...

    The dataReceived() method is inherited from NetstringReceiver, because
    ProtocolTransportMixin does not implement it. It will call the
    stringReceived() method of this class once a netstring is received.
    """
    def stringReceived(self, data):
        """
        netstring received and decoded. Forward to inner proto.
        """
        self.inner_protocol.dataReceived(data)


    def write(self, data):
        """
        Intercept outgoing data from inner protocol, wrap in netstring and
        send to external transport.
        """
        self.sendString(data)   # inherited from NetstringReceiver
