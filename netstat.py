#! /usr/bin/env python
# This is a Server Density netstat plugin
# Author: yaniv.aknin@audish.com

import platform
assert platform.system() == 'Linux', 'I ought to run in Linux'

import os
from subprocess import Popen, PIPE

class netstat(object):
    def __init__(self, agentConfig, checksLogger, rawConfig):
        self.agentConfig = agentConfig
        self.checksLogger = checksLogger
        self.rawConfig = rawConfig

    def run(self):
        result = {}
        process = Popen('netstat -tn', shell=True, stdout=PIPE, preexec_fn=lambda: os.close(0))
        stdout, dummy_stderr = process.communicate()
        for line in stdout.splitlines()[2:]: # first two lines in linux netstat are headers
            proto, recvq, sendq, local, remote, state = line.split()
            if state not in result:
                result[state] = 0
            result[state] += 1
        return result


if __name__ == '__main__':
    import logging
    logging.basicConfig()
    plugin = netstat(None, logging, dict(Main=dict()))
    print(plugin.run())
