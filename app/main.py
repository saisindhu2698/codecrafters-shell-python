import sys

def main():
    sys.stdout.write("$ ")
    sys.stdout.flush()
    
    command = input()
    
    if command.startswith("echo "):
        # Print the text following "echo " directly
        sys.stdout.write(command[5:] + "\n")
    elif command == "":
        pass
    else:
        sys.stdout.write(f"{command}: command not found\n")
    
    main()

if __name__ == "__main__":
    main()
