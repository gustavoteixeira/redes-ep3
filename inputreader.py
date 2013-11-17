def find_first_of(s, occ, start = 0):
    i = len(s) + 1
    for c in occ:
        f = s.find(c, start)
        if f > -1 and f < i:
            i = f
    if i > len(s):
        return -1
    return i

groupers = { '[': ']', '"': '"' }
def oursplit(input):
    resp = []
    start = 0
    while True:
        i = find_first_of(input, groupers, start)
        if i < 0:
            resp.extend(input[start:].strip().split(' '))
            break
        else:
            resp.extend(input[start:i].strip().split(' '))
        e = input.index(groupers[input[i]], i+1)
        resp.append(input[(i+1):e])
        start = e + 1
    return filter(None, resp)
    
class Host:
    def configurate(self, input):
        self.ip, self.default_gateway, self.dns_server = input
    
class Router:
    def __init__(self, size):
        self.size = size
        self.interfaces = [None] * size
        
    def configurate_route(self, input):
        raise Exception("NYI")
        
    def configurate_performance(self, input):
        raise Exception("NYI")
        
    def configurate_ip(self, input):
        assert(len(input) % 2 == 0)
        for i in xrange(len(input) / 2):
            self.interfaces[int(input[i * 2 + 0])] = input[i * 2 + 1]
        
    def configurate(self, input):
        if input[0] == 'route':
            self.configurate_route(input[1:])
        elif input[0] == 'performance':
            self.configurate_performance(input[1:])
        else:
            self.configurate_ip(input)
    
class Simulator:
    def __init__(self, env):
        self.env = env
        
    def __call__(self, input):
        if input[0][0] == '$':
            # Configurating a host or a router
            self.env.expand(input[0]).configurate(input[1:])
        else:
            name = input[0].replace('-', '') # - is an invalid character in method names in python
            return getattr(self, 'method_' + name)(input[1:])
        
    def method_host(self, input):
        return Host()
        
    def method_router(self, input):
        return Router(int(input[0]))
        
    def method_duplexlink(self, input):
        return 'duplex-link'
 
class Env:
    def function_set(self, input):
        self.variables[input[0]] = self.evaluate(oursplit(input[1]))
        return self.variables[input[0]]
        
    def function_new(self, input):
        return input[0]

    def __init__(self):
        self.variables = { 'simulator': Simulator(self) }
        self.functions = {
            'set': self.function_set,
            'new': self.function_new
        }
        
    def expand(self, s):
        if s[0] == '$':
            return self.variables[s[1:]]
        else:
            return self.functions[s]
        
    def evaluate(self, input):
        call = self.expand(input[0])
        if len(input) > 1:
            return call(input[1:])
        else:
            return call
    
def parse(file):
    env = Env()
    for line in file:
        line = line.strip()
        if not line or line[0] == '#':
            continue
        
        input = oursplit(line)
        print(input)
        print(env.evaluate(input))
        print("")
    
    print("-------")
    for v in env.variables:
        print(v, env.variables[v])
    #raise Exception("NYI")