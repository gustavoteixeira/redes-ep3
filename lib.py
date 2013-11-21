def force_interface(s):
    if s.find('.') == -1:
        return s + ".0"
    return s

class IP(object):
    def __init__(self, ip):
        assert(ip.count(".") == 3)
        sum = 0
        multi = 1
        for piece in reversed(ip.split('.')):
            sum += int(piece) * multi
            multi *= 256
        self.value = sum
        
    def __repr__(self):
        return str(self.value)

class NetworkInterface(object):
    def __init__(self, ip):
        self.ip = ip
        self.link = None
        
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
        
class Host(object):
    def __init__(self):
        self.interface = NetworkInterface(None)
        self.default_gateway, self.dns_server = None, None
        self.agents = []

    def configurate(self, input):
        self.interface.ip, self.default_gateway, self.dns_server = map(IP, input)
        return self
        
    def attach(self, agent):
        self.agents.append(agent)
        return agent
        
    def __getitem__(self, key):
        assert(key == 0)
        return self.interface
        
    def __str__(self):
        return "[Host - interface: {0}, default_gateway: {1}, dns_server: {2}]".format(self.interface, self.default_gateway, self.dns_server)
    
class Router(object):
    def __init__(self, size):
        self.size = size
        self.interfaces = [NetworkInterface(None) for _ in range(size)]
        self.process_time = None
        self.routes = []
        
    def __getitem__(self, key):
        return self.interfaces[key]
        
    def configurate_route(self, input):
        assert(len(input) % 2 == 0)
        for x in range(len(input) / 2):
            mask = IP(input[2*x])
            target = input[2*x + 1]
            try:
                target = IP(target)
            except AssertionError:
                target = self.interfaces[int(target)]
            self.routes.append((mask, target))
        
    def configurate_performance(self, input):
        assert(len(input) % 2 == 1)
        self.process_time = input[0] # TODO
        for x in range(len(input) / 2):
            interface = int(input[2*x + 1])
            size = int(input[2*x + 2])
            self.interfaces[interface].queue_size = size
        
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
        
    def __str__(self):
        return "[Router - process_time: {0}, interfaces: {1}, routes: {2}]".format(self.process_time, self.interfaces, self.routes)

class AgentService(object):
    def attach(self, env, input):
        host = env.expand(input[0])
        return host.attach(self)    
        
class AgentHTTPClient(AgentService):
    pass
    
class AgentHTTPServer(AgentService):
    pass
    
class AgentDNSServer(AgentService):
    pass
    
class AgentSniffer(object):
    def attach(self, env, input):
        interface_a = env.expand(force_interface(input[0]))
        interface_b = env.expand(force_interface(input[1]))
        assert(interface_a.link == interface_b.link)
        self.file = input[2]
        interface_a.link.sniffers.append(self)
        return self
        