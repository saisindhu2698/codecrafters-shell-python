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

def execute_command(args, redirect_stdout=None, append_stdout=False,
                    redirect_stderr=None, append_stderr=False):
    builtin = ["echo", "exit", "type", "pwd", "cd"]
    PATH = os.environ.get("PATH")
    HOME = os.environ.get("HOME")
    command = args[0]

    # Setup stdout redirection if specified.
    if redirect_stdout:
        mode = "a" if append_stdout else "w"
        try:
            f_stdout = open(redirect_stdout, mode)
        except Exception as e:
            sys.stderr.write(f"Error opening {redirect_stdout}: {e}\n")
            return
        target_stdout = f_stdout
    else:
        target_stdout = sys.stdout

    # Setup stderr redirection if specified.
    if redirect_stderr:
        mode = "a" if append_stderr else "w"
        try:
            f_stderr = open(redirect_stderr, mode)
        except Exception as e:
            sys.stderr.write(f"Error opening {redirect_stderr}: {e}\n")
            if redirect_stdout:
                f_stdout.close()
            return
        target_stderr = f_stderr
    else:
        target_stderr = sys.stderr

    # For built-in commands, temporarily replace sys.stderr if needed.
    original_stderr = sys.stderr
    if redirect_stderr:
        sys.stderr = target_stderr

    if command == "exit":
        sys.exit(0)
    elif command == "echo":
        target_stdout.write(" ".join(args[1:]) + "\n")
        target_stdout.flush()
    elif command == "pwd":
        target_stdout.write(os.getcwd() + "\n")
        target_stdout.flush()
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
                target_stdout.write(f"{new_command} is a shell builtin\n")
            elif cmd_path:
                target_stdout.write(f"{new_command} is {cmd_path}\n")
            else:
                sys.stderr.write(f"{new_command}: not found\n")
        target_stdout.flush()
    else:
        # External command: locate in PATH.
        cmd_path = None
        for path in PATH.split(os.pathsep):
            full_path = os.path.join(path, command)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                cmd_path = full_path
                break
        if cmd_path:
            try:
                # Pass the proper file handles to subprocess.run.
                result = subprocess.run(
                    args,
                    stdout=(target_stdout if redirect_stdout else subprocess.PIPE),
                    stderr=(target_stderr if redirect_stderr else subprocess.PIPE),
                    text=True
                )
                if not redirect_stdout:
                    sys.stdout.write(result.stdout)
                if not redirect_stderr:
                    sys.stderr.write(result.stderr)
            except Exception as e:
                sys.stderr.write(f"Error executing command: {e}\n")
        else:
            sys.stderr.write(f"{command}: command not found\n")

    # Restore original stderr if replaced.
    if redirect_stderr:
        sys.stderr = original_stderr

    if redirect_stdout:
        f_stdout.close()
    if redirect_stderr:
        f_stderr.close()
    sys.stdout.flush()

def main():
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        try:
            command_line = input().strip()
            if not command_line:
                continue

            # Use shlex to split the command line.
            args = shlex.split(command_line)

            # Initialize redirection variables.
            redirect_stdout = None
            append_stdout = False
            redirect_stderr = None
            append_stderr = False

            # Check for stderr append redirection (operator "2>>")
            if "2>>" in args:
                idx = args.index("2>>")
                if idx + 1 >= len(args):
                    sys.stderr.write("Syntax error: expected filename after '2>>'\n")
                    continue
                redirect_stderr = args[idx + 1]
                append_stderr = True
                args = args[:idx] + args[idx+2:]
            # Check for stderr redirection (operator "2>") if "2>>" not present.
            elif "2>" in args:
                idx = args.index("2>")
                if idx + 1 >= len(args):
                    sys.stderr.write("Syntax error: expected filename after '2>'\n")
                    continue
                redirect_stderr = args[idx + 1]
                append_stderr = False
                args = args[:idx] + args[idx+2:]

            # Check for stdout appending redirection (operators ">>" or "1>>")
            if ">>" in args:
                idx = args.index(">>")
                if idx + 1 >= len(args):
                    sys.stderr.write("Syntax error: expected filename after '>>'\n")
                    continue
                redirect_stdout = args[idx + 1]
                append_stdout = True
                args = args[:idx]
            elif "1>>" in args:
                idx = args.index("1>>")
                if idx + 1 >= len(args):
                    sys.stderr.write("Syntax error: expected filename after '1>>'\n")
                    continue
                redirect_stdout = args[idx + 1]
                append_stdout = True
                args = args[:idx]
            # Check for stdout redirection (operators ">" or "1>")
            elif ">" in args:
                idx = args.index(">")
                if idx + 1 >= len(args):
                    sys.stderr.write("Syntax error: expected filename after '>'\n")
                    continue
                redirect_stdout = args[idx + 1]
                append_stdout = False
                args = args[:idx]
            elif "1>" in args:
                idx = args.index("1>")
                if idx + 1 >= len(args):
                    sys.stderr.write("Syntax error: expected filename after '1>'\n")
                    continue
                redirect_stdout = args[idx + 1]
                append_stdout = False
                args = args[:idx]

            if not args:
                sys.stderr.write("Syntax error: no command specified\n")
                continue

            execute_command(args, redirect_stdout=redirect_stdout, append_stdout=append_stdout,
                            redirect_stderr=redirect_stderr, append_stderr=append_stderr)
        except EOFError:
            sys.stdout.write("\n")
            break
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
