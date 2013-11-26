from __future__ import print_function
from functools import partial
import base, transport

class DuplexLink(object):
    def __init__(self, bandwidth, latency):
        self.bandwidth, self.latency = base.convert_bandwidth(bandwidth), base.convert_time(latency)
        self.endpoint_a, self.endpoint_b = None, None
        self.sniffers = []
        
    def attach(self, endpoint_a, endpoint_b):
        self.endpoint_a, self.endpoint_b = endpoint_a, endpoint_b
        endpoint_a.link = self
        endpoint_b.link = self
        
    def calculate_transfer_time(self, packet):
        return 0.0 # TODO
        
    def send_packet(self, packet, source):
        if self.endpoint_a == source:
            target = self.endpoint_b
        elif self.endpoint_b == source:
            target = self.endpoint_a
        else:
            raise Exception("DuplexLink received send_packet from unknown source.")
        
        for sniffer in self.sniffers:
            print("\nPacket {0} at time {1}s sniffed by {2}".format(packet.id, base.timemanagerglobal.current_time, sniffer))
            
            trans_packet = packet.data
            if(isinstance(trans_packet, transport.UDPPacket)):
                print("Internet Layer (IP):\n\tFrom {0} to {1}, UDP, TTL {3}".format(packet.source, packet.destination, packet.ttl, packet.ttl))
                print("Transport Layer (UDP):\n\tPorts: Source {0} Destination {1}, Length {2} bytes".format(trans_packet.source_port, trans_packet.destination_port, trans_packet.length))
            elif(isinstance(trans_packet, transport.TCPPacket)):
                print("Internet Layer (IP):\n\tFrom {0} to {1}, TCP, TTL {3}".format(packet.source, packet.destination, packet.ttl, packet.ttl))
                print("Transport Layer (TCP):\n\tPorts: Source {0}, Destination {1}".format(trans_packet.source_port, trans_packet.destination_port))
            
            trans_packet = packet.data
            application_data = trans_packet.data
            message = (trans_packet.data[:100] + '...') if len(trans_packet.data) > 100 else trans_packet.data
            print("Application Layer:\n\tMessage:\n{0}\n".format(message))
        base.timemanagerglobal.execute_in(self.calculate_transfer_time(packet) + self.latency, 
                                          partial(target.receive, packet))
        
    def __str__(self):
        return "[DuplexLink - bandwidth: {0}, latency: {1}, attached: {2}]".format(self.bandwidth, self.latency, self.endpoint_a != None)

