import os
import sys
import shlex
import subprocess

def execute_command(command):
    tokens = shlex.split(command)  # Split the command safely
    if '>' in tokens:
        op_index = tokens.index('>') if '>' in tokens else tokens.index('1>')
        cmd = tokens[:op_index]  # Command part
        output_file = tokens[op_index + 1]  # File name

        with open(output_file, 'w') as outfile:
            process = subprocess.Popen(cmd, stdout=outfile, stderr=sys.stderr)
            process.communicate()
    else:
        process = subprocess.Popen(tokens, stdout=sys.stdout, stderr=sys.stderr)
        process.communicate()

def shell():
    while True:
        try:
            command = input("$ ")  # Prompt for user input
            if command.strip().lower() == "exit":
                break
            execute_command(command)
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    shell()
