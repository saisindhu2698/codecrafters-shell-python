import os
import sys
import shlex
import pathlib
import readline
import subprocess  # Add this import to handle external commands
from typing import Final, TextIO, Mapping

# Constants
SHELL_BUILTINS: Final[list[str]] = [
    "echo",
    "exit",
    "type",
    "pwd",
    "cd",
]

def parse_programs_in_path(path: str, programs: dict[str, pathlib.Path]) -> None:
    """Creates a mapping of programs in path to their paths"""
    for p, _, bins in pathlib.Path(path).walk():
        for b in bins:
            programs[b] = p / b

def generate_program_paths() -> Mapping[str, pathlib.Path]:
    programs: dict[str, pathlib.Path] = {}
    for p in (os.getenv("PATH") or "").split(":"):
        parse_programs_in_path(p, programs)
    return programs

PROGRAMS_IN_PATH: Final[Mapping[str, pathlib.Path]] = {**generate_program_paths()}
COMPLETIONS: Final[list[str]] = [*SHELL_BUILTINS, *PROGRAMS_IN_PATH.keys()]

def display_matches(substitution, matches, longest_match_length):
    """Displays autocompletion matches"""
    print()
    if matches:
        print("  ".join(matches))
    print("$ " + substitution, end="")

def complete(text: str, state: int) -> str | None:
    """Provides autocompletion"""
    matches = list(set([s for s in COMPLETIONS if s.startswith(text)]))
    if len(matches) == 1:
        return matches[state] + " " if state < len(matches) else None
    return matches[state] if state < len(matches) else None

# Set up readline for autocompletion
readline.set_completion_display_matches_hook(display_matches)
readline.parse_and_bind("tab: complete")
readline.set_completer(complete)

def main():
    current_dir = os.getcwd()  # Track the current directory for `cd`
    
    while True:
        sys.stdout.write("$ ")
        cmds = shlex.split(input())
        out = sys.stdout
        err = sys.stderr
        close_out = False
        close_err = False
        try:
            # Handle output redirection (standard and error)
            if ">" in cmds:
                out_index = cmds.index(">")
                out = open(cmds[out_index + 1], "w")
                close_out = True
                cmds = cmds[:out_index] + cmds[out_index + 2:]
            elif "1>" in cmds:
                out_index = cmds.index("1>")
                out = open(cmds[out_index + 1], "w")
                close_out = True
                cmds = cmds[:out_index] + cmds[out_index + 2:]
            if "2>" in cmds:
                out_index = cmds.index("2>")
                err = open(cmds[out_index + 1], "w")
                close_err = True
                cmds = cmds[:out_index] + cmds[out_index + 2:]
            if ">>" in cmds:
                out_index = cmds.index(">>")
                out = open(cmds[out_index + 1], "a")
                close_out = True
                cmds = cmds[:out_index] + cmds[out_index + 2:]

            # Execute the command
            if cmds:
                if cmds[0] in SHELL_BUILTINS:
                    if cmds[0] == "exit":
                        break
                    elif cmds[0] == "cd":
                        if len(cmds) > 1:
                            target_dir = cmds[1]
                            if target_dir == "~":
                                target_dir = os.path.expanduser("~")  # Expand ~ to home directory
                            try:
                                os.chdir(target_dir)
                                current_dir = os.getcwd()
                            except FileNotFoundError:
                                err.write(f"{target_dir}: No such file or directory\n")
                        else:
                            os.chdir(os.path.expanduser("~"))
                            current_dir = os.getcwd()
                    elif cmds[0] == "pwd":
                        out.write(f"{current_dir}\n")
                    elif cmds[0] == "type":
                        if len(cmds) > 1:
                            out.write(f"{cmds[1]} is a shell built-in command.\n")
                    elif cmds[0] == "echo":
                        out.write(" ".join(cmds[1:]) + "\n")
                else:
                    # Handle external commands using subprocess
                    try:
                        subprocess.run(cmds, stdout=out, stderr=err)
                    except FileNotFoundError:
                        err.write(f"{cmds[0]}: command not found\n")
        except Exception as e:
            err.write(f"Error: {str(e)}\n")
        finally:
            # Close files if needed
            if close_out:
                out.close()
            if close_err:
                err.close()

if __name__ == "__main__":
    main()
