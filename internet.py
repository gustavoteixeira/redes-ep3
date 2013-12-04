from __future__ import print_function
import base, collections

class IPPacket(object):
    id = 0
    def __init__(self, data, source, destination):
        self.ttl = 64
        self.data = data
        self.source = source
        self.destination = destination
        self.id = IPPacket.id
        IPPacket.id += 1
        
    def __len__(self):
        return 4+4+4+len(self.data)
        
    def __str__(self):
        return "[IPPacket-{3} -- {0} -> {1}, data: {2}]".format(self.source, self.destination, self.data, self.id)
        
Route = collections.namedtuple("Route", "network, mask, value")

class NetworkInterface(object):
    def __init__(self, owner):
        self.owner = owner
        self.ip = None
        self.link = None
        
    def configure(self, ip):
        self.ip = ip
        
    def send_to(self, ippacket):
        self.link.send_packet(ippacket, self)
        
    def receive(self, ippacket):
        #print("NetworkInterface({1}).receive -- {0}".format(ippacket, self.ip))
        self.owner.receive(ippacket, self)
        
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
        self.interface.send_to(ippacket)
    
    def receive(self, ippacket, interface):
        ippacket.ttl -= 1
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
        for interface in self.interfaces:
            interface.packet_queue = []
        self.process_time = None
        self.routes = []
        self.next_interface = 0
        self.active_processor = False
        
    def __getitem__(self, key):
        return self.interfaces[key]
        
    def configure_route(self, input):
        assert(len(input) % 2 == 0)
        for x in range(len(input) / 2):
            network = base.IP(input[2*x])
            target = input[2*x + 1]
            try:
                target = base.IP(target)
            except AssertionError:
                target = self.interfaces[int(target)]
            self.routes.append(Route(network, base.IP("255.255.255.0"), target))
        
    def configure_performance(self, input):
        assert(len(input) % 2 == 1)
        self.process_time = base.convert_time(input[0])
        for x in range(len(input) / 2):
            interface = int(input[2*x + 1])
            size = int(input[2*x + 2])
            self.interfaces[interface].queue_maxsize = size
        
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
    def delegate_to(self, ippacket, target_ip):
        for route in self.routes:
            if (target_ip.value & route.mask.value) == route.network.value:
                # Found the intended route to target
                if type(route.value) == base.IP:
                    return self.delegate_to(ippacket, route.value)
                return route.value.send_to(ippacket)
    
    def send_to(self, ippacket):
        self.delegate_to(ippacket, ippacket.destination)
    
    def receive(self, ippacket, interface):
        if len(interface.packet_queue) >= interface.queue_maxsize:
            return # Dropping the packet!
        ippacket.ttl -= 1
        if ippacket.ttl > 0:
            interface.packet_queue.append(ippacket)
            if not self.active_processor:
                self.activate_processor()
        else:
            # TODO: ep4 aqui
            pass
        
    def activate_processor(self):
        self.active_processor = True
        base.timemanagerglobal.execute_in(self.process_time,
                                          self.handle_packet)
        
    def handle_packet(self):
        for i in range(3):
            interface = self.interfaces[(self.next_interface + i) % 3]
            if len(interface.packet_queue) > 0:
                packet = interface.packet_queue.pop(0)
                self.send_to(packet)
                self.next_interface = (self.next_interface + 1) % 3
                self.activate_processor()
        self.active_processor = False
        
        
    def __str__(self):
        return "[Router - process_time: {0}, interfaces: {1}, routes: {2}]".format(self.process_time, self.interfaces, self.routes)
