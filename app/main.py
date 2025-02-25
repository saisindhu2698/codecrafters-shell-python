import sys
import os
import readline
import shlex
import subprocess

# Global variable to track tab presses
tab_pressed = False  

def completer(text, state):
    """Autocomplete function for built-in commands and external executables in PATH."""
    global tab_pressed
    builtin = ["echo ", "exit ", "type ", "pwd ", "cd "]
    matches = []

    # Check for built-in commands
    matches.extend([cmd for cmd in builtin if cmd.startswith(text)])

    # Check for external executable commands in PATH
    if not matches:
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        for directory in path_dirs:
            try:
                for filename in os.listdir(directory):
                    if filename.startswith(text) and os.access(os.path.join(directory, filename), os.X_OK):
                        matches.append(filename)
            except FileNotFoundError:
                continue  # In case a directory in PATH doesn't exist
    
    # Sort matches alphabetically (important for test case)
    matches.sort()

    # If multiple matches exist, handle double-tab behavior
    if len(matches) > 1:
        if state == 0:  
            if not tab_pressed:
                tab_pressed = True
                sys.stdout.write("\a")  # Ring the bell on the first press
                sys.stdout.flush()
                return None
            else:
                tab_pressed = False
                sys.stdout.write("\n" + "  ".join(matches) + "\n$ " + text)
                sys.stdout.flush()
                return None

    # Return a single match when only one is found
    return matches[state] if state < len(matches) else None

def main():
    global tab_pressed
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        try:
            command_line = input().strip()
            if not command_line:
                continue

            tab_pressed = False  # Reset tab tracking after command execution

            args = shlex.split(command_line)
            command = args[0]

            # Handle built-in commands
            if command == "exit":
                sys.exit(0)
            elif command == "echo":
                sys.stdout.write(" ".join(args[1:]) + "\n")
                sys.stdout.flush()
            elif command == "pwd":
                sys.stdout.write(os.getcwd() + "\n")
                sys.stdout.flush()
            elif command == "cd":
                directory = args[1] if len(args) > 1 else os.environ.get("HOME", "/")
                try:
                    os.chdir(directory)
                except Exception as e:
                    sys.stderr.write(f"cd: {directory}: {str(e)}\n")
                sys.stdout.flush()
            elif command == "type":
                if len(args) < 2:
                    sys.stderr.write("type: missing argument\n")
                else:
                    new_command = args[1]
                    if new_command in ["echo", "exit", "type", "pwd", "cd"]:
                        sys.stdout.write(f"{new_command} is a shell builtin\n")
                    else:
                        found = False
                        for path in os.environ.get("PATH", "").split(os.pathsep):
                            full_path = os.path.join(path, new_command)
                            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                                sys.stdout.write(f"{new_command} is {full_path}\n")
                                found = True
                                break
                        if not found:
                            sys.stderr.write(f"{new_command}: not found\n")
                sys.stdout.flush()
            else:
                result = subprocess.run(args, capture_output=True, text=True)
                sys.stdout.write(result.stdout)
                sys.stderr.write(result.stderr)
                sys.stdout.flush()

        except EOFError:
            sys.stdout.write("\n")
            break
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
