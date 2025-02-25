import os
import sys
import subprocess

def split_input(inp):
    """Splits the input string into a list of words and handles redirection."""
    i = 0
    inpList = []  # List to store individual command parts
    toFile = ""   # Variable to store file for redirection
    curWord = ""  # Variable to accumulate characters for the current word

    while i < len(inp):
        # Escape sequence handling
        if inp[i] == "\\":
            curWord += inp[i + 1]  # Add the next character to curWord
            i += 1
        # Handle space: time to separate words, unless we're inside a redirection
        elif inp[i] == " ":
            if ">" in curWord:  # If the word contains '>', it's a redirection
                toFile = inp[i + 1 :]  # Capture the output file from the input
                return inpList, toFile
            if curWord:  # If curWord has any content, append it to inpList
                inpList.append(curWord)
            curWord = ""  # Reset curWord for next word
        # Handle single quotes for words containing special characters
        elif inp[i] == "'":
            i += 1
            while inp[i] != "'":  # Capture everything inside single quotes
                curWord += inp[i]
                i += 1
        # Handle double quotes (escaping certain characters within)
        elif inp[i] == '"':
            i += 1
            while inp[i] != '"':  # Capture everything inside double quotes
                if inp[i] == "\\" and inp[i + 1] in ["\\", "$", '"']:  # Handle escaped characters
                    curWord += inp[i + 1]
                    i += 2
                else:
                    curWord += inp[i]
                    i += 1
        else:
            curWord += inp[i]  # Regular characters are just added to curWord
        i += 1

    inpList.append(curWord)  # Add the last word to inpList
    return inpList, toFile  # Return the command list and redirection file

def main():
    """Main loop that runs the shell program."""
    exited = False  # Flag to track if the shell should exit
    path_list = os.environ["PATH"].split(":")  # Get directories listed in PATH
    builtin_list = ["exit", "echo", "type", "pwd", "cd"]  # Built-in commands
    
    while not exited:
        sys.stdout.write("$ ")  # Display prompt
        userinp = input()  # Wait for user input
        
        # Split the input into a list of words and determine file redirection
        inpList, toFile = split_input(userinp)
        
        output = ""  # Default output to empty
        # Matching based on the first word in the input (command)
        match inpList[0]:
            case "cd":
                # Change directory, handle '~' for HOME
                path = inpList[1]
                if path == "~":
                    os.chdir(os.environ["HOME"])
                elif os.path.isdir(path):
                    os.chdir(path)
                else:
                    output = path + ": No such file or directory"
            case "pwd":
                output = os.getcwd()  # Get current working directory
            case "type":
                # Check if the input command is in the PATH or is a built-in command
                for path in path_list:
                    if os.path.isfile(f"{path}/{inpList[1]}"):
                        output = inpList[1] + " is " + f"{path}/{inpList[1]}"
                        break
                if inpList[1] in builtin_list:
                    output = inpList[1] + " is a shell builtin"
                if not output:
                    output = inpList[1] + ": not found"
            case "echo":
                output = " ".join(inpList[1:])  # Print the arguments after echo
            case "exit":
                exited = True  # Set the flag to exit the loop
            case _:
                # For other commands, try to find them in the PATH and execute
                isCmd = False
                for path in path_list:
                    p = f"{path}/{inpList[0]}"
                    if os.path.isfile(p):
                        output = subprocess.run(
                            [p] + inpList[1:], stdout=subprocess.PIPE, text=True
                        ).stdout.rstrip()
                        isCmd = True
                        break
                if not isCmd:
                    output = userinp + ": command not found"
        
        # If no file redirection, print the output to standard output
        if not toFile:
            if output:
                print(output, file=sys.stdout)
        else:
            # If there's redirection, append output to the specified file
            with open(toFile, "a") as f:
                print(output, end="", file=f)

if __name__ == "__main__":
    main()
