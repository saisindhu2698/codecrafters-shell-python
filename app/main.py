# main.py
import platform
import sys
from typing import Optional, TextIO
from .command_factory import CommandFactory
from .input_parser import InputParser, ParsedInput
from .shell_context import ShellContext
if platform.system == "Windows":
    from pyreadline3 import Readline
else:
    import readline
class Shell:
    def __init__(self) -> None:
        self._ctx = ShellContext()
        self._factory = CommandFactory(self._ctx)
        self._parser = InputParser()
        if platform.system == "Windows":
            self._readline = Readline()
            self._readline.parse_and_bind("tab: complete")
            self._readline.set_completer(self.complete)
        else:
            readline.parse_and_bind("tab: complete")  # type: ignore
            readline.set_completer(self.complete)  # type: ignore
            readline.set_completion_display_matches_hook(self.display_matches)  # type: ignore  # noqa: F821
            readline.parse_and_bind("set bell-style audible")  # type: ignore
            readline.set_auto_history(True)  # type: ignore
    def display_matches(
        self, substitution: str, matches: list[str], longest_match_length: int
    ):
        try:
            sys.stdout.write("\n")
            sys.stdout.write(" ".join(matches) + "\n")
            sys.stdout.write(f"$ {substitution}")
            sys.stdout.flush()
            readline.redisplay()  # type: ignore
        except Exception as e:
            sys.stderr.write(f"{e}")
    def complete(self, text: str, state: int) -> Optional[str]:
        ALL_COMMANDS = (
            self._ctx.get_built_in_commands() + self._ctx._utils.get_exe_list()
        )
        matches = [cmd + " " for cmd in ALL_COMMANDS if cmd.startswith(text)]
        return matches[state] if state < len(matches) else None
    def handle_external_command(
        self,
        command_name: str,
        args: list[str],
        output_stream: Optional[TextIO] = sys.stdout,
        err_stream: Optional[TextIO] = sys.stderr,
    ) -> None:
        subprocess = self._ctx._utils.get_subprocess()
        is_executable, _ = self._ctx._utils.search_for_exe(command_name)
        if not is_executable:
            if err_stream:
                err_stream.write(f"{command_name}: not found\n")
        else:
            command_args = [command_name] + args
            subprocess.call(command_args, stdout=output_stream, stderr=err_stream)
    def execute_parsed_input(self, parsed_input: ParsedInput):
        command = self._factory.create_command(
            parsed_input.command_name, parsed_input.args
        )
        output_stream = sys.stdout
        err_stream = sys.stderr
        # handle redirection and appending of stdout and stderr
        if parsed_input.redirect_to_stdout:
            if (
                parsed_input.redirection_symbol == ">>"
                or parsed_input.redirection_symbol == "1>>"
            ):
                output_stream = open(parsed_input.redirect_to_stdout, "a+")
            else:
                output_stream = open(parsed_input.redirect_to_stdout, "w")
        if parsed_input.redirect_to_stderr:
            if parsed_input.redirection_symbol == "2>>":
                err_stream = open(parsed_input.redirect_to_stderr, "a+")
            else:
                err_stream = open(parsed_input.redirect_to_stderr, "w")
        try:
            if command:
                # explicitly handle exit command
                if parsed_input.command_name == "exit":
                    if parsed_input.redirect_to_stdout:
                        output_stream.close()
                    if parsed_input.redirect_to_stderr:
                        err_stream.close()
                    command.execute()
                    return 0
                # else handle the command
                command.execute(output_stream=output_stream, err_stream=err_stream)
            elif (
                # handle external commands
                parsed_input.command_name not in self._ctx.get_built_in_commands()
                and parsed_input.args
                and isinstance(parsed_input.args, list)
            ):
                self.handle_external_command(
                    parsed_input.command_name,
                    parsed_input.args,
                    output_stream,
                    err_stream,
                )
            else:
                if err_stream:
                    err_stream.write(
                        f"{parsed_input.command_name}: command not found\n"
                    )
        finally:
            if parsed_input.redirect_to_stdout:
                output_stream.close()
            if parsed_input.redirect_to_stderr:
                err_stream.close()
def main():
    shell = Shell()
    parser = InputParser()
    while True:
        sys.stdout.write("$ ")
        # TODO: implement autocomplete
        try:
            input_line = input()
            parsed_input = parser.parse(input_line)
            shell.execute_parsed_input(parsed_input)
        except EOFError:
            break
if __name__ == "__main__":
    main()