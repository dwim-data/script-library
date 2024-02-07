from repo_utils.init import init
init()

import os
from repo_utils.commander import SystemCommander

init()
commander = SystemCommander()

from repo_utils.logger import script_logger
logger = script_logger
