
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