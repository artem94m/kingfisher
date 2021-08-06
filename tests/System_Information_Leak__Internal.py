import sys

sys.stderr.write(sys.exc_info())
sys.stdout.write(sys.exc_info())
print(sys.exc_info())