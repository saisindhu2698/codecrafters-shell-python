import sys
import os
import readline
import shlex
import subprocess

tab_pressed = False

def completer(text, state):
    global tab_pressed
    builtin = ["echo ", "exit ", "type ", "pwd ", "cd "]
    matches = []

    matches.extend([cmd for cmd in builtin if cmd.startswith(text)])

    if not matches:
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        seen = set()  # Keep track of seen filenames
        for directory in path_dirs:
            try:
                for filename in os.listdir(directory):
                    full_path = os.path.join(directory, filename)
                    if filename.startswith(text) and os.access(full_path, os.X_OK) and os.path.isfile(full_path) and filename not in seen:
                        matches.append(filename)
                        seen.add(filename)  # Mark as seen
            except FileNotFoundError:
                continue

    matches.sort()

    if len(matches) > 1:
        if state == 0:
            # ... (bell ringing code)
            return None
        else:
            tab_pressed = False
            # Join with *regular* spaces
            output_string = " ".join(matches)
            sys.stdout.write("\n" + output_string + "\n$ " + text)
            sys.stdout.flush()
            return None
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

            tab_pressed = False

            args = shlex.split(command_line)
            if not args: #Handle empty command
                continue
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
