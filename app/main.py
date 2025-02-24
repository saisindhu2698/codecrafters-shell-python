import sys
import os
import subprocess
import shlex
import readline  # Import readline for autocompletion

# Define the builtins globally
builtins = {"echo", "exit", "type", "pwd", "cd"}

def find_executable(command):
    paths = os.getenv("PATH", "").split(":")
    for path in paths:
        exe_path = os.path.join(path, command)
        if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
            return exe_path
    return None

# Function to handle the autocompletion
def complete_builtin_commands(text, state):
    matches = [cmd for cmd in builtins if cmd.startswith(text)]
    if state < len(matches):
        return matches[state] + " "  # Add a space after the completed command
    else:
        return None

def main():
    # Bind tab key to use our custom completion function
    readline.set_completer(complete_builtin_commands)
    readline.parse_and_bind("tab: complete")  # Allow tab to trigger completion

    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        try:
            command = input().strip()
        except EOFError:
            break
        
        if not command:
            continue
        
        # Use shlex.split to handle quoting (including double quotes) correctly
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
                # Handle the ~ character for the user's home directory.
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
                except subprocess.CalledProcessError as e:
                    print(f"{cmd_name}: process exited with status {e.returncode}")
                except Exception as e:
                    print(f"{cmd_name}: failed to execute: {e}")
            else:
                print(f"{cmd_name}: command not found")

if __name__ == "__main__":
    main()
