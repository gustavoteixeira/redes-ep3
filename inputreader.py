def parse(file):
    for line in file:
        line.strip()
        if line:
            if line[0] == '#' or line[0] == '\n':
                continue
            else:
                print(line)
    #raise Exception("NYI")