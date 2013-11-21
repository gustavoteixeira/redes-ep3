from __future__ import print_function
import base
from base import IP

GAMBSDAHORA = {}

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
        interface_a = env.expand(base.force_interface(input[0]))
        interface_b = env.expand(base.force_interface(input[1]))
        assert(interface_a.link == interface_b.link)
        self.file = input[2]
        interface_a.link.sniffers.append(self)
        return self
        