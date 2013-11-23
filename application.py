from __future__ import print_function
import base, transport
from base import IP

def TimedPrint(s):
    print("{:7.4f}".format(base.timemanagerglobal.current_time) + ": " + s)

def MakeDNSRequest(base_host, target_hostname, callback):
    def dns_callback(socket, data, source):
        socket.close()
        callback(IP(data))
    
    TimedPrint("Host {0} querying DNS for '{1}'.".format(base_host.interface.ip, target_hostname))
    socket = transport.CreateSocketOn(base_host, 'udp')
    socket.callback = dns_callback
    socket.send_to(target_hostname, (base_host.dns_server, 53))

class AgentService(object):
    def attach(self, env, input):
        host = env.expand(input[0])
        self.socket = transport.CreateSocketOn(host, self.protocol, self.port)
        self.socket.callback = self.receive_request
    
class AgentHTTPServer(AgentService):
    def __init__(self):
        self.protocol = 'tcp'
        self.port = 80
        
    def receive_request(self, socket, data, source):
        response = "404 Error"
        TimedPrint("Host {0} sending HTTP response '{1}' to {2}.".format(socket.host.interface.ip, response, source))
        socket.send_to(response, source)
    
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
            TimedPrint("Host {0} received GET: '{1}'".format(socket.host.interface.ip, data))
    
        TimedPrint("Host {1} sending GET to '{0}'.".format(ip, self.host.interface.ip))
        socket = transport.CreateSocketOn(self.host, 'tcp')
        socket.callback = get_callback
        socket.send_to("GET /", (ip, 80))
        
    def do_stuff(self, input):
        assert(input[0] == 'GET')
        
        try:
            target = IP(input[1])
            self.do_get(target)
            
        except AssertionError:
            MakeDNSRequest(self.host, input[1], self.do_get)
            
    
class AgentSniffer(object):
    def attach(self, env, input):
        interface_a = env.expand(base.force_interface(input[0]))
        interface_b = env.expand(base.force_interface(input[1]))
        assert(interface_a.link == interface_b.link)
        self.file = input[2]
        interface_a.link.sniffers.append(self)
        return self
        