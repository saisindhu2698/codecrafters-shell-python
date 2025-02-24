import sys
import os
import subprocess

def shell_prompt():
    while True:
        # Display the prompt
        print("$ ", end="", flush=True)
        
        # Read input from the user
        command = input().strip()
        
        # If the user types 'exit', exit the shell
        if command == "exit":
            break

        # Process the command (This part executes the command)
        execute_command(command)

def execute_command(command):
    # Check if the command contains redirection operator ">"
    if ">" in command:
        command_parts = command.split(">")
        cmd = command_parts[0].strip()
        file_name = command_parts[1].strip()

        # Redirect output to file
        with open(file_name, 'w') as f:
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                f.write(result.stdout)
            except subprocess.CalledProcessError as e:
                f.write(e.stderr)
        return

    # Handle regular commands
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout, end="")  # Print the output to the shell
    except subprocess.CalledProcessError as e:
        print(e.stderr, end="")  # Print errors if any

if __name__ == "__main__":
    shell_prompt()
