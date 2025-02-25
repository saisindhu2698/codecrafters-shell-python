import sys
import os
import readline
import shlex
import subprocess

def longest_common_prefix(strs):
    if not strs:
        return ""
    shortest = min(strs, key=len)
    for i, char in enumerate(shortest):
        for other in strs:
            if other[i] != char:
                return shortest[:i]
    return shortest

def completer(text, state):
    matches = []
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    for directory in path_dirs:
        try:
            for filename in os.listdir(directory):
                if filename.startswith(text) and os.access(os.path.join(directory, filename), os.X_OK):
                    matches.append(filename)
        except FileNotFoundError:
            continue
    matches = sorted(matches)
    if state < len(matches):
        return matches[state]
    return None

def main():
    PATH = os.environ.get("PATH")
    HOME = os.environ.get("HOME")
    
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
            output_file = None
            redir_index = None
            
            if '>' in args or '1>' in args:
                redir_index = args.index('>') if '>' in args else args.index('1>')
                if len(args) <= redir_index + 1:
                    sys.stderr.write("Error: No file specified for redirection\n")
                    continue
                output_file = args[redir_index + 1]
                args = args[:redir_index]
            
            if not args:
                continue
            
            command = args[0]
            if command == "exit":
                sys.exit(0)
            elif command == "pwd":
                output = os.getcwd() + "\n"
            elif command == "cd":
                directory = args[1] if len(args) > 1 else HOME
                try:
                    os.chdir(directory)
                except FileNotFoundError:
                    sys.stderr.write(f"cd: {directory}: No such file or directory\n")
                    continue
                except PermissionError:
                    sys.stderr.write(f"cd: {directory}: Permission denied\n")
                    continue
                except Exception as e:
                    sys.stderr.write(f"cd: {directory}: {str(e)}\n")
                    continue
                continue
            elif command == "echo":
                output = " ".join(args[1:]) + "\n"
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
                        output = result.stdout
                        error_output = result.stderr
                    except Exception as e:
                        sys.stderr.write(f"Error executing command: {e}\n")
                        continue
                else:
                    sys.stderr.write(f"{command}: command not found\n")
                    continue
            
            if output_file:
                try:
                    with open(output_file, "w") as f:
                        if output:
                            f.write(output)
                    if error_output:
                        sys.stderr.write(error_output)
                except Exception as e:
                    sys.stderr.write(f"Error writing to file {output_file}: {e}\n")
            else:
                if output:
                    sys.stdout.write(output)
                if error_output:
                    sys.stderr.write(error_output)
            sys.stdout.flush()
        except EOFError:
            sys.stdout.write("\n")
            break
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()