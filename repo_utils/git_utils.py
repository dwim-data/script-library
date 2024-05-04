import argparse
import logging
from pathlib import Path
import re
import inquirer
from semver import Version
from repo_utils.shared import commander, logger
from semver import Version

class GitUtils:
    def __init__(self, directory : Path):
        if(not directory):
            raise RuntimeError("GitUtils requires a directory to be specified")
        self.directory = directory
        
    def get_branch(self, log_level: int = logging.DEBUG):
        return commander.exec_system_command(cmd='git branch --show-current', directory=self.directory.absolute(), log_level=log_level)

    def get_commit_date(self, log_level: int = logging.DEBUG):
        return commander.exec_system_command(cmd='git --no-pager log -1 --format=\"%ai\"', directory=self.directory.absolute(), log_level=log_level)

    def get_commit_hash(self, log_level: int = logging.DEBUG):
        return commander.exec_system_command(cmd='git rev-parse HEAD', directory=self.directory.absolute(), log_level=log_level)

    def get_commit_hash_short(self, log_level: int = logging.DEBUG):
        return commander.exec_system_command(cmd='git rev-parse --short HEAD', directory=self.directory.absolute(), log_level=log_level)

    def get_commit_message(self, log_level: int = logging.DEBUG):
        return commander.exec_system_command(cmd='git log -1 --pretty=%s', directory=self.directory.absolute(), log_level=log_level)
    
    def get_uncommitted_files(self, log_level: int = logging.DEBUG):
        files = commander.exec_system_command(cmd='git status --porcelain', directory=self.directory.absolute(), log_level=log_level).strip().split('\n')
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
        

class VersionSorter:
    def __init__(self, obj: Version, *args):
        self.version = obj
    def __lt__(self, other):
        if(self.version.major != other.version.major):
            # print(f'{self.version.major} < {other.version.major}')
            return self.version.major < other.version.major
        elif(self.version.minor != other.version.minor):
            # print(f'{self.version.minor} < {other.version.minor}')
            return self.version.minor < other.version.minor
        elif(self.version.patch != other.version.patch):
            # print(f'{self.version.patch} < {other.version.patch}')
            return self.version.patch < other.version.patch
        elif(self.version.build == None or other.version.build == None):
            return True
        elif(self.version.build != other.version.build):
            # print(f'{self.version.build} < {other.version.build}')
            return self.version.build < other.version.build

class GitVersionUtils:
    def __init__(self, directory : Path):
        self.git = GitUtils(directory=directory)
        
    def _parseVersion(self, e: str):
        s=f'{e}'
        if(not '+build' in e and '-' in e):
            buildNumber=e.split('-')[1]
            s=e.replace(f'-{buildNumber}', f'+build.{buildNumber}')
        version = Version.parse(s)
        return version
    
    def get_latest_version(self, log_level=logging.INFO):
        tags = commander.exec_system_command('git tag', self.git.directory.absolute(), log_level).split('\n')
        tags = [ self._parseVersion(i) for i in tags ]
        tags.sort(key=VersionSorter, reverse=True)
        return tags[0] if len(tags) > 0 else None
    
    def ensure_git_uptodate(self, excluded_patterns = [], log_level=logging.DEBUG):
        raw_modified_files = self.git.get_uncommitted_files(log_level)
        modified_files = []
        
        for file in raw_modified_files:
            include = True
            for pattern in excluded_patterns:
                match = re.search(pattern, file, re.MULTILINE)
                if match:
                    logger.log(level=log_level, msg=f'Git change [{file}] ignored given pattern [{str(pattern)}]')
                    include = False
                else:
                    logger.log(level=log_level, msg=f'Git change [{file}] not ignored given pattern [{str(pattern)}]')
            
            if include:
                modified_files.append(file)  
        
        if(len(modified_files) > 0):
            results = '\n'.join(modified_files)
            raise Exception(f'Please commit all changes to git.  Found the following changes:\n{results}\n')

    def confirm_if_git_not_uptodate(self, log_level=logging.INFO):
        modified_files = self.git.get_uncommitted_files(log_level)
        modified_files = [ i for i in modified_files if not i.startswith("scripts/") and not i.startswith("submodules/")]
        if(len(modified_files) > 0):
            questions = [
                inquirer.List(
                    "Continue",
                    message="Are you sure you wish to build with uncommitted changes?",
                    choices=["yes", "no"],
                )
            ]
            answers = inquirer.prompt(questions)
            print(answers)
            if(answers['Continue'] == "no"):
                results = '\n'.join(modified_files)
            raise Exception(f'Please commit all changes to git.  Found the following changes:\n{results}\n')

    def increment_version_tags(self, latest_tag: Version, major: bool, minor: bool, patch: bool, build: bool, continuous_build: bool = False):
        """Increments the major, minor, patch tags within a given version.  This will also increment and append the build number so that it is universal."""
        new_tag=None
        if(latest_tag):
            new_tag : Version = latest_tag
            if(major or minor or patch or build):
                new_tag = new_tag.bump_build() if continuous_build else new_tag
            if(major):
                temp_tag = new_tag.bump_major()
                new_tag = Version(temp_tag.major, temp_tag.minor, temp_tag.patch, temp_tag.prerelease, new_tag.build)
            if(minor):
                temp_tag = new_tag.bump_minor()
                new_tag = Version(temp_tag.major, temp_tag.minor, temp_tag.patch, temp_tag.prerelease, new_tag.build)
            if(patch):
                temp_tag = new_tag.bump_patch()
                new_tag = Version(temp_tag.major, temp_tag.minor, temp_tag.patch, temp_tag.prerelease, new_tag.build)
        return new_tag