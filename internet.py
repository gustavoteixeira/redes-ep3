from __future__ import print_function

GAMBSDAHORA = {}

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
