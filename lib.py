class IP(object):
    def __init__(self, ip):
        self.ip = ip
        
    def __repr__(self):
        return self.ip

class NetworkInterface(object):
    def __init__(self, ip):
        self.ip = ip
        self.link = None
        
class DuplexLink(object):
    def __init__(self, source, destination, bandwidth, latency):
        self.bandwidth, self.latency = bandwidth, latency
        self.source, self.destination = source, destination
        source.link = self
        destination.link = self
        
class Host(object):
    def __init__(self):
        self.interface = NetworkInterface(None)

    def configurate(self, input):
        self.interface.ip, self.default_gateway, self.dns_server = map(IP, input)
        
    def __getitem__(self, key):
        assert(key == 0)
        return self.interface
    
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