class IP(object):
    def __init__(self, ip):
        self.ip = ip
        
    def __repr__(self):
        return self.ip

class NetworkInterface(object):
    def __init__(self, ip):
        self.ip = ip
        self.link = None
        
    def __repr__(self):
        return "[Interface - ip: {0}, link: {1}]".format(self.ip, self.link)
        
class DuplexLink(object):
    def __init__(self, bandwidth, latency):
        self.bandwidth, self.latency = bandwidth, latency
        self.endpoint_a, self.endpoint_b = None, None
        
    def attach(self, endpoint_a, endpoint_b):
        self.endpoint_a, self.endpoint_b = endpoint_a, endpoint_b
        endpoint_a.link = self
        endpoint_b.link = self
        
    def __repr__(self):
        return "[DuplexLink - bandwidth: {0}, latency: {1}, attached: {2}]".format(self.bandwidth, self.latency, self.endpoint_a != None)
        
class Host(object):
    def __init__(self):
        self.interface = NetworkInterface(None)
        self.default_gateway, self.dns_server = None, None

    def configurate(self, input):
        self.interface.ip, self.default_gateway, self.dns_server = map(IP, input)
        return self
        
    def __getitem__(self, key):
        assert(key == 0)
        return self.interface
        
    def __repr__(self):
        return "[Host - interface: {0}, default_gateway: {1}, dns_server: {2}]".format(self.interface, self.default_gateway, self.dns_server)
    
class Router(object):
    def __init__(self, size):
        self.size = size
        self.interfaces = [NetworkInterface(None) for _ in range(size)]
        
    def __getitem__(self, key):
        return self.interfaces[key]
        
    def configurate_route(self, input):
        raise Exception("NYI")
        
    def configurate_performance(self, input):
        raise Exception("NYI")
        
    def configurate_ip(self, input):
        assert(len(input) % 2 == 0)
        for i in xrange(len(input) / 2):
            self.interfaces[int(input[i * 2 + 0])].ip = IP(input[i * 2 + 1])
        
    def configurate(self, input):
        if input[0] == 'route':
            self.configurate_route(input[1:])
        elif input[0] == 'performance':
            self.configurate_performance(input[1:])
        else:
            self.configurate_ip(input)
        return self
        
    def __repr__(self):
        return "[Router - interfaces: {0}]".format(self.interfaces) 