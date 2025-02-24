import sys
import os
import subprocess

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
        try:
            command = input().strip()
        except EOFError:
            break
        
        if not command:
            continue
        
        parts = command.split()
        cmd_name = parts[0]
        args = parts[1:]
        
        if cmd_name == "exit":
            try:
                exit_code = int(args[0]) if args else 0
                sys.exit(exit_code)
            except ValueError:
                print("exit: invalid argument")
                continue
        elif cmd_name == "echo":
            print(" ".join(args))
        elif cmd_name == "type":
            if args:
                target_cmd = args[0]
                if target_cmd in builtins:
                    print(f"{target_cmd} is a shell builtin")
                else:
                    exe_path = find_executable(target_cmd)
                    if exe_path:
                        print(f"{target_cmd} is {exe_path}")
                    else:
                        print(f"{target_cmd}: not found")
            else:
                print("type: missing argument")
        else:
            exe_path = find_executable(cmd_name)
            if exe_path:
                try:
                    subprocess.run([cmd_name] + args, check=True)  # Pass cmd_name instead of exe_path
                except subprocess.CalledProcessError as e:
                    print(f"{cmd_name}: process exited with status {e.returncode}")
                except Exception as e:
                    print(f"{cmd_name}: failed to execute: {e}")
            else:
                print(f"{cmd_name}: command not found")

if __name__ == "__main__":
    main()
