from __future__ import print_function
from functools import partial
import base

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
            
        base.timemanagerglobal.execute_in(self.calculate_transfer_time(packet) + self.latency, 
                                          partial(target.receive, packet))
        
    def __str__(self):
        return "[DuplexLink - bandwidth: {0}, latency: {1}, attached: {2}]".format(self.bandwidth, self.latency, self.endpoint_a != None)

