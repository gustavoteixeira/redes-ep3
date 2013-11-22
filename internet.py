from __future__ import print_function
import base

class IPPacket(object):
    def __init__(self, data, source, destination):
        self.ttl = 64
        self.data = data
        self.source = source
        self.destination = destination

class NetworkInterface(object):
    def __init__(self, owner):
        self.owner = owner
        self.ip = None
        self.link = None
        
    def configure(self, ip):
        self.ip = ip
        
    def send_to(self, ippacket, destination_ip):
        # Simplesmente taca o pacote no fio?
        self.link.send_packet(ippacket, self)
        
    def receive(self, ippacket):
        self.owner.receive(ippacket)
        
    def __str__(self):
        return "[Interface - ip: {0}, link: {1}]".format(self.ip, self.link)

class Host(object):
    def __init__(self):
        self.interface = NetworkInterface(self)
        self.default_gateway, self.dns_server = None, None
        self.sockets = {}

    def configure(self, input):
        ip, self.default_gateway, self.dns_server = map(base.IP, input)
        self.interface.configure(ip)
        return self
        
    def port_free(self, port):
        return port not in self.sockets
        
    def add_socket(self, socket):
        self.sockets[socket.port] = socket
        
    def remove_socket(self, port):
        del self.sockets[port]
        
    # Send data
    def send_to(self, data, destination_ip):
        ippacket = IPPacket(data, self.interface.ip, destination_ip)
        self.interface.send_to(ippacket, self.default_gateway)
    
    def receive(self, ippacket):
        port = ippacket.data.destination_port # Peek the transport data...
        if port in self.sockets:
            self.sockets[port].receive(ippacket.data, ippacket.source)
                
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
            mask = base.IP(input[2*x])
            target = input[2*x + 1]
            try:
                target = base.IP(target)
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
            self.interfaces[int(input[i * 2 + 0])].configure(base.IP(input[i * 2 + 1]))
        
    def configure(self, input):
        if input[0] == 'route':
            self.configure_route(input[1:])
        elif input[0] == 'performance':
            self.configure_performance(input[1:])
        else:
            self.configure_ip(input)
        return self
        
        
        
    # Send data
    def send_to(self, data, destination_ip):
        raise Exception("NYI")
    
    def receive(self, ippacket):
        raise Exception("NYI")
        
    def __str__(self):
        return "[Router - process_time: {0}, interfaces: {1}, routes: {2}]".format(self.process_time, self.interfaces, self.routes)