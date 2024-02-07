
from colorama import Fore, Style
from lib.logger import script_logger

def as_color(color, msg):
    return f'{color}{msg}{Fore.RESET}'

def print_user_message(msg):
    script_logger.info(as_color(Fore.YELLOW,msg))

def prompt_for_yes_no(msg):
    script_logger.debug(f'Printing yes_no user message [{msg}]')
    print(as_color(Fore.YELLOW,msg))
    try:
        response = input("[Y]/n : ")
        return response.strip().lower() == "y" or response.strip().lower() == ""
    except KeyboardInterrupt as ki:
        print('\r')
        return

def prompt_for_confirmations(msg):
    script_logger.debug(f'Printing confirmation message [{msg}]')
    print(as_color(Fore.YELLOW,msg))
    try:
        input("Press <any key> to continue...")
    except KeyboardInterrupt as ki:
        print('\r')
        return