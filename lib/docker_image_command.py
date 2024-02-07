import logging
import os
from lib.shared import commander
from lib.repo_folders import repo_dir

class DockerImageCommand:
    def __init__(self, 
                 image : str 
                 ):
        self.image = image
        
    def ensure_image_exist(self):
        result = commander.exec_system_binary(f'docker',args=['images', '-q', self.image])
        if(result == ''):
            result = commander.exec_system_binary(f'docker',args=['pull', self.image])
            
    # TODO -- have this execute the docker command directly instead of through a wrapper shell script
    def run_command(self, command: str, env={}, streamed: bool = False, directory = None, log_level: int = logging.DEBUG):
        self.ensure_image_exist()
        if(directory == None):
            directory = repo_dir.absolute()

        binary = command.split(' ')[0]
        args = command.split(' ')[1:]
        return commander.exec_system_binary(binary, args=args, streamed = streamed, directory = directory, env=env, log_level = log_level)
