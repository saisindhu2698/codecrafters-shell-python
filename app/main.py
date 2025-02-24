import sys
import os
import subprocess
import shlex

def find_executable(command):
    paths = os.getenv("PATH", "").split(":")
    for path in paths:
        exe_path = os.path.join(path, command)
        if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
            return exe_path
    return None

def main():
    builtins = {"echo", "exit", "type", "pwd", "cd"}
    
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        try:
            command = input().strip()
        except EOFError:
            break
        
        if not command:
            continue
        
        # Check for output redirection '>' or '1>'
        if '>' in command or '1>' in command:
            if '1>' in command:
                parts = command.split('1>')
                command_part = parts[0].strip()
                file_path = parts[1].strip()
            else:
                parts = command.split('>')
                command_part = parts[0].strip()
                file_path = parts[1].strip()

            # Parse the command using shlex to handle quotes and spaces
            parts = shlex.split(command_part)
            cmd_name = parts[0]
            args = parts[1:]

            # Check if file path is provided correctly
            try:
                with open(file_path, 'w') as f:
                    subprocess.run([cmd_name] + args, stdout=f, check=True)
            except FileNotFoundError:
                print(f"{cmd_name}: {file_path}: No such file or directory")
            except Exception as e:
                print(f"{cmd_name}: failed to execute: {e}")
        else:
            # Handle normal command without redirection
            parts = shlex.split(command)
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
                # Echo command should print exactly what is in the arguments
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
            elif cmd_name == "pwd":
                print(os.getcwd())
            elif cmd_name == "cd":
                if len(args) != 1:
                    print("cd: too many arguments")
                else:
                    path = args[0]
                    if path == "~":
                        home = os.getenv("HOME")
                        if home is None:
                            print("cd: HOME environment variable not set")
                            continue
                        path = home
                    try:
                        os.chdir(path)
                    except FileNotFoundError:
                        print(f"cd: {args[0]}: No such file or directory")
                    except NotADirectoryError:
                        print(f"cd: {args[0]}: Not a directory")
                    except PermissionError:
                        print(f"cd: {args[0]}: Permission denied")
            else:
                exe_path = find_executable(cmd_name)
                if exe_path:
                    try:
                        subprocess.run([cmd_name] + args, check=True)
                    except subprocess.CalledProcessError:
                        # Suppress error messages on failure
                        pass  # Command failed silently, just print the prompt next
                    except Exception as e:
                        print(f"{cmd_name}: failed to execute: {e}")
                else:
                    print(f"{cmd_name}: command not found")

if __name__ == "__main__":
    main()
