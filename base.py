import Queue

def convert_time(t):
    if t.endswith("us"):
        time = float(t[:-2]) /1000000
    elif t.endswith("ms"):
        time = float(t[:-2]) /1000
    else:
        time = float(t)
    return time
    
def convert_bandwidth(b):
    elif b.endswith("Gbps"):
        bandwidth = float(b[:-4]) * 1024 * 1024 * 128
    elif b.endswith("Mbps"):
        bandwidth = float(b[:-4]) * 1024 * 128
    elif b.endswith("Kbps"):
        bandwidth = float(b[:-4]) * 128
    bandwidth = float(b) # TODO
    return bandwidth

def force_interface(s):
    if s.find('.') == -1:
        return s + ".0"
    return s

class IP(object):
    def __init__(self, ip):
        assert(str(ip).count(".") == 3)
        self.original = ip
        self.value = self.convert(ip)
    
    def convert(self, s):
        sum = 0
        multi = 1
        for piece in reversed(s.split('.')):
            sum += int(piece) * multi
            multi *= 256
        return sum
        
    def __repr__(self):
        return self.original
        
timemanagerglobal = None
class TimeManager(object):
    def __init__(self):
        global timemanagerglobal
        timemanagerglobal = self
        self.current_time = 0.0
        self.timeline = Queue.PriorityQueue()
        
    def is_empty(self):
        return self.timeline.empty()
        
    def execute_in(self, time, func):
        assert(time > 0)
        self.timeline.put((self.current_time + time, func))
        
    def execute_next(self):
        time, func = self.timeline.get(False)
        self.current_time = time
        func()