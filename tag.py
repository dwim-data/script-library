#!/usr/bin/env python3
from pathlib import Path
import os
from repo_utils.shared import commander, logger
from repo_utils.git_utils import GitVersionUtils
from semver import Version
import argparse

repo_dir = Path(os.path.dirname(os.path.abspath(__file__)))
git_version_utils = GitVersionUtils(repo_dir)
version_file = os.path.join(repo_dir.absolute(),'VERSION')

parser = argparse.ArgumentParser(description='Build mobile application')
parser.add_argument('--major', required=False, action='store_true', help="Increment the major version number")
parser.add_argument('--minor', required=False, action='store_true', help="Increment the minor version number")
parser.add_argument('--patch', required=False, action='store_true', help="Increment the patch version number")


def is_tagging_requested():
    return args.major or args.minor or args.patch


def update_release_version(dir:Path, latest_tag: Version):
  with open(os.path.join(dir.absolute(),'VERSION'), 'r+') as file:
    file.seek(0)
    file.write(str(latest_tag))
    file.truncate()

def add_version_tag_and_push(dir:Path, latest_tag: Version):
  commander.exec_system_command(f'git add {version_file}', dir.absolute())
  commander.exec_system_command(f'git commit -m "Updated version to {latest_tag}"', dir.absolute())
  commander.exec_system_command(f'git tag -a "{latest_tag}" -m "Release {latest_tag}"', dir.absolute())
  commander.exec_system_command('git push', dir.absolute())
  commander.exec_system_command('git push --tags', dir.absolute())


if __name__ == "__main__":
  try:
    args = parser.parse_args()
    if(not is_tagging_requested()):
       parser.print_help()
       parser.print_usage()
       exit(1)

    git_version_utils.git.ensure_git_uptodate(excluded_patterns=[
        r"tag.py"
    ])
    current_tag = git_version_utils.get_latest_version()
    logger.info(f'Current version is {current_tag}')

    updated_tag = git_version_utils.increment_version_tags(current_tag, args.major, args.minor, args.patch, False)
    logger.info(f'Setting updated version to {updated_tag}')
    update_release_version(dir=repo_dir, latest_tag=updated_tag)
    add_version_tag_and_push(dir=repo_dir, latest_tag=updated_tag)

    version_name = f'{updated_tag.major}.{updated_tag.minor}.{updated_tag.patch}'
    logger.info(f'Updated version to [{version_name}]')

  except Exception as ex:
      logger.error(f'Failed: {ex}')
      raise ex
      exit(1)