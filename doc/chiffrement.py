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

import base64
import random
import json
from sign import sign
import hmac
import hashlib
from twisted.protocols.basic import NetstringReceiver
from aes import *
import hashlib


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

def bytes_xor(a, b) :
    return bytes(x ^ y for x, y in zip(a, b))
def strxor (s0, s1):
    l = [ chr ( ord (a) ^ ord (b) ) for a,b in zip (s0, s1) ]
    return ''.join (l)
class ChiffrementWrapperProtocol(ProtocolTransportMixin, NetstringReceiver):
    def AES_128_CTR_1(self,octets=32):
        while(octets>len(self.stream_encrypt)):
            P = self.CTR1.to_bytes(16, 'big')
            self.stream_encrypt+=(self.aes_encrypt.encrypt(P))
            self.CTR1+=1
        temp = self.stream_encrypt[:octets]
        self.stream_encrypt = self.stream_encrypt[octets:]
        return temp
    def AES_128_CTR_2(self,octets=32):
        while(octets>len(self.stream_decrypt)):
            P = self.CTR2.to_bytes(16, 'big')
            self.stream_decrypt+=(self.aes_decrypt.encrypt(P))
            self.CTR2+=1
        temp = self.stream_decrypt[:octets]
        self.stream_decrypt = self.stream_decrypt[octets:]
        return temp
    def dataReceived(self,data):
        if(self.DH  == False):
            #print("DATA received",data)
            data = json.loads(data.decode())
            B = data['B']
            signature = data['signature']
            self.DH =True
            K = pow(B,self.x,self.p)
            # dechiffrer
            self.Kaes = hashlib.sha256((str(K)+'A').encode()).digest()[:16]
            self.Kiv  = int(hashlib.sha256((str(K)+'B').encode()).hexdigest()[:32],16)
            self.Kmac = hashlib.sha256((str(K)+'C').encode()).digest()[:16]
            # chiffer
            self.Kaes2 = hashlib.sha256((str(K)+'D').encode()).digest()[:16]
            self.Kiv2  = int(hashlib.sha256((str(K)+'E').encode()).hexdigest()[:32],16)
            self.Kmac2 = hashlib.sha256((str(K)+'F').encode()).digest()[:16]
            self.CTR1 = self.Kiv
            self.CTR2 = self.Kiv2
            self.aes_encrypt = AES(self.Kaes)
            self.aes_decrypt = AES(self.Kaes2)
            return super().connectionMade()
        else :
            tag     = data[-32:]
            data    = data[:-32]
            mask = self.AES_128_CTR_1(len(data))
            #print("[CHIFFREMENT-READ] Mask : ",mask)
            decrypted_data = bytes_xor(data,mask)
            if(tag == hmac.new(self.Kmac, msg = decrypted_data, digestmod = hashlib.sha256).digest()) : self.inner_protocol.dataReceived(decrypted_data)
            #print("[Chiffrement-READ] Decrypted data encoded",decrypted_data)
            #self.inner_protocol.dataReceived(decrypted_data)
        
        
    def write(self, data):
        mask = self.AES_128_CTR_2(len(data))
        #print("[CHIFFREMENT-WRITE] Mask : ",mask)
        encrypted_data = bytes_xor(data,mask)
        tag = hmac.new( self.Kmac2, msg = data, digestmod = hashlib.sha256).digest()
        authenticated_data = encrypted_data+tag
        #print("[CHIFFREMENT-WRITE] Autenticated : ",(authenticated_data) )
        self.transport.write(authenticated_data)  # inherited from NetstringReceiver
        
    def connectionMade(self):
        self.DH = False
        print("Connexion initialized, implement diffie Hellman key exchange")
        self.g = int("3f:b3:2c:9b:73:13:4d:0b:2e:77:50:66:60:ed:bd:48:4c:a7:b1:8f:21:ef:20:54:07:f4:79:3a:1a:0b:a1:25:10:db:c1:50:77:be:46:3f:ff:4f:ed:4a:ac:0b:b5:55:be:3a:6c:1b:0c:6b:47:b1:bc:37:73:bf:7e:8c:6f:62:90:12:28:f8:c2:8c:bb:18:a5:5a:e3:13:41:00:0a:65:01:96:f9:31:c7:7a:57:f2:dd:f4:63:e5:e9:ec:14:4b:77:7d:e6:2a:aa:b8:a8:62:8a:c3:76:d2:82:d6:ed:38:64:e6:79:82:42:8e:bc:83:1d:14:34:8f:6f:2f:91:93:b5:04:5a:f2:76:71:64:e1:df:c9:67:c1:fb:3f:2e:55:a4:bd:1b:ff:e8:3b:9c:80:d0:52:b9:85:d1:82:ea:0a:db:2a:3b:73:13:d3:fe:14:c8:48:4b:1e:05:25:88:b9:b7:d2:bb:d2:df:01:61:99:ec:d0:6e:15:57:cd:09:15:b3:35:3b:bb:64:e0:ec:37:7f:d0:28:37:0d:f9:2b:52:c7:89:14:28:cd:c6:7e:b6:18:4b:52:3d:1d:b2:46:c3:2f:63:07:84:90:f0:0e:f8:d6:47:d1:48:d4:79:54:51:5e:23:27:cf:ef:98:c5:82:66:4b:4c:0f:6c:c4:16:59".replace(':',''),base=16)
        self.p = int("00:87:a8:e6:1d:b4:b6:66:3c:ff:bb:d1:9c:65:19:59:99:8c:ee:f6:08:66:0d:d0:f2:5d:2c:ee:d4:43:5e:3b:00:e0:0d:f8:f1:d6:19:57:d4:fa:f7:df:45:61:b2:aa:30:16:c3:d9:11:34:09:6f:aa:3b:f4:29:6d:83:0e:9a:7c:20:9e:0c:64:97:51:7a:bd:5a:8a:9d:30:6b:cf:67:ed:91:f9:e6:72:5b:47:58:c0:22:e0:b1:ef:42:75:bf:7b:6c:5b:fc:11:d4:5f:90:88:b9:41:f5:4e:b1:e5:9b:b8:bc:39:a0:bf:12:30:7f:5c:4f:db:70:c5:81:b2:3f:76:b6:3a:ca:e1:ca:a6:b7:90:2d:52:52:67:35:48:8a:0e:f1:3c:6d:9a:51:bf:a4:ab:3a:d8:34:77:96:52:4d:8e:f6:a1:67:b5:a4:18:25:d9:67:e1:44:e5:14:05:64:25:1c:ca:cb:83:e6:b4:86:f6:b3:ca:3f:79:71:50:60:26:c0:b8:57:f6:89:96:28:56:de:d4:01:0a:bd:0b:e6:21:c3:a3:96:0a:54:e7:10:c3:75:f2:63:75:d7:01:41:03:a4:b5:43:30:c1:98:af:12:61:16:d2:27:6e:11:71:5f:69:38:77:fa:d7:ef:09:ca:db:09:4a:e9:1e:1a:15:97".replace(':',''),base=16)
        self.q = int("00:8c:f8:36:42:a7:09:a0:97:b4:47:99:76:40:12:9d:a2:99:b1:a4:7d:1e:b3:75:0b:a3:08:b0:fe:64:f5:fb:d3".replace(':',''),base=16)

        self.x = random.randint(1,self.q)
        self.A = pow(self.g,self.x,self.p)
        s = sign(str(self.A))
        jdict = json.dumps({'username':"az",'A':self.A,"signature":s.hex()})
        
        # self.Kiv = 0x00000000000000000000000000000000
        # self.Kaes = (0x00000000000000000000000000000000).to_bytes(16,'big')
        # self.Kmac = (0x00000000000000000000000000000000).to_bytes(16,'big')
        
        # self.Kiv2 = 0x00000000000000000000000000000000
        # self.Kaes2 = (0x00000000000000000000000000000000).to_bytes(16,'big')
        # self.Kmac2 = (0x00000000000000000000000000000000).to_bytes(16,'big')
        
        # self.CTR1 = self.Kiv
        # self.CTR2 = self.Kiv
        
        self.stream_encrypt = b""
        self.stream_decrypt = b""
        self.transport.write(jdict.encode()) 