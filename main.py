import argparse
import inputreader

parser = argparse.ArgumentParser(description='Network simulator.')
parser.add_argument('inputfile', help='Path to the input file')
config = parser.parse_args()

print("==================================")
print("WELCOME TO THE WONDERFUL SIMULATOR")
print("==================================")

# Read input
print("Reading configuration file '%s'..." % config.inputfile)
env = inputreader.parse(open(config.inputfile))

print("Starting TimeManager loop!")
while not env.timemanager.is_empty():
    env.timemanager.execute_next()

print("Goodbye!")