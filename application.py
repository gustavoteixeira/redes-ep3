from __future__ import print_function
import base, transport, re, os
from base import IP

def TimedPrint(s):
    print("{:7.4f}".format(base.timemanagerglobal.current_time) + ": " + s)

def MakeDNSRequest(base_host, target_hostname, callback):
    start_time = base.timemanagerglobal.current_time
    def dns_callback(socket, data, source):
        end_time = base.timemanagerglobal.current_time
        TimedPrint("{0} received DNS in {1}ms".format(socket.host.interface.ip, int((end_time - start_time) * 1000)))
        socket.close()
        callback(IP(data))
    
    TimedPrint("{0} querying DNS for '{1}'.".format(base_host.interface.ip, target_hostname))
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
        m = re.match("^GET (.+) HTTP/1.1$", data)
        f = None
        if m:
            try:
                f = open("./" + m.group(1).replace("../", ""), "rb")
                size = os.fstat(f.fileno()).st_size
                socket.send_to("HTTP/1.1 200 OK\Content-Type: application/octet-stream\nContent-Length: " + str(size) + "\n\n" + f.read(), source)
            except IOError:
                socket.send_to("HTTP/1.1 404 NOT FOUND\nContent-Length: 0\n\n", source)
        else:
            socket.send_to("HTTP/1.1 400 BAD REQUEST\nContent-Length: 0\n\n", source)
    
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
        start_time = base.timemanagerglobal.current_time
        def get_callback(socket, data, source):
            end_time = base.timemanagerglobal.current_time
            socket.close()
            TimedPrint("{0} received GET in {1}ms [{2} bytes]".format(socket.host.interface.ip, int((end_time - start_time) * 1000), len(data)))
    
        TimedPrint("{1} sending GET to {0}.".format(ip, self.host.interface.ip))
        socket = transport.CreateSocketOn(self.host, 'tcp')
        socket.callback = get_callback
        socket.send_to("GET /teste.txt HTTP/1.1", (ip, 80))
        
    def do_traceroute(self, ip):
        class ICMPHandler(object):
            def __init__(self):
                self.distance = 1
                self.count = 1
            
            def __call__(self, host, ippacket):
                if self.count < 3:
                    self.count += 1
                elif ippacket.data.type == transport.ICMPPacket.TIME_EXCEEDED:
                    self.distance += 1
                    self.count = 1
                else:
                    host.icmp_handler = None
                    return
                host.send_to(transport.ICMPPacket(transport.ICMPPacket.ECHO_REQUEST), ip, self.distance)
    
        self.host.icmp_handler = ICMPHandler()
        self.host.send_to(transport.ICMPPacket(transport.ICMPPacket.ECHO_REQUEST), ip, 1)
        
    def do_stuff(self, input):
        action = None
        if input[0] == 'GET':
            action = self.do_get
                
        elif input[0] == 'traceroute':
            action = self.do_traceroute
        
        else:
            raise Exception("Unexpected command: " + str(input[0]))
            
        try:
            target = IP(input[1])
            action(target)
            
        except AssertionError:
            MakeDNSRequest(self.host, input[1], action)
            
    
class AgentSniffer(object):
    def attach(self, env, input):
        interface_a = env.expand(base.force_interface(input[0]))
        interface_b = env.expand(base.force_interface(input[1]))
        assert(interface_a.link == interface_b.link)
        self.file = open(input[2], "w")
        interface_a.link.sniffers.append(self)
        return self
        