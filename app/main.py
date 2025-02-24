import sys
import os
import subprocess
import shlex

def find_executable(command):
    """Handles finding executables that may have spaces or quotes in their names."""
    # First check if the command is quoted (i.e., it contains spaces, quotes, or backslashes)
    if '"' in command or "'" in command:
        # Handle quoted executables, remove the quotes
        command = shlex.split(command)[0]
    
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

def parse_input(command):
    """Handles the parsing of commands with proper escaping and quoting."""
    result = []
    i = 0
    length = len(command)
    in_single_quote = False
    in_double_quote = False
    escape = False
    current = ""
    
    while i < length:
        char = command[i]

        # Handle escape character
        if escape:
            if in_double_quote:
                # In double quotes, the escape only applies to \, $, ", and newline
                if char in ['\\', '$', '"', '\n']:
                    current += char
                else:
                    current += '\\' + char
            else:
                current += char
            escape = False
            i += 1
            continue
        elif char == '\\':
            escape = True
        elif char == "'":
            if in_single_quote:
                result.append(current)
                current = ""
                in_single_quote = False
            else:
                if current:
                    result.append(current)
                    current = ""
                in_single_quote = True
        elif char == '"':
            if in_double_quote:
                result.append(current)
                current = ""
                in_double_quote = False
            else:
                if current:
                    result.append(current)
                    current = ""
                in_double_quote = True
        else:
            current += char
        
        i += 1
    
    if current:
        result.append(current)

    return result

def main():
    builtins = {"echo", "exit", "type", "pwd", "cd"}
    
    # Print the program name on startup
    print_program_name()

    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        try:
            command = input().strip()
        except EOFError:
            break
        
        if not command:
            continue
        
        # Parse the input command with support for backslash quoting and single quotes
        parsed_command = parse_input(command)
        
        # Handling redirection and file output
        if '>' in parsed_command:
            parts = ' '.join(parsed_command).split('>')  # Split around the redirection operator
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
            cmd_name = parsed_command[0]
            args = parsed_command[1:]
            
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
