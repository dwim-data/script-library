import glob
import logging
import os
from pathlib import Path
from lib.docker_image_command import DockerImageCommand
from lib.shared import logger
from lib.repo_folders import print_temp_folders_by_glob, remove_temp_folders_by_glob, repo_dir
import tempfile

class Helmfile:
    def __init__(self, 
                 enable_secrets : bool = False,
                 version : str = '0.148.1',
                 ):
        self.enable_secrets = enable_secrets
        self.commander = DockerImageCommand(f'ghcr.io/helmfile/helmfile:v{version}')

    def run_command(self, command: str, streamed: bool = True, log_level: int = logging.INFO):
        binary = os.path.join(repo_dir.absolute(), 'bin', 'helmfile')
        command = f'{binary} {command}'
        env = {
            "HELMFILE_IMAGE": f'{self.commander.image}'
        }
        if(self.enable_secrets):
            env["ENABLE_COMMON_SECRETS"] = "true"
        return self.commander.run_command(command, directory = repo_dir.absolute(), streamed=streamed, env=env, log_level= log_level)

    def clean(self):
        print_temp_folders_by_glob('flutter_tools*')
        # remove_temp_folders_by_glob('helmfile*', 'helmfile')
        # remove_temp_folders_by_glob('chartify*', 'chartify')

    def generate_values(self, env: str, release: str):
        command = f'-e {env} --selector release={release} write-values --output-file-template /dev/stdout --skip-deps'
        return self.run_command(command)

    def update_dependencies(self, environment: str, log_level: int = logging.INFO, force : bool = False):
        helm_repo_path = os.path.join(repo_dir.absolute(), 'bin', 'helm', 'cache', 'repository')
        if(not os.path.exists(helm_repo_path) or force):
            logger.debug(f'Updating dependencies as helm-cache at {helm_repo_path} not present')
            self.run_command(f'-e {environment} deps', streamed = True, log_level= log_level)
        else:
            logger.debug(f'Not updating dependencies as helm-cache already present')
