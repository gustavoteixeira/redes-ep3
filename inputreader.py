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
            return self.env.expand(input[0]).configurate(input[1:])
        else:
            name = input[0].replace('-', '') # - is an invalid character in method names in python
            return getattr(self, 'method_' + name)(input[1:])
        
    def method_host(self, input):
        return lib.Host()
        
    def method_router(self, input):
        return lib.Router(int(input[0]))
        
    def method_duplexlink(self, input):
        link = lib.DuplexLink(input[2], input[3])
        source      = lib.force_interface(input[0])
        destination = lib.force_interface(input[1])
        link.attach(self.env.expand(source), self.env.expand(destination))
        return link
        
    def method_attachagent(self, input):
        agent = self.env.expand(input[0])
        return agent.attach(self.env, input[1:])
        
    def method_at(self, input):
        time = input[0]
        request = input[1]
        
        request_input = oursplit(request)
        if request_input[0] == 'finish':
            return("MEU DEUS TERMINOU AS COISAS")
        
        agent = self.env.expand("$" + request_input[0])
        agent.do_stuff(request_input[1:])
 
class Env:
    def function_set(self, input):
        self.variables[input[0]] = self.evaluate(oursplit(input[1]))
        return self.variables[input[0]]
        
    def function_new(self, input):
        class_name = input[0].replace('/', '')
        return lib.__dict__[class_name]()

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
        env.evaluate(input)
    
    #raise Exception("NYI")