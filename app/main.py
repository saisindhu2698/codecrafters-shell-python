import sys

def main():
    # Print the shell prompt
    sys.stdout.write("$ ")

    # Wait for user input
    command = input().strip()

    # Split the command into parts
    parts = command.split()

    # Check if the command is "echo"
    if parts and parts[0] == "echo":
        # Print everything after "echo"
        print(" ".join(parts[1:]))
    else:
        # Print error for invalid commands (or handle other builtins)
        print(f"{command}: command not found")
    
    # Continue the loop
    main()

if __name__ == "__main__":
    main()