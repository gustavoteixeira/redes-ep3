def parse(file):
    for line in file:
        line = line.strip()
        if not line or line[0] == '#':
            continue
        print(line)
    #raise Exception("NYI")