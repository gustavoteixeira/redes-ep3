from __future__ import print_function
from base import IP
import internet

class UDPPacket(object):
    def __init__(self, data, source_port, destination_port):
        self.data, self.source_port, self.destination_port = data, source_port, destination_port
        
    def __str__(self):
        return "[UDPSocket -- {0} -> {1}, data: '{2}']".format(self.source_port, self.destination_port, self.data)
        
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