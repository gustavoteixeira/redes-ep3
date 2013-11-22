from __future__ import print_function
from functools import partial

class DuplexLink(object):
    def __init__(self, bandwidth, latency):
        self.bandwidth, self.latency = bandwidth, latency
        self.endpoint_a, self.endpoint_b = None, None
        self.sniffers = []
        
    def attach(self, endpoint_a, endpoint_b):
        self.endpoint_a, self.endpoint_b = endpoint_a, endpoint_b
        endpoint_a.link = self
        endpoint_b.link = self
        
    def calculate_transfer_time(self, packet):
        print(len(packet))
        
    def send_packet(self, packet, source):
        if self.endpoint_a == source:
            target = self.endpoint_b
        elif self.endpoint_b == source:
            target = self.endpoint_a
        else:
            raise Exception("DuplexLink received send_packet from unknown source.")
            
        callback = partial(target.receive, packet)
        callback()
        #time = self.calculate_transfer_time(packet) + self.latency
            
        #TIMEMANAGERDAHORA.execute_in(time, callback)
        
    def __str__(self):
        return "[DuplexLink - bandwidth: {0}, latency: {1}, attached: {2}]".format(self.bandwidth, self.latency, self.endpoint_a != None)

