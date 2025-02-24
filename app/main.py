import os
import sys
import readline
from typing import Optional

# Dictionary to track the number of times Tab is pressed for a specific prefix
tab_press_count = {}

def display_matches(substitution: str, matches: list[str], longest_match_length: int):
    try:
        if len(matches) > 1:
            # When there are multiple matches, print them on a new line
            sys.stdout.write("\n")
            sys.stdout.write("  ".join(sorted(matches)) + "\n")
        sys.stdout.write(f"$ {substitution}")  # After displaying matches, show the prompt
        sys.stdout.flush()
        readline.redisplay()  # Redraw the prompt
    except Exception as e:
        sys.stderr.write(f"Error displaying matches: {e}\n")

def complete(text: str, state: int) -> Optional[str]:
    global tab_press_count

    if text not in tab_press_count:
        tab_press_count[text] = 0  # Initialize the tab press count for this prefix
    
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    matches = []

    # Find all executables that match the prefix
    for directory in path_dirs:
        try:
            for filename in os.listdir(directory):
                if filename.startswith(text) and os.access(os.path.join(directory, filename), os.X_OK):
                    matches.append(filename)
        except FileNotFoundError:
            continue

    matches = sorted(set(matches))  # Remove duplicates and sort

    # Handle tab press logic
    if len(matches) > 1:  # More than one match found
        if tab_press_count[text] == 0:
            tab_press_count[text] += 1
            sys.stdout.write("\a")  # Ring the bell character
            sys.stdout.write(f"$ {text}")  # Display the current text (prefix) without repeating the prompt
            sys.stdout.flush()
            return None  # Wait for the second Tab press to show completions
        elif tab_press_count[text] == 1:
            # On second Tab press, display the matches and the prompt
            display_matches(text, matches, len(matches[0]))  # Display the matches
            tab_press_count[text] = 0  # Reset tab press count for this prefix
            return None
    return None

def setup_readline():
    """Setup readline for autocompletion and tab press handling."""
    readline.set_completer(complete)  # Set the completer function
    readline.set_completion_display_matches_hook(display_matches)  # Hook for displaying matches
    readline.parse_and_bind("tab: complete")  # Bind the Tab key for completion
    readline.parse_and_bind("set bell-style audible")  # Enable audible bell on Tab press
    readline.set_auto_history(True)  # Enable automatic history

# Main function to simulate a basic shell
def main():
    setup_readline()
    
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        command_line = input().strip()

        if command_line == "exit":
            break
        elif command_line:
            # Handle the command execution here (external or internal commands)
            pass

# Run the shell program
if __name__ == "__main__":
    main()
