from repo_utils.ensure_pip_installations import ensure_pip_installations


def init(colorama=True, ruamel_yaml=False, pymongo=False, slugify=False, beautiful_soup=False):
    ensure_pip_installations(colorama, ruamel_yaml, pymongo, slugify, beautiful_soup)

    if(colorama):
        from colorama import init
        init()
