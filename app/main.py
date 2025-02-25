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
        seen = set()
        for directory in path_dirs:
            try:
                for filename in os.listdir(directory):
                    full_path = os.path.join(directory, filename)
                    if filename.startswith(text) and os.access(full_path, os.X_OK) and os.path.isfile(full_path) and filename not in seen:
                        matches.append(filename)
                        seen.add(filename)
            except FileNotFoundError:
                continue

    matches.sort()

    if len(matches) > 1:
        if state == 0:  # First tab press
            if not tab_pressed:
                tab_pressed = True
                sys.stdout.write("\a")
                sys.stdout.flush()
                return None
            else:  # Second tab press
                tab_pressed = False
                output_string = "  ".join(matches)  # Two spaces
                sys.stdout.write("\n" + output_string + "\n$ " + text)
                sys.stdout.flush()
                return None
        else:  # Subsequent tab presses
            tab_pressed = False
            if state < len(matches):
                return matches[state]
            else:
                return None

    elif len(matches) == 1:
        return matches[state] if state < len(matches) else None

    return None


def main():
    # *** ISOLATION STEP 1: MINIMAL REPRODUCIBLE EXAMPLE ***
    # Comment out everything except the following lines:
    # sys.stdout.write("$ custom_exe_7734\n")
    # sys.stdout.flush()
    # return  # Exit immediately to isolate

    #global tab_pressed
    #readline.set_completer(completer)
    #readline.parse_and_bind("tab: complete")

    while True:
        sys.stdout.write("$ ") # *** ISOLATION STEP 3: CHECK PROMPT ***
        sys.stdout.flush()
        try:
            command_line = input().strip()
            if not command_line:
                continue

            tab_pressed = False

            args = shlex.split(command_line)
            if not args:
                continue

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
                directory = args[1] if len(args) > 1 else os.environ.get("HOME", "/")
                try:
                    os.chdir(directory)
                except Exception as e:
                    sys.stderr.write(f"cd: {directory}: {str(e)}\n")
                    sys.stderr.flush()
                sys.stdout.flush()
            elif command == "type":
                if len(args) < 2:
                    sys.stderr.write("type: missing argument\n")
                    sys.stderr.flush()
                else:
                    new_command = args[1]
                    if new_command in ["echo", "exit", "type", "pwd", "cd"]:
                        sys.stdout.write(f"{new_command} is a shell builtin\n")
                        sys.stdout.flush()
                    else:
                        found = False
                        for path in os.environ.get("PATH", "").split(os.pathsep):
                            full_path = os.path.join(path, new_command)
                            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                                sys.stdout.write(f"{new_command} is {full_path}\n")
                                sys.stdout.flush()
                                found = True
                                break
                        if not found:
                            sys.stderr.write(f"{new_command}: not found\n")
                            sys.stderr.flush()
            else:
                try:
                    result = subprocess.run(args, capture_output=True, text=True, check=True)
                    sys.stdout.write(result.stdout)
                    sys.stderr.write(result.stderr)
                    sys.stdout.flush()
                    sys.stderr.flush()
                except subprocess.CalledProcessError as e:
                    sys.stderr.write(f"Error: {e}\n")
                    sys.stderr.write(e.stderr)
                    sys.stderr.flush()
                except Exception as e:
                    sys.stderr.write(f"Error: {e}\n")
                    sys.stderr.flush()

        except EOFError:
            sys.stdout.write("\n")
            break
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.stderr.flush()


if __name__ == "__main__":
    main()