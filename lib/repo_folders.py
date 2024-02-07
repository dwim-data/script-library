
import glob
import os
from pathlib import Path
import tempfile
from lib.shared import logger

repo_dir = Path(os.path.dirname(os.path.realpath(__file__))).parent.parent
temp_dir = Path(os.path.join(repo_dir.absolute(), 'temp'))
environment_dir = Path(os.path.join(repo_dir.absolute(), 'environments'))

def get_release_env_file(env: str, throw_on_not_found : bool = True):
    path = os.path.join(environment_dir.absolute(), f'default.{env}.yaml')
    if(not os.path.exists(path) and throw_on_not_found):
        raise RuntimeError(f'Release environment file not found [{path}]')
    return Path(path)

def get_folder_size(path : str):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return ByteSize(total_size)

def remove_temp_folders_by_glob(pattern : str, name : str):
    folder_size = 0
    folders = glob.glob(f'{tempfile.gettempdir()}/{pattern}', recursive=False)
    if(len(folders ) > 0):
        for folder in folders:
            folder_size += get_folder_size(folder)
            remove_dir(folder)
        logger.info(f'Removed {folder_size} of {name} temp folders in {tempfile.gettempdir()}')
    else:
        logger.info(f'No {name} temp folders found in {tempfile.gettempdir()}')

def print_temp_folders_by_glob(pattern : str):
    folder_size = 0
    folders = glob.glob(f'{tempfile.gettempdir()}/{pattern}', recursive=False)
    for folder in folders:
        folder_size += get_folder_size(folder)
    logger.info(f'Found {len(folders)} folders in {tempfile.gettempdir()} that matched {pattern} with a total size of {folder_size}')


def remove_dir(directory):
    directory = Path(directory)
    for item in directory.iterdir():
        if item.is_dir():
            remove_dir(item)
        else:
            item.unlink()
    directory.rmdir()

class ByteSize(int):

    _KB = 1024
    _suffixes = 'B', 'KB', 'MB', 'GB', 'PB'

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.bytes = self.B = int(self)
        self.kilobytes = self.KB = self / self._KB**1
        self.megabytes = self.MB = self / self._KB**2
        self.gigabytes = self.GB = self / self._KB**3
        self.petabytes = self.PB = self / self._KB**4
        *suffixes, last = self._suffixes
        suffix = next((
            suffix
            for suffix in suffixes
            if 1 < getattr(self, suffix) < self._KB
        ), last)
        self.readable = suffix, getattr(self, suffix)

        super().__init__()

    def __str__(self):
        return self.__format__('.2f')

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, super().__repr__())

    def __format__(self, format_spec):
        suffix, val = self.readable
        return '{val:{fmt}} {suf}'.format(val=val, fmt=format_spec, suf=suffix)

    def __sub__(self, other):
        return self.__class__(super().__sub__(other))

    def __add__(self, other):
        return self.__class__(super().__add__(other))
    
    def __mul__(self, other):
        return self.__class__(super().__mul__(other))

    def __rsub__(self, other):
        return self.__class__(super().__sub__(other))

    def __radd__(self, other):
        return self.__class__(super().__add__(other))
    
    def __rmul__(self, other):
        return self.__class__(super().__rmul__(other)) 