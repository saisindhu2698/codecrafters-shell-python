import os
import sys
import readline

def get_executables(prefix):
    """Finds all executables in PATH that start with the given prefix."""
    matches = []
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)

    for directory in path_dirs:
        try:
            for filename in os.listdir(directory):
                if filename.startswith(prefix) and os.access(os.path.join(directory, filename), os.X_OK):
                    matches.append(filename)
        except FileNotFoundError:
            continue  # Skip missing directories

    return sorted(matches)

def longest_common_prefix(strings):
    """Finds the longest common prefix among a list of strings."""
    if not strings:
        return ""

    prefix = strings[0]
    for string in strings[1:]:
        while not string.startswith(prefix):
            prefix = prefix[:-1]  # Trim the last character
            if not prefix:
                return ""
    return prefix

def completer(text, state):
    """Autocomplete function handling prefix-based completion."""
    matches = get_executables(text)

    # If there's only one match, return it fully
    if len(matches) == 1:
        return matches[0] + " " if state == 0 else None

    # If there are multiple matches, find the longest common prefix
    if matches:
        common_prefix = longest_common_prefix(matches)
        if common_prefix != text:  # Only complete if there's new content
            readline.insert_text(common_prefix)
            readline.redisplay()
            return None  # Don't return anything, we manually update the text

        # If already at the longest prefix, return individual matches
        return matches[state] if state < len(matches) else None

    return None  # No matches found

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
            os.system(command_line)  # Execute the command
        except EOFError:
            sys.stdout.write("\n")
            break
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
