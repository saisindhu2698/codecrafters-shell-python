import sys
import os

def find_executable(command):
    paths = os.getenv("PATH", "").split(":")
    for path in paths:
        exe_path = os.path.join(path, command)
        if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
            return exe_path
    return None

def main():
    builtins = {"echo", "exit", "type"}
    
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        command = input().strip()
        
        if command.startswith("exit "):
            try:
                exit_code = int(command.split()[1])
                sys.exit(exit_code)
            except (IndexError, ValueError):
                print("exit: invalid argument")
                continue
        elif command.startswith("echo "):
            print(command[5:])
        elif command.startswith("type "):
            cmd_name = command.split()[1]
            if cmd_name in builtins:
                print(f"{cmd_name} is a shell builtin")
            else:
                exe_path = find_executable(cmd_name)
                if exe_path:
                    print(f"{cmd_name} is {exe_path}")
                else:
                    print(f"{cmd_name}: not found")
        else:
            print(f"{command}: command not found")

if __name__ == "__main__":
    main()
