import sys
import os
import subprocess
import shlex

def find_executable(command):
    paths = os.getenv("PATH", "").split(":")
    for path in paths:
        exe_path = os.path.join(path, command)
        if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
            return exe_path
    return None

def mysplit(input):
    res = ['']
    current_quote = ''
    i = 0

    while i < len(input):
        c = input[i]
        if c == '\\':
            ch = input[i+1]
            if current_quote == "'":
                res[-1] += c
            elif current_quote == '"':
                if ch in ['\\', '$', '"', '\n']:
                    res[-1] += ch
                else:
                    res[-1] += '\\' + ch
                i += 1
            else:
                res[-1] += input[i+1]
                i += 1
        elif c in ['"',"'"]:
            if current_quote == '':
                current_quote = c
            elif current_quote == c:
                current_quote = ''
            else:
                res[-1] += c
        elif c == ' ' and current_quote == '':
            if res[-1] != '':
                res.append('')
        else:
            res[-1] += c
        i += 1
        
    if res[-1] == '':
        res.pop()

    return res

def main():
    builtins = {"echo", "exit", "type", "pwd", "cd"}
    
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        try:
            command = input().strip()
        except EOFError:
            break
        
        if not command:
            continue
        
        # Split the command properly using mysplit function
        inp = mysplit(command)
        
        # Check if there is output redirection using > or 1>
        to_redirect = None
        if '1>' in inp:
            idx = inp.index('1>')
            inp, to_redirect = inp[:idx], inp[idx+1]
        elif '>' in inp:
            idx = inp.index('>')
            inp, to_redirect = inp[:idx], inp[idx+1]

        # Parse the command using shlex to handle quotes and spaces
        cmd_name = inp[0]
        args = inp[1:]

        # Handle output redirection
        if to_redirect:
            try:
                with open(to_redirect, 'w') as f:
                    subprocess.run([cmd_name] + args, stdout=f, check=True)
            except FileNotFoundError:
                print(f"{cmd_name}: {to_redirect}: No such file or directory")
            except Exception as e:
                print(f"{cmd_name}: failed to execute: {e}")
        else:
            # Handle normal command execution without redirection
            if cmd_name == "exit":
                try:
                    exit_code = int(args[0]) if args else 0
                    sys.exit(exit_code)
                except ValueError:
                    print("exit: invalid argument")
                    continue
            elif cmd_name == "echo":
                # Echo command should print exactly what is in the arguments
                print(" ".join(args))
            elif cmd_name == "type":
                if args:
                    target_cmd = args[0]
                    if target_cmd in builtins:
                        print(f"{target_cmd} is a shell builtin")
                    else:
                        exe_path = find_executable(target_cmd)
                        if exe_path:
                            print(f"{target_cmd} is {exe_path}")
                        else:
                            print(f"{target_cmd}: not found")
                else:
                    print("type: missing argument")
            elif cmd_name == "pwd":
                print(os.getcwd())
            elif cmd_name == "cd":
                if len(args) != 1:
                    print("cd: too many arguments")
                else:
                    path = args[0]
                    if path == "~":
                        home = os.getenv("HOME")
                        if home is None:
                            print("cd: HOME environment variable not set")
                            continue
                        path = home
                    try:
                        os.chdir(path)
                    except FileNotFoundError:
                        print(f"cd: {args[0]}: No such file or directory")
                    except NotADirectoryError:
                        print(f"cd: {args[0]}: Not a directory")
                    except PermissionError:
                        print(f"cd: {args[0]}: Permission denied")
            else:
                exe_path = find_executable(cmd_name)
                if exe_path:
                    try:
                        subprocess.run([cmd_name] + args, check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"{cmd_name}: process exited with status {e.returncode}")
                    except Exception as e:
                        print(f"{cmd_name}: failed to execute: {e}")
                else:
                    print(f"{cmd_name}: command not found")

if __name__ == "__main__":
    main()
