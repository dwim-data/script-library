from repo_utils.ensure_pip_installations import ensure_pip_installations


def init(colorama=True, ruamel_yaml=False, pymongo=False, slugify=False, beautiful_soup=False, inquirer=False):
    ensure_pip_installations(colorama=colorama, ruamel_yaml=ruamel_yaml, pymongo=pymongo, slugify=slugify, beautiful_soup=beautiful_soup, inquirer=inquirer)

    if(colorama):
        from colorama import init
        init()
