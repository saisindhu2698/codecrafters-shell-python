import pathlib
import readline
from typing import Final

SHELL_BUILTINS: Final[list[str]] = [
    "echo",
    "exit",
    "type",
    "pwd",
    "cd",
]

# Let's assume PROGRAMS_IN_PATH is built elsewhere:
PROGRAMS_IN_PATH: dict[str, pathlib.Path] = {
    # e.g., "ls": pathlib.Path("/bin/ls"),
    # Populate with executables found in PATH...
}

COMPLETIONS: Final[list[str]] = [*SHELL_BUILTINS, *PROGRAMS_IN_PATH.keys()]

# Global variables to track completion state
_last_text: str = ""
_tab_count: int = 0

def display_matches(substitution: str, matches: list[str], longest_match_length: int) -> None:
    """Hook for readline that displays matches after the second TAB press."""
    # Only print matches if more than one option
    if matches:
        print()  # newline before list
        print("  ".join(matches))
    # Reprint the prompt with current substitution
    print("$ " + substitution, end="")

def complete(text: str, state: int) -> str | None:
    """
    A completer function that, if multiple matches exist, rings a bell on the first TAB press
    and shows all matching completions on the second TAB press.
    """
    global _last_text, _tab_count

    # Compute all matches starting with the given text.
    matches = sorted({s for s in COMPLETIONS if s.startswith(text)})

    # If the completion text changed, reset the tab counter.
    if text != _last_text:
        _last_text = text
        _tab_count = 0

    # Only when multiple matches exist do we handle the TAB behavior.
    if len(matches) > 1:
        if _tab_count == 0:
            # On the first TAB press, ring the bell.
            print("\a", end="", flush=True)
            _tab_count += 1
            return None  # Do not complete yet.
        elif _tab_count == 1:
            # On the second TAB press, the display hook will be used to show matches.
            _tab_count = 0  # Reset for next round.
            # Return None so that readline calls the display hook.
            return None

    # If exactly one match exists or we're iterating over matches,
    # then return the match. Append a space if it is a builtin.
    if matches:
        candidate = matches[state] if state < len(matches) else None
        if candidate is None:
            return None
        if candidate in SHELL_BUILTINS:
            return candidate + " "
        else:
            return candidate + " "  # For external commands, add a space.
    else:
        return None

# Set the custom display hook and completer.
readline.set_completion_display_matches_hook(display_matches)
readline.set_completer(complete)
readline.parse_and_bind("tab: complete")

# A simple loop to test completion behavior.
if __name__ == "__main__":
    try:
        while True:
            line = input("$ ")
            # For testing, simply echo the entered command.
            print("You entered:", line)
    except EOFError:
        print()  # For a graceful exit.
