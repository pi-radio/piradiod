#!/usr/bin/env python3

from twisted.internet import endpoints, protocol, reactor
from twisted.protocols import basic
from lark import Lark

from spidev import SPIDev
from LTC5584 import LTC5584Dev
from LMX2595 import LMX2595Dev

class PiRadioProtocol(basic.LineReceiver):
    def connectionMade(self):
        print("Connection established")

    def lineReceived(self, l):
        print(l)

class PiRadio_140GHz_Bringup:
    def __init__(self):
        print("Initializing 140GHz Bringup Board")

        self.LTC5584 = [ LTC5584Dev(2, i) for i in range(8) ]

        self.LMXEravant = LMX2595Dev(2, 12)
        
        
        
class PiRadioFactory(protocol.ServerFactory):
    protocol = PiRadioProtocol

    def __init__(self, board):
        self.board = board

endpoint = endpoints.serverFromString(reactor, "tcp:6666")

endpoint.listen(PiRadioFactory(PiRadio_140GHz_Bringup()))

print("Listening for connections")
reactor.run()
