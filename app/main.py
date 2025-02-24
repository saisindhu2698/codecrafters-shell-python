import sys

def main():
    builtins = {"echo", "exit", "type"}
    
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
        elif command.startswith("type "):
            cmd_name = command.split()[1]
            if cmd_name in builtins:
                print(f"{cmd_name} is a shell builtin")
            else:
                print(f"{cmd_name}: not found")
        else:
            print(f"{command}: command not found")

if __name__ == "__main__":
    main()
