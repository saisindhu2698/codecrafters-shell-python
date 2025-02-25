import sys
import os
import readline
import shlex
import subprocess

TAB_PRESSED = 0  # Track tab presses

def find_executables(prefix):
    """Find all executable files in PATH that start with the given prefix."""
    matches = []
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)

    for directory in path_dirs:
        try:
            for filename in os.listdir(directory):
                if filename.startswith(prefix) and os.access(os.path.join(directory, filename), os.X_OK):
                    matches.append(filename)
        except FileNotFoundError:
            continue  # Skip missing directories in PATH
    
    return sorted(matches)  # Return sorted list for consistent ordering

def completer(text, state):
    """Autocomplete function for executables and built-in commands."""
    global TAB_PRESSED
    builtin = ["echo", "exit", "type", "pwd", "cd"]
    matches = [cmd for cmd in builtin if cmd.startswith(text)]
    
    # If no built-in matches, search for executables
    if not matches:
        matches = find_executables(text)

    if state == 0:
        if len(matches) > 1:
            if TAB_PRESSED == 0:
                sys.stdout.write("\a")  # Ring the bell on the first Tab press
                sys.stdout.flush()
                TAB_PRESSED += 1
                return None
            elif TAB_PRESSED == 1:
                sys.stdout.write("\n" + "  ".join(matches) + "\n$ " + text)
                sys.stdout.flush()
                TAB_PRESSED = 0  # Reset counter
                return None
        TAB_PRESSED = 0  # Reset counter if only one match

    return matches[state] + " " if state < len(matches) else None

def main():
    global TAB_PRESSED
    builtin = ["echo", "exit", "type", "pwd", "cd"]
    PATH = os.environ.get("PATH")
    HOME = os.environ.get("HOME")  # Get the user's home directory
    
    # Set up autocomplete
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        try:
            command_line = input().strip()
            if not command_line:
                continue
            args = shlex.split(command_line)

            command = args[0]
            if command == "exit":
                sys.exit(0)
            elif command == "echo":
                sys.stdout.write(" ".join(args[1:]) + "\n")
                sys.stdout.flush()
            elif command == "pwd":
                sys.stdout.write(os.getcwd() + "\n")
                sys.stdout.flush()
            elif command == "cd":
                directory = args[1] if len(args) > 1 else HOME
                if directory == "~":
                    directory = HOME
                try:
                    os.chdir(directory)
                except Exception as e:
                    sys.stderr.write(f"cd: {directory}: {str(e)}\n")
                    sys.stderr.flush()
            elif command == "type":
                if len(args) < 2:
                    sys.stderr.write("type: missing argument\n")
                else:
                    new_command = args[1]
                    cmd_path = None
                    for path in PATH.split(os.pathsep):
                        full_path = os.path.join(path, new_command)
                        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                            cmd_path = full_path
                            break
                    if new_command in builtin:
                        sys.stdout.write(f"{new_command} is a shell builtin\n")
                    elif cmd_path:
                        sys.stdout.write(f"{new_command} is {cmd_path}\n")
                    else:
                        sys.stderr.write(f"{new_command}: not found\n")
                sys.stdout.flush()
            else:
                cmd_path = None
                for path in PATH.split(os.pathsep):
                    full_path = os.path.join(path, command)
                    if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                        cmd_path = full_path
                        break
                if cmd_path:
                    try:
                        result = subprocess.run(args, capture_output=True, text=True)
                        sys.stdout.write(result.stdout)
                        sys.stderr.write(result.stderr)
                    except Exception as e:
                        sys.stderr.write(f"Error executing command: {e}\n")
                else:
                    sys.stderr.write(f"{command}: command not found\n")
                sys.stdout.flush()
        except EOFError:
            sys.stdout.write("\n")
            break
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
