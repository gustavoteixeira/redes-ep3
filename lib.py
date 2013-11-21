from __future__ import print_function
import random


GAMBSDAHORA = {}

def force_interface(s):
    if s.find('.') == -1:
        return s + ".0"
    return s

class IP(object):
    def __init__(self, ip):
        assert(str(ip).count(".") == 3)
        self.original = ip
        self.value = self.convert(ip)
    
    def convert(self, s):
        sum = 0
        multi = 1
        for piece in reversed(s.split('.')):
            sum += int(piece) * multi
            multi *= 256
        return sum
        
    def __repr__(self):
        return self.original

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
        
    def dns_request(self, hostname, callback):
        
        def dns_callback(socket, data, source):
            socket.close()
            callback(IP(data))
        
        socket = self.create_socket('udp')
        socket.callback = dns_callback
        socket.send_to(hostname, (self.dns_server, 53))
        
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
        

class AgentService(object):
    def attach(self, env, input):
        host = env.expand(input[0])
        self.socket = host.create_socket(self.protocol, self.port)
        self.socket.callback = self.receive_request
    
class AgentHTTPServer(AgentService):
    def __init__(self):
        self.protocol = 'tcp'
        self.port = 80
        
    def receive_request(self, socket, data, source):
        socket.send_to("404 Error", source)
    
class AgentDNSServer(AgentService):
    def __init__(self):
        self.protocol = 'udp'
        self.port = 53
        
    def attach(self, env, input):
        AgentService.attach(self, env, input)
        self.env = env
        
    def receive_request(self, socket, data, source):
        target = self.env.expand("$" + data)
        socket.send_to(str(target.interface.ip), source)

class AgentHTTPClient(AgentService):
    def attach(self, env, input):
        self.host = env.expand(input[0])
        return self
        
    def do_get(self, ip):
        def get_callback(socket, data, source):
            socket.close()
            print("Received GET: '{0}'".format(data))
    
        print("Send GET request to {0}.".format(ip))
        socket = self.host.create_socket('tcp')
        socket.callback = get_callback
        socket.send_to("GET /", (ip, 80))
        
    def do_stuff(self, input):
        assert(input[0] == 'GET')
        
        print("\n============\nAgentHTTPClient do_stuff start! input: " + str(input))
        try:
            target = IP(input[1])
            self.do_get(target)
            
        except AssertionError:
            print(input[1] + " is not an IP, query DNS.")
            self.host.dns_request(input[1], self.do_get)
            
    
class AgentSniffer(object):
    def attach(self, env, input):
        interface_a = env.expand(force_interface(input[0]))
        interface_b = env.expand(force_interface(input[1]))
        assert(interface_a.link == interface_b.link)
        self.file = input[2]
        interface_a.link.sniffers.append(self)
        return self
        