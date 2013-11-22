import base, application, transport, internet, link
from functools import partial

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
            return self.env.expand(input[0]).configure(input[1:])
        else:
            name = input[0].replace('-', '') # - is an invalid character in method names in python
            return getattr(self, 'method_' + name)(input[1:])
        
    def method_host(self, input):
        return internet.Host()
        
    def method_router(self, input):
        return internet.Router(int(input[0]))
        
    def method_duplexlink(self, input):
        l = link.DuplexLink(input[2], input[3])
        source      = base.force_interface(input[0])
        destination = base.force_interface(input[1])
        l.attach(self.env.expand(source), self.env.expand(destination))
        return l
        
    def method_attachagent(self, input):
        agent = self.env.expand(input[0])
        return agent.attach(self.env, input[1:])
        
    def action(self, input):
        if input[0] == 'finish':
            return("MEU DEUS TERMINOU AS COISAS")
        
        agent = self.env.expand("$" + input[0])
        agent.do_stuff(input[1:])
        
    def method_at(self, input):
        time = base.convert_time(input[0])
        request_input = oursplit(input[1])
        self.env.timemanager.execute_in(time, partial(self.action, request_input))
 
class Env:
    def function_set(self, input):
        self.variables[input[0]] = self.evaluate(oursplit(input[1]))
        return self.variables[input[0]]
        
    def function_new(self, input):
        class_name = input[0].replace('/', '')
        return application.__dict__[class_name]()

    def __init__(self):
        self.variables = { 'simulator': Simulator(self) }
        self.functions = {
            'set': self.function_set,
            'new': self.function_new
        }
        self.timemanager = base.TimeManager()
                
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
    return env