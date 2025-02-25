import sys
import os
import readline
import shlex
import subprocess
import pathlib
from typing import Final, TextIO

SHELL_BUILTINS: Final[list[str]] = ["echo", "exit", "type", "pwd", "cd"]

PROGRAMS_IN_PATH: dict[str, pathlib.Path] = {}
for path in os.environ["PATH"].split(os.pathsep):
    if not path:
        continue
    p = pathlib.Path(path)
    if not p.is_dir():
        continue
    for program in p.iterdir():
        if program.is_file() and os.access(program, os.X_OK):
            PROGRAMS_IN_PATH[program.name] = program

COMPLETIONS: Final[list[str]] = [*SHELL_BUILTINS, *PROGRAMS_IN_PATH.keys()]

def display_matches(substitution, matches, longest_match_length):
    if matches:
        print()
        print("  ".join(matches))
    print("$ " + substitution, end="")
    sys.stdout.flush()
def complete(text: str, state: int) -> str | None:
    matches = list(set([s for s in COMPLETIONS if s.startswith(text)]))
    matches.sort()

    if len(matches) > 1:
        if state == 0:  # First tab press
            sys.stdout.write("\a")  # Ring the bell
            sys.stdout.flush()
            return None  # Important: Return None for multiple matches

        elif state is None: # Second tab press (state becomes None)
            output_string = "  ".join(matches)
            print() # Newline before matches
            print(output_string) # Print the matches
            print("$ " + text, end="") #Print the prompt with the typed text
            sys.stdout.flush()
            return None # Important: Return None after printing matches

        else: # Subsequent tab presses (try to complete)
            try:
                return matches[state] + " " if state < len(matches) else None
            except IndexError:
                return None

    elif len(matches) == 1:
        return matches[state] + " " if state < len(matches) else None
    return None

# readline.set_completion_display_matches_hook(display_matches)  # Remove this line
readline.set_completer(complete)
readline.parse_and_bind("tab: complete")

def main():
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        try:
            command_line = input().strip()
            if not command_line:
                continue

            cmds = shlex.split(command_line)
            out = sys.stdout
            err = sys.stderr
            close_out = False
            close_err = False
            try:
                # Redirection logic (remains the same)
                if ">" in cmds: # ... (redirection logic)
                    pass # Placeholder
                elif "1>" in cmds: # ... (redirection logic)
                    pass # Placeholder
                elif "2>" in cmds: # ... (redirection logic)
                    pass # Placeholder
                elif ">>" in cmds: # ... (redirection logic)
                    pass # Placeholder
                elif "1>>" in cmds: # ... (redirection logic)
                    pass # Placeholder
                elif "2>>" in cmds: # ... (redirection logic)
                    pass # Placeholder

                handle_all(cmds, out, err)
            finally:
                if close_out:
                    out.close()
                if close_err:
                    err.close()

        except EOFError:
            print()  # Add newline for EOFError
            break

def handle_all(cmds: list[str], out: TextIO, err: TextIO):
    match cmds:
        case ["echo", *s]:
            out.write(" ".join(s) + "\n")
            out.flush()
        case ["type", s]:
            type_command(s, out, err)
        case ["exit", "0"]:
            sys.exit(0)
        case ["pwd"]:
            out.write(os.getcwd() + "\n")
            out.flush()
        case ["cd", dir]:
            cd(dir, out, err)
        case [cmd, *args] if cmd in PROGRAMS_IN_PATH:
            try:
                process = subprocess.Popen([cmd, *args], stdout=out, stderr=err, text=True) # text=True added
                process.wait()
            except FileNotFoundError:
                err.write(f"{cmd}: command not found\n")
                err.flush()
            except subprocess.CalledProcessError as e:  # Catch subprocess errors
                err.write(f"{cmd}: {e}\n") #Print error and stderr
                err.write(e.stderr.decode()) #Decode stderr if its bytes
                err.flush()
        case command:
            out.write(f"{' '.join(command)}: command not found\n")
            out.flush()

def type_command(command: str, out: TextIO, err: TextIO):
    if command in SHELL_BUILTINS:
        out.write(f"{command} is a shell builtin\n")
        out.flush()
        return

    if command in PROGRAMS_IN_PATH:
        out.write(f"{command} is {PROGRAMS_IN_PATH[command]}\n")
        out.flush()
        return

    out.write(f"{command}: not found\n")
    out.flush()

def cd(path: str, out: TextIO, err: TextIO) -> None:
    if path.startswith("~"):
        home = os.getenv("HOME") or "/root"
        path = path.replace("~", home)
    p = pathlib.Path(path)
    if not p.exists():
        err.write(f"cd: {path}: No such file or directory\n")
        err.flush()
        return
    try:
        os.chdir(p)
    except OSError as e: #Catch OSError for cd failures
        err.write(f"cd: {path}: {e}\n")
        err.flush()


if __name__ == "__main__":
    main()