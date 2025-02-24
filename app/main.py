import os
import readline
import subprocess
import sys
import shlex

# Variable to keep track of tab press count for a specific prefix
tab_press_count = {}

def completer(text, state):
    """Autocomplete function for executables and built-in commands."""
    global tab_press_count
    if text not in tab_press_count:
        tab_press_count[text] = 0

    # Check for matching executables in PATH
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    matches = set()  # Use a set to avoid duplicates
    
    for directory in path_dirs:
        try:
            for filename in os.listdir(directory):
                if filename.startswith(text) and os.access(os.path.join(directory, filename), os.X_OK):
                    matches.add(filename)  # Add to set to ensure uniqueness
        except FileNotFoundError:
            continue  # In case a directory in PATH doesn't exist
    
    if matches:
        # Handle Tab key presses
        if tab_press_count[text] == 0:
            tab_press_count[text] += 1
            sys.stdout.write('\a')  # Ring the bell on first Tab press
            sys.stdout.flush()
            sys.stdout.write(f"$ {text}")  # Show the current text (prefix) without repeating prompt
            sys.stdout.flush()
            return None  # Do not return any match yet (waiting for second Tab)
        elif tab_press_count[text] == 1:
            # Show the matching executables on the second Tab press
            sys.stdout.write("\n" + "  ".join(sorted(matches)) + "\n")  # Print completions
            sys.stdout.write("$ ")  # Print prompt after completions
            sys.stdout.flush()
            tab_press_count[text] = 0  # Reset the tab press count for the next command
            return None  # Do not return any match yet
    return None

def main():
    """Main function to run the shell with autocompletion."""
    global tab_press_count
    # Initialize readline for autocompletion
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        try:
            # Read input and parse using shlex
            command_line = input().strip()
            if not command_line:
                continue

            args = shlex.split(command_line)  # Properly split command while handling quotes
            command = args[0]
            
            # Handle "exit"
            if command == "exit":
                sys.exit(0)
            
            # Handle other built-in commands like echo, pwd, cd, etc.
            elif command == "echo":
                sys.stdout.write(" ".join(args[1:]) + "\n")
                sys.stdout.flush()
            
            elif command == "pwd":
                sys.stdout.write(os.getcwd() + "\n")
                sys.stdout.flush()
            
            elif command == "cd":
                try:
                    os.chdir(args[1] if len(args) > 1 else os.environ.get("HOME"))
                except FileNotFoundError:
                    sys.stderr.write(f"cd: {args[1]}: No such file or directory\n")
                sys.stdout.flush()
            
            elif command == "type":
                if len(args) < 2:
                    sys.stderr.write("type: missing argument\n")
                else:
                    new_command = args[1]
                    cmd_path = None
                    # Search for the command in PATH
                    for path in os.environ.get("PATH", "").split(os.pathsep):
                        full_path = os.path.join(path, new_command)
                        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                            cmd_path = full_path
                            break
                    if new_command in ["echo", "pwd", "cd"]:
                        sys.stdout.write(f"{new_command} is a shell builtin\n")
                    elif cmd_path:
                        sys.stdout.write(f"{new_command} is {cmd_path}\n")
                    else:
                        sys.stderr.write(f"{new_command}: not found\n")
                sys.stdout.flush()

            # External command execution
            else:
                cmd_path = None
                for path in os.environ.get("PATH", "").split(os.pathsep):
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
        
        except EOFError:  # Handle Ctrl+D gracefully
            sys.stdout.write("\n")
            break
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
