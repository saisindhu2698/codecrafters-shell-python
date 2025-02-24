import sys

def main():
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        command = input().strip()
        
        if command.startswith("exit "):
            try:
                exit_code = int(command.split()[1])
                sys.exit(exit_code)
            except (IndexError, ValueError):
                print("exit: invalid argument")
                continue
        elif command.startswith("echo "):
            print(command[5:])
        else:
            print(f"{command}: command not found")

if __name__ == "__main__":
    main()
