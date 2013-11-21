from __future__ import print_function
import random
import base
from base import IP

GAMBSDAHORA = {}

class UDPPacket(object):
    def __init__(self, data, source_port, destination_port):
        self.data, self.source_port, self.destination_port = data, source_port, destination_port
        
class NetworkInterface(object):
    def __init__(self, owner):
        self.owner = owner
        self.ip = None
        self.link = None
        
    def configure(self, ip):
        self.ip = ip
        GAMBSDAHORA[ip.value] = self
        
    def send_packet(self, packet, destination_ip):
        target_interface = GAMBSDAHORA[destination_ip.value] # MAGIA
        target_interface.receive_packet(packet, self.ip)
        
    def receive_packet(self, packet, source_ip):
        self.owner.receive_data(packet.data, packet.destination_port, (source_ip, packet.source_port))
        
    def __str__(self):
        return "[Interface - ip: {0}, link: {1}]".format(self.ip, self.link)
        
class DuplexLink(object):
    def __init__(self, bandwidth, latency):
        self.bandwidth, self.latency = bandwidth, latency
        self.endpoint_a, self.endpoint_b = None, None
        self.sniffers = []
        
    def attach(self, endpoint_a, endpoint_b):
        self.endpoint_a, self.endpoint_b = endpoint_a, endpoint_b
        endpoint_a.link = self
        endpoint_b.link = self
        
    def __str__(self):
        return "[DuplexLink - bandwidth: {0}, latency: {1}, attached: {2}]".format(self.bandwidth, self.latency, self.endpoint_a != None)

class Socket(object):
    def __init__(self, protocol, interface, port):
        self.protocol, self.interface, self.port = protocol, interface, port
        self.callback = None
        
    def send_to(self, data, address):
        destination_ip, destination_port = address
        
        packet = UDPPacket(data, self.port, destination_port)
        self.interface.send_packet(packet, destination_ip)
        
    def receive(self, data, source):
        print("Socket {0} received data '{1}' from '{2}'.".format((self.interface.ip, self.port), data, source))
        self.callback(self, data, source)
        
    def close(self):
        self.interface.owner.remove_socket(self.port)
        
class Host(object):
    def __init__(self):
        self.interface = NetworkInterface(self)
        self.default_gateway, self.dns_server = None, None
        self.sockets = {}

    def configure(self, input):
        ip, self.default_gateway, self.dns_server = map(IP, input)
        self.interface.configure(ip)
        return self
        
    def create_socket(self, protocol, port = None):
        if port:
            if port in self.sockets:
                return None
        else:
            for attempt in xrange(10000, 65535):
                if attempt not in self.sockets:
                    port = attempt
                    break
                    
        
        self.sockets[port] = Socket(protocol, self.interface, port)
        return self.sockets[port]
        
    def remove_socket(self, port):
        del self.sockets[port]
        
    def receive_data(self, data, port, source):
        if port in self.sockets:
            return self.sockets[port].receive(data, source)
                
    def __getitem__(self, key):
        assert(key == 0)
        return self.interface
        
    def __str__(self):
        return "[Host - interface: {0}, default_gateway: {1}, dns_server: {2}]".format(self.interface, self.default_gateway, self.dns_server)
    
class Router(object):
    def __init__(self, size):
        self.size = size
        self.interfaces = [NetworkInterface(self) for _ in range(size)]
        self.process_time = None
        self.routes = []
        
    def __getitem__(self, key):
        return self.interfaces[key]
        
    def configure_route(self, input):
        assert(len(input) % 2 == 0)
        for x in range(len(input) / 2):
            mask = IP(input[2*x])
            target = input[2*x + 1]
            try:
                target = IP(target)
            except AssertionError:
                target = self.interfaces[int(target)]
            self.routes.append((mask, target))
        
    def configure_performance(self, input):
        assert(len(input) % 2 == 1)
        self.process_time = input[0] # TODO
        for x in range(len(input) / 2):
            interface = int(input[2*x + 1])
            size = int(input[2*x + 2])
            self.interfaces[interface].queue_size = size
        
    def configure_ip(self, input):
        assert(len(input) % 2 == 0)
        for i in xrange(len(input) / 2):
            self.interfaces[int(input[i * 2 + 0])].configure(IP(input[i * 2 + 1]))
        
    def configure(self, input):
        if input[0] == 'route':
            self.configure_route(input[1:])
        elif input[0] == 'performance':
            self.configure_performance(input[1:])
        else:
            self.configure_ip(input)
        return self
        
    def __str__(self):
        return "[Router - process_time: {0}, interfaces: {1}, routes: {2}]".format(self.process_time, self.interfaces, self.routes)
        