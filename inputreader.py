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
    
class Simulator:
    def __init__(self, env):
        self.env = env
        
    def __call__(self, input):
        if type(input[0]) == str:
            name = input[0].replace('-', '') # - is an invalid character in method names in python
            return getattr(self, 'method_' + name)(input[1:])
        else:
            # Configurating a host or a router
            return False
        
    def method_host(self, input):
        return 'host'
        
    def method_router(self, input):
        return 'router-' + input[0]
        
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
    
    print("-------")
    for v in env.variables:
        print(v, env.variables[v])
    #raise Exception("NYI")