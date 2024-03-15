from repo_utils.logger import internal_logger
import os
import sys
import subprocess

lib_base = os.path.dirname(os.path.abspath(__file__))


def ensure_pip_installations(colorama=True, ruamel_yaml=True, pymongo=False, slugify=False, beautiful_soup=False, inquirer=False):
    try:
        if(colorama):
            import colorama
        import requests
        import nacl.utils
        if(inquirer):
            import inquirer
        if(ruamel_yaml):
            from ruamel.yaml import YAML    
        if(pymongo):
            import pymongo  
        if(slugify):
            from slugify import slugify
        if(beautiful_soup):
            import html5lib
            from bs4 import BeautifulSoup
        internal_logger.debug('Found all import packages...')
    except Exception as e:
        requirements_path = os.path.join(lib_base, 'requirements.txt')

        # implement pip as a subprocess:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '-r', requirements_path])
        print('Successfully ran pip installation.')
