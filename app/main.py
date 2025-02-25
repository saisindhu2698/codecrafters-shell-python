import sys
import os
import readline
import shlex
import subprocess

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
        return matches[state]  # Return the matched command without extra space
    return None


def main():
    HOME = os.environ.get("HOME", "")
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
            if '>' in args or '1>' in args:
                redir_index = args.index('>') if '>' in args else args.index('1>')
                if redir_index + 1 >= len(args):
                    sys.stderr.write("Error: No file specified for redirection\n")
                    continue
                output_file = args[redir_index + 1]
                args = args[:redir_index]
            
            if not args:
                continue
            
            command = args[0]
            output = ""
            error_output = ""
            
            if command == "exit":
                sys.exit(0)
            elif command == "pwd":
                output = os.getcwd() + "\n"
            elif command == "cd":
                directory = args[1] if len(args) > 1 else HOME
                try:
                    os.chdir(directory)
                except Exception as e:
                    error_output = f"cd: {directory}: {str(e)}\n"
                continue
            elif command == "echo":
                output = " ".join(args[1:]) + "\n"
            else:
                try:
                    result = subprocess.run(args, capture_output=True, text=True, check=True)
                    output = result.stdout
                    error_output = result.stderr
                except subprocess.CalledProcessError as e:
                    output = e.stdout
                    error_output = e.stderr
                except FileNotFoundError:
                    error_output = f"{command}: command not found\n"
            
            if output_file:
                try:
                    with open(output_file, "w") as f:
                        f.write(output)
                except Exception as e:
                    error_output += f"Error writing to file {output_file}: {e}\n"
            else:
                sys.stdout.write(output)
                sys.stdout.flush()
            
            if error_output:
                sys.stderr.write(error_output)
                sys.stderr.flush()
        except EOFError:
            sys.stdout.write("\n")
            break
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()
