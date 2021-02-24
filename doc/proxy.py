"""
Python telnet proxy v1.0. Copyright (C) LIP6

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

import argparse

try:
    from twisted.internet import protocol
    from twisted.internet import reactor
    from twisted.internet.error import ConnectionDone
except ImportError:
    print("Ce proxy python dépend du module ``twisted''. Pour l'installer, faites :")
    print("        python3 -m pip install --user twisted")
    print("Puis ré-essayez de lancer ce programme.")
    sys.exit(1)


class ClientProtocol(protocol.Protocol):
    """
    This protocol talks to the server
    (it simulates the telnet client of the user).
    """

    def connectionMade(self):
        """
        I am connected to the server
        """
        print("Connection to the server established!")

    def dataReceived(self, data):
        """
        I got some data from the server. Forward it to the telnet client.
        """
        self.server_protocol.transport.write(data)

    def connectionLost(self, reason):
        """
        Lost connection to the server? Disconnect the telnet client
        """
        self.server_protocol.transport.loseConnection()



class ServerProtocol(protocol.Protocol):
    """
    This protocol talks to the telnet client of the user
    (it simulates the server).
    """

    def dataReceived(self, data):
        """
        Received data from the telnet client. Forward to the server.
        """
        self.client_protocol.transport.write(data)

    def connectionLost(self, reason):
        self.client_protocol.transport.loseConnection()



class ClientFactory(protocol.ClientFactory):
    """
    This factory builds instances of the client protocol and it gives them
    access to the server protocol.
    """
    def __init__(self, server_protocol):
        self.server_protocol = server_protocol

    def buildProtocol(self, addr):
        """
        Build a fresh instance of the client protocol, and connect it with the
        (pre-existing instance of the server protocol)
        """
        client_protocol = ClientProtocol()
        client_protocol.server_protocol = self.server_protocol
        self.server_protocol.client_protocol = client_protocol
        return client_protocol


class ServerFactory(protocol.Factory):
    """
    This factory creates instances of the server protocol. On incoming
    connections, an instance of the client protocol is spawned up and connected
    to the server.
    """
    def buildProtocol(self, addr):
        print("using build protocol, should probably modify the underlying protocol\n could then be eadier in this code")
        server_protocol = ServerProtocol()
        reactor.connectTCP(args.connect_host, args.connect_port, ClientFactory(server_protocol))
        return server_protocol


parser = argparse.ArgumentParser()
parser.add_argument('--listen_port', type=int, default=4242)
parser.add_argument('--connect_host', default='crypta.fil.cool')
parser.add_argument('--connect_port', type=int, default=6023)

args = parser.parse_args()
print("Listening on port {}, forwarding to {}:{}".format(args.listen_port, args.connect_host, args.connect_port))

reactor.listenTCP(args.listen_port, ServerFactory())
reactor.run()
