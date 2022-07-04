from subprocess import PIPE, Popen
import sys

def get_command_output(command):
    with Popen(command, stdout=PIPE, stderr=PIPE, shell=True) as process:
        output, err = process.communicate(timeout=15)
        if not process.returncode:
            output = output.decode("utf-8")
            return (True, output)
    return (False,"")

if __name__ == "__main__":
    r, i = get_command_output(sys.argv[1])
    for line in i.split('\n'):
        print(line)
    print(r)
