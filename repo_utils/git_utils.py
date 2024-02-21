import logging
from repo_utils.shared import commander
from repo_utils.repo_folders import repo_dir

class GitUtils:
    def get_branch(self, folder : str = repo_dir.absolute(), log_level: int = logging.DEBUG):
        return commander.exec_system_command('git branch --show-current', folder, log_level=log_level)

    def get_commit_date(self, folder : str = repo_dir.absolute(), log_level: int = logging.DEBUG):
        return commander.exec_system_command('git --no-pager log -1 --format=\"%ai\"', folder, log_level=log_level)

    def get_commit_hash(self, folder : str = repo_dir.absolute(), log_level: int = logging.DEBUG):
        return commander.exec_system_command('git rev-parse HEAD', folder, log_level=log_level)

    def get_commit_hash_short(self, folder : str = repo_dir.absolute(), log_level: int = logging.DEBUG):
        return commander.exec_system_command('git rev-parse --short HEAD', folder, log_level=log_level)

    def get_commit_message(self, folder : str = repo_dir.absolute(), log_level: int = logging.DEBUG):
        return commander.exec_system_command('git log -1 --pretty=%s', folder, log_level=log_level)
    
    def get_uncommitted_files(self, folder : str = repo_dir.absolute(), log_level: int = logging.INFO):
        files = commander.exec_system_command('git status --porcelain', folder, log_level=log_level).strip().split('\n')
        files = [ file.strip().replace('M ','').strip() for file in files ]
        return files