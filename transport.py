from __future__ import print_function
from base import IP
import sys, internet

class TCPPacket(object):
    id = 0
    def __init__(self, data, source_port, destination_port):
        self.data, self.source_port, self.destination_port = data, source_port, destination_port
        self.length = sys.getsizeof(data)
        self.id = TCPPacket.id
        TCPPacket.id += 1

class UDPPacket(object):
    id = 0
    def __init__(self, data, source_port, destination_port):
        self.data, self.source_port, self.destination_port = data, source_port, destination_port
        self.length = sys.getsizeof(data) + 32 # size of UDP header = 32 bytes (considering source port and checksum)
        self.id = UDPPacket.id
        UDPPacket.id += 1
        
    def __str__(self):
        return "[UDPSocket-{3} -- {0} -> {1}, data: '{2}']".format(self.source_port, self.destination_port, self.data, self.id)
        
class UDPSocket(object):
    def __init__(self, host, port):
        self.host, self.port = host, port
        self.callback = None
        
    def send_to(self, data, address):
        destination_ip, destination_port = address
        
        packet = UDPPacket(data, self.port, destination_port)
        self.host.send_to(packet, destination_ip)
        
    def receive(self, udppacket, source_ip):
        self.callback(self, udppacket.data, (source_ip, udppacket.source_port))
        
    def close(self):
        self.host.remove_socket(self.port)
        
        
def CreateSocketOn(host, protocol, port = None):
    if port:
        if not host.port_free(port):
            return None
    else:
        for attempt in xrange(10000, 65535):
            if host.port_free(attempt):
                port = attempt
                break
                
    sock = UDPSocket(host, port)
    host.add_socket(sock)
    return sock