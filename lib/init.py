from lib.ensure_pip_installations import ensure_pip_installations


def init(colorama=True, ruamel_yaml=False, pymongo=False):
    ensure_pip_installations(colorama, ruamel_yaml, pymongo)

    if(colorama):
        from colorama import init
        init()
