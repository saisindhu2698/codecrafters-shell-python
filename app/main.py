import os
import readline
import subprocess
import sys
import shlex

# Variable to keep track of tab press count
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
            sys.stdout.write(f"$ {text}")  # Show the current text again after the first Tab press
            sys.stdout.flush()
            return None  # Do not return any match yet (waiting for second Tab)
        elif tab_press_count[text] == 1:
            # Show the matching executables on the second Tab press
            sys.stdout.write("\n" + "  ".join(sorted(matches)) + "\n$ ")
            sys.stdout.flush()
            tab_press_count[text] = 0  # Reset the tab press count for the next command
            return None  # Do not return any match yet
    return None

def find_executable(command):
    paths = os.getenv("PATH", "").split(":")
    for path in paths:
        exe_path = os.path.join(path, command)
        if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
            return exe_path
    return None

def redirect_output(command, file_path):
    """Redirects output to a file while ensuring only the intended output is written."""
    with open(file_path, "w") as f:
        try:
            # Run the command and capture stdout to the file.
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Only write stdout to the file (avoid stderr and other unwanted content).
            f.write(result.stdout.decode())
        except subprocess.CalledProcessError as e:
            print(f"{command[0]}: process exited with status {e.returncode}")
        except Exception as e:
            print(f"{command[0]}: failed to execute: {e}")

def print_program_name():
    """Prints the program name (excluding the full path)."""
    program_name = os.path.basename(sys.argv[0])
    print(f"Arg #0 (program name): {program_name}")

def main():
    """Main function to run the shell with autocompletion."""
    global tab_press_count
    builtins = {"echo", "exit", "type", "pwd", "cd"}
    
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

            # Print the program name after the prompt
            print_program_name()

            # Check if redirection is present and handle 1> or >
            if '>' in command_line or '1>' in command_line:
                parts = command_line.split('>')  # Split around the redirection operator
                cmd_part = parts[0].strip()  # The command part
                file_part = parts[1].strip()  # The file to redirect to
                
                # Handle the command and args before the redirection
                cmd_parts = shlex.split(cmd_part)
                cmd_name = cmd_parts[0]
                args = cmd_parts[1:]
                
                # Check if the file is valid
                if not file_part:
                    print("No file specified for output redirection.")
                    continue

                # Redirect output to the file
                redirect_output([cmd_name] + args, file_part)
                
            else:
                parts = shlex.split(command_line)
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
        
        except EOFError:  # Handle Ctrl+D gracefully
            sys.stdout.write("\n")
            break
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
