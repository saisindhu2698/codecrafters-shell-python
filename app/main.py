import sys
import os
import readline
import shlex
import subprocess

# Global variables to track completion state
_last_text = ""
_tab_count = 0

def completer(text, state):
    """
    Autocomplete function for built-in commands and external executables in PATH.
    
    Behavior:
      - On first TAB press when multiple matches exist, ring the bell.
      - On second TAB press, display all matches.
    """
    global _last_text, _tab_count

    builtin = ["echo ", "exit ", "type ", "pwd ", "cd "]
    matches = []

    # First, check for built-in commands.
    matches.extend([cmd for cmd in builtin if cmd.startswith(text)])

    # Then, check for external executables in PATH.
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    for directory in path_dirs:
        try:
            for filename in os.listdir(directory):
                fullpath = os.path.join(directory, filename)
                if filename.startswith(text) and os.access(fullpath, os.X_OK):
                    matches.append(filename)
        except FileNotFoundError:
            continue

    # Remove duplicate entries and sort the list.
    matches = sorted(set(matches))
    
    # Reset the tab counter if the completion text changes.
    if text != _last_text:
        _last_text = text
        _tab_count = 0

    # If more than one match exists, handle TAB behavior.
    if len(matches) > 1:
        if _tab_count == 0:
            # On the first TAB press, ring the bell.
            sys.stdout.write('\a')
            sys.stdout.flush()
            _tab_count += 1
            return None  # Do not auto-complete yet.
        elif _tab_count == 1:
            # On the second TAB press, reset counter and return None so that
            # readline calls the display hook.
            _tab_count = 0
            return None

    # If exactly one match or iterating over matches, return the match.
    if state < len(matches):
        candidate = matches[state]
        # For builtins (which already include a trailing space), return as-is.
        if candidate in builtin:
            return candidate
        # For executables, append a trailing space.
        return candidate + " "
    else:
        return None

def display_matches(substitution, matches, longest_match_length):
    """
    Readline display hook.
    Prints matching commands (separated by two spaces) on a new line,
    then reprints the prompt with the current substitution.
    """
    if matches:
        sys.stdout.write("\n" + "  ".join(matches) + "\n")
    sys.stdout.write("$ " + substitution)
    sys.stdout.flush()

def main():
    PATH = os.environ.get("PATH")
    HOME = os.environ.get("HOME")
    
    # Set up autocomplete and the display hook.
    readline.set_completer(completer)
    readline.set_completion_display_matches_hook(display_matches)
    readline.parse_and_bind("tab: complete")
    
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        try:
            command_line = input().strip()
            if not command_line:
                continue

            # Process command line input.
            args = shlex.split(command_line)
            command = args[0]

            # Handle built-in commands.
            if command == "exit":
                sys.exit(0)
            elif command == "echo":
                output = " ".join(args[1:])
                sys.stdout.write(output + "\n")
                sys.stdout.flush()
            elif command == "pwd":
                sys.stdout.write(os.getcwd() + "\n")
                sys.stdout.flush()
            elif command == "cd":
                # Default to HOME if no argument is provided.
                directory = args[1] if len(args) > 1 else HOME
                if directory == "~":
                    directory = HOME
                try:
                    os.chdir(directory)
                except FileNotFoundError:
                    sys.stderr.write(f"cd: {directory}: No such file or directory\n")
                except PermissionError:
                    sys.stderr.write(f"cd: {directory}: Permission denied\n")
                except Exception as e:
                    sys.stderr.write(f"cd: {directory}: {str(e)}\n")
                sys.stdout.flush()
            elif command == "type":
                if len(args) < 2:
                    sys.stderr.write("type: missing argument\n")
                else:
                    new_command = args[1]
                    cmd_path = None
                    # Search for the command in PATH.
                    for path in PATH.split(os.pathsep):
                        full_path = os.path.join(path, new_command)
                        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                            cmd_path = full_path
                            break
                    if new_command in [cmd.strip() for cmd in ["echo", "exit", "type", "pwd", "cd"]]:
                        sys.stdout.write(f"{new_command} is a shell builtin\n")
                    elif cmd_path:
                        sys.stdout.write(f"{new_command} is {cmd_path}\n")
                    else:
                        sys.stderr.write(f"{new_command}: not found\n")
                sys.stdout.flush()
            else:
                # Handle external commands.
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
