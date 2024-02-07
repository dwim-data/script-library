from lib.init import init
init()

import os
from lib.commander import SystemCommander

init()
commander = SystemCommander()

from lib.logger import script_logger
logger = script_logger
