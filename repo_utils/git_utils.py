import argparse
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
        files = [ file.strip().replace('M ','').strip() for file in files if len(file.strip()) > 0 ]
        return files
    
class GitInfo:
    def __init__(self, branch : str, commit_date : str, commit_hash : str, commit_hash_short):
        self.branch = branch
        self.commit_date = commit_date
        self.commit_hash = commit_hash
        self.commit_hash_short = commit_hash_short

    def __str__(self):
     return f'branch=[{self.branch}], commit_date=[{self.commit_date}], commit_hash_short=[{self.commit_hash_short}], commit_hash=[{self.commit_hash}]'

class GitInfoArgs:
    def add_git_args(parser : argparse.ArgumentParser):
        parser.add_argument('--git-branch', default=None, help="The git branch to use, if not, will pull from the git repo")
        parser.add_argument('--git-commit-date', default=None, help="The git commit date to use, if not, will pull from the git repo")
        parser.add_argument('--git-commit-hash', default=None, help="The git commit hash to use, if not, will pull from the git repo")
        parser.add_argument('--git-commit-hash-short', default=None, help="The git commit short hash to use, if not, will pull from the git repo")

    def get_git_info(args: argparse.Namespace, git: GitUtils) -> GitInfo:
        return GitInfo(
           branch=args.git_branch if args.git_branch != None else git.get_branch(),
           commit_date=args.git_commit_date if args.git_commit_date != None else git.get_commit_date(),
           commit_hash=args.git_commit_hash if args.git_commit_hash != None else git.get_commit_hash(),
           commit_hash_short=args.git_commit_hash_short if args.git_commit_hash_short != None else git.get_commit_hash_short(),
        )