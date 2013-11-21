import lib

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
        if input[0][0] == '$':
            # Configurating a host or a router
            self.env.expand(input[0]).configurate(input[1:])
        else:
            name = input[0].replace('-', '') # - is an invalid character in method names in python
            return getattr(self, 'method_' + name)(input[1:])
        
    def method_host(self, input):
        return lib.Host()
        
    def method_router(self, input):
        return lib.Router(int(input[0]))
        
    def method_duplexlink(self, input):
        source      = input[0]
        destination = input[1]
        if source.find('.') == -1: source += ".0"
        if destination.find('.') == -1: destination += ".0"
        return (self.env.expand(source), self.env.expand(destination), input[2], input[3])
 
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
            try:
                name, index = s[1:].split('.')
                return self.variables[name][int(index)]
            except ValueError:
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