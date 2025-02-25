import sys
import os
import readline
import shlex
import subprocess

def completer(text, state):
    """Autocomplete commands and executables from the PATH environment variable."""
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
        return matches[state] + " "  # Add a space after the completion for proper autocomplete
    return None

def execute_command(command_line):
    """Process and execute the given command line."""
    HOME = os.environ.get("HOME", "")
    args = shlex.split(command_line)
    output_file = None
    
    # Handle redirection '>' or '1>'
    if '>' in args or '1>' in args:
        redir_index = args.index('>') if '>' in args else args.index('1>')
        if redir_index + 1 >= len(args):
            sys.stderr.write("Error: No file specified for redirection\n")
            return ""
        output_file = args[redir_index + 1]
        args = args[:redir_index]
    
    if not args:
        return ""

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
        return error_output
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
        return output  # Return the output from the redirection handling
    else:
        return output + error_output

def main():
    """Main function to run the shell program."""
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        try:
            command_line = input().strip()
            if not command_line:
                continue
            
            result = execute_command(command_line)

            # Output the result or error message
            if result:
                sys.stdout.write(result)
                sys.stdout.flush()

        except EOFError:
            sys.stdout.write("\n")
            break
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()
