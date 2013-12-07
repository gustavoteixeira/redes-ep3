from __future__ import print_function
from base import IP
import sys, internet

class TCPPacket(object):
    id = 0
    def __init__(self, data, source_port, destination_port):
        self.data, self.source_port, self.destination_port = data, source_port, destination_port
        self.length = sys.getsizeof(data) + 20 # size of TCP header considering 0 bytes options
        self.id = TCPPacket.id
        TCPPacket.id += 1
        
    def __len__(self):
        return self.length

class UDPPacket(object):
    id = 0
    def __init__(self, data, source_port, destination_port):
        self.data, self.source_port, self.destination_port = data, source_port, destination_port
        self.length = sys.getsizeof(data) + 8 # size of UDP header = 8 bytes (considering source port and checksum)
        self.id = UDPPacket.id
        UDPPacket.id += 1
        
    def __len__(self):
        return self.length
        
    def __str__(self):
        return "[UDPSocket-{3} -- {0} -> {1}, data: '{2}']".format(self.source_port, self.destination_port, self.data, self.id)
        
class ICMPPacket(object):
    id = 0
    ECHO_REPLY = 0
    ECHO_REQUEST = 8
    TIME_EXCEEDED = 11
    
    def __init__(self, type):
        self.type = type
        self.id = ICMPPacket.id
        ICMPPacket.id += 1
        
    def __len__(self):
        return 1
        
    def __str__(self):
        return "[ICMPPacket-{1} -- type {0}]".format(self.type, self.id)
        
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

class TCPSocket(object):
    def __init__(self, host, port):
        self.host, self.port = host, port
        self.state = "LISTEN"
        self.callback = None
        
    def send_to(self, data, address):
        destination_ip, destination_port = address
        if self.state == "SYN-RECEIVED":
            self.state = "ESTABLISHED"
        else:
            self.state = "SYN-SENT"
        packet = TCPPacket(data, self.port, destination_port)
        self.host.send_to(packet, destination_ip)
        
    def receive(self, tcppacket, source_ip):
        if tcppacket.data == "FIN" and self.state == "ESTABLISHED":
            self.state = "LAST-ACK"
            send_to("FIN ACK", self.host)
        elif tcppacket.data == "FIN ACK" and self.state == "FIN-WAIT-1":
            self.state = "TIME-WAIT"
            send_to("ACK", host)
        elif tcppacket.data == "ACK" and self.state == "LAST-ACK":
            self.host.remove_socket(self.port)
        elif self.state == "SYN-SENT":
            self.state = "SYN-RECEIVED"
        else:
            self.state = "ESTABLISHED"
        self.callback(self, tcppacket.data, (source_ip, tcppacket.source_port))
        
    def close(self):
        self.state = "FIN-WAIT-1"
        send_to("FIN", self.host)
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