import sys

print(something)
sys.stderr.write(something)
sys.stdout.write(something)
print(something, file=sys.stdout)
print(something, file=sys.stderr)