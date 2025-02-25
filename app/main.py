import sys
import os
import readline
import shlex
import subprocess

auto_complete_state = {}

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
    builtin = ["echo", "exit", "type", "pwd", "cd"]
    matches = set(cmd for cmd in builtin if cmd.startswith(text))
    
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    for directory in path_dirs:
        try:
            for filename in os.listdir(directory):
                if filename.startswith(text) and os.access(os.path.join(directory, filename), os.X_OK):
                    matches.add(filename)
        except FileNotFoundError:
            continue
    
    matches = sorted(matches)
    
    if len(matches) > 1:
        common_prefix = longest_common_prefix(matches)
        if common_prefix and common_prefix != text:
            return common_prefix if state == 0 else None
        if state == 0:
            print("\n" + "  ".join(matches))
            sys.stdout.write("$ " + text)
            sys.stdout.flush()
        return None
    
    return matches[state] + " " if state < len(matches) else None

def main():
    builtin = ["echo", "exit", "type", "pwd", "cd"]
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
