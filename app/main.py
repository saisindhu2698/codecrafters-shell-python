from collections.abc import Mapping
import readline
import shlex
import subprocess
import sys
import pathlib
import os
from typing import Final, TextIO

SHELL_BUILTINS: Final[list[str]] = [
    "echo",
    "exit",
    "type",
    "pwd",
    "cd",
]


def parse_programs_in_path(path: str, programs: dict[str, pathlib.Path]) -> None:
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
    if matches:
        print()
        print("  ".join(matches))
    print("$ " + substitution, end="")


def complete(text: str, state: int) -> str | None:
    matches = list(set([s for s in COMPLETIONS if s.startswith(text)]))
    matches.sort()

    if len(matches) > 1:
        if state == 0:
            readline.set_completion_display_matches_hook(display_matches)
            return None
        else:
            return None

    elif len(matches) == 1:
        return matches[0] + " " if state == 0 else None

    return None


readline.set_completer(complete)
readline.parse_and_bind("tab: complete")


def main():
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        try:
            command_line = input()
            cmds = shlex.split(command_line)
            out = sys.stdout
            err = sys.stderr
            close_out = False
            close_err = False
            try:
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
                elif "1>>" in cmds:
                    out_index = cmds.index("1>>")
                    out = open(cmds[out_index + 1], "a")
                    close_out = True
                    cmds = cmds[:out_index] + cmds[out_index + 2:]

                if "2>>" in cmds:
                    out_index = cmds.index("2>>")
                    err = open(cmds[out_index + 1], "a")
                    close_err = True
                    cmds = cmds[:out_index] + cmds[out_index + 2:]

                handle_all(cmds, out, err)

            finally:
                if close_out:
                    out.close()
                if close_err:
                    err.close()

            if command_line and (len(complete(command_line.split()[0], 0)) == 1 or len(complete(command_line.split()[0], 0)) == 0):
                sys.stdout.write(" ")
                sys.stdout.flush()

        except EOFError:
            print()
            break

        except KeyboardInterrupt:
            print()
            break


def handle_all(cmds: list[str], out: TextIO, err: TextIO):
    match cmds:
        case ["echo", *s]:
            out.write(" ".join(s) + "\n")
        case ["type", s]:
            type_command(s, out, err)
        case ["exit"]:
            sys.exit(0)
        case ["pwd"]:
            out.write(f"{os.getcwd()}\n")
        case ["cd", dir]:
            cd(dir, out, err)
        case [cmd, *args] if cmd in PROGRAMS_IN_PATH:
            process = subprocess.Popen([cmd, *args], stdout=out, stderr=err)
            process.wait()
        case command:
            out.write(f"{' '.join(command)}: command not found\n")


def type_command(command: str, out: TextIO, err: TextIO):
    if command in SHELL_BUILTINS:
        out.write(f"{command} is a shell builtin\n")
        return

    if command in PROGRAMS_IN_PATH:
        out.write(f"{command} is {PROGRAMS_IN_PATH[command]}\n")
        return

    out.write(f"{command}: not found\n")


def cd(path: str, out: TextIO, err: TextIO) -> None:
    if path.startswith("~"):
        home = os.getenv("HOME") or "/root"
        path = path.replace("~", home)
    p = pathlib.Path(path)
    if not p.exists():
        out.write(f"cd: {path}: No such file or directory\n")
        return
    try:
        os.chdir(p)
    except OSError as e:
        out.write(f"cd: {path}: {e}\n")


if __name__ == "__main__":
    main()