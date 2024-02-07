import logging
import os
import platform
import re
import selectors
import signal
import subprocess
import sys
from lib.logger import script_logger
from colorama import Fore, Style


class SystemCommander:

    def is_windows(self):
        return platform.system() == 'Windows'

    def is_mac(self):
        return platform.system() == 'Darwin'

    def is_linux(self):
        return platform.system() == 'Linux'

    def system_has_command(self, exec):
        try:
            cmd = ('powershell Get-Command -Name ' + exec) if self.is_windows() else ('command -v ' + exec)
            self.exec_system_command(cmd)
            return True
        except Exception:
            return False

    def sanitize_output(self, stdout, decode = True):
        output = stdout.decode('utf8') if decode else stdout
        return output.replace('\\r', '').replace('\\n', '\n').strip()

    def strip_lines_to_str(self, lines):
        lines = [ re.sub('\n$', '', line) for line in lines ]
        return '\n'.join(lines)

    def get_command_environment(self, env = {}):
        my_env = os.environ.copy()
        try:
            if(env is not None):
                for key in env.keys():
                    my_env[key] = env[key]
        except:
            script_logger.debug(f'Failed to get environment from {env}')
            my_env = os.environ.copy()
        return my_env

    def exec_system_command(self, cmd, directory : str = None, env = {}, log_level = logging.DEBUG, privledged = False):
        # Remove double spaces
        cmd = re.sub(' +', ' ', cmd)
        if directory:
            cmd_display = f'cd {directory} && {cmd}'
        cmd_display = Fore.CYAN + cmd + Fore.RESET

        if privledged and not self.is_windows():
            cmd = f'sudo {cmd}'

        sep = Fore.YELLOW + \
            '\n------------------------------------------------------------------------' + Fore.RESET

        try:
            if directory is None or directory == '':
                directory = os.getcwd()

            script_logger.info(f'Executing command [' + cmd_display + ']')
            result = subprocess.run(
                cmd, shell=True, cwd=directory, env=self.get_command_environment(env=env), check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                script_logger.info(result)
                raise RuntimeError(self.sanitize_output(result.stdout) + '\n\n' + self.sanitize_output(result.stderr))

            output = self.sanitize_output(result.stdout)
            log_msg = f'Command [{cmd_display}] completed successfully'
            if output != '':
                log_msg = f'{log_msg}:' + sep + '\n' + Fore.YELLOW + \
                    Fore.LIGHTBLACK_EX + output + Style.RESET_ALL + sep
            else:
                log_msg = log_msg + '.'
            script_logger.log(log_level, log_msg)

            return output
        except Exception as err:
            sep = '\n------------------------------------------------------------------------'
            raise RuntimeError(
                "Failed to execute command [{1}] returned: {0}\n{2}{0}"
                .format(sep, cmd_display, err)) from err

    def exec_system_command_streamed(self, cmd, directory : str = None, env = {}, log_level = logging.DEBUG, privledged = False):
        # Remove double spaces
        cmd = re.sub(' +', ' ', cmd)
        if privledged and not self.is_windows():
            cmd = f'sudo {cmd}'

        cmd_display_raw = cmd
        if directory:
            cmd_display_raw = f'cd {directory} && ' + cmd

        cmd_display = Fore.CYAN + cmd_display_raw + Fore.RESET

        sep = Fore.YELLOW + \
            '\n------------------------------------------------------------------------' + Fore.RESET

        try:
            if directory is None:
                directory = os.getcwd()

            script_logger.log(log_level, f'Executing command [' + cmd_display + ']')

            print(Fore.LIGHTBLACK_EX)
            subprocess.check_call(
                cmd, shell=True, env=self.get_command_environment(env=env), cwd=directory)
            print(Style.RESET_ALL)
        except Exception as err:
            print(Style.RESET_ALL)
            sep = '\n------------------------------------------------------------------------'
            raise RuntimeError(
                "Failed to execute command [{1}] returned: {0}\n{2}{0}".format(sep, cmd_display_raw, err)) from err
        
    
    def exec_system_binary(self, binary : str, args = [], directory : str = None, env = {}, streamed = False, log_level = logging.DEBUG, privledged = False):
        # Remove double spaces
        cmd = re.sub(' +', ' ', " ".join(args))
        cmd = f'{binary} {cmd}'
        if privledged and not self.is_windows():
            cmd = f'sudo {cmd}'

        cmd_display_raw = cmd
        if directory:
            cmd_display_raw = f'cd {directory} && {cmd}'

        cmd_display = Fore.CYAN + cmd_display_raw + Fore.RESET

        sep = Fore.YELLOW + \
            '\n------------------------------------------------------------------------' + Fore.RESET

        try:
            if directory is None:
                directory = os.getcwd()

            script_logger.log(log_level, f'Executing command [' + cmd_display + ']')

            print(Fore.LIGHTBLACK_EX)
            args.insert(0, binary)

            output = None

            with subprocess.Popen(args, env=self.get_command_environment(env=env), cwd=directory, stdout=subprocess.PIPE, stderr=sys.stderr, universal_newlines=True) as process:
                
                output_lines = []

                # Poll process for new output until finished
                while True:
                    try:
                        nextline = process.stdout.readline()
                        if nextline == '' and process.poll() is not None:
                            break
                        output_lines.append(nextline)
                        if(streamed):
                            # Redirect sub-process stream to stderr...
                            sys.stderr.write(nextline)
                            sys.stderr.flush()
                    except KeyboardInterrupt as ke:
                        try:
                            print(f'Sending SIGKILL to {process.pid}')
                            process.kill()
                        except OSError:
                            print(f'Failed to terminate process {process.pid}')
                            pass

                if process.returncode != 0:
                    raise RuntimeError(self.strip_lines_to_str(output_lines) + '\n\n')
                
                output = self.strip_lines_to_str(output_lines)

            print(Style.RESET_ALL)

            log_msg = f'Command [{cmd_display}] completed successfully'
            if(not streamed):
                if output != '':
                    log_msg = f'{log_msg}:' + sep + '\n' + Fore.YELLOW + \
                        Fore.LIGHTBLACK_EX + output + Style.RESET_ALL + sep
                else:
                    log_msg = log_msg + '.'
            script_logger.log(log_level, log_msg)

            return output
        except Exception as err:
            print(Style.RESET_ALL)
            sep = '\n------------------------------------------------------------------------'
            raise RuntimeError(
                "Failed to execute command [{1}] returned: {0}\n{2}{0}".format(sep, cmd_display_raw, err)) from err
