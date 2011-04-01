# This file contains base-classes used in the implementation of other plugins in this repo.
# Author: yaniv.aknin@audish.com

import sys
assert sys.version_info[0] == 2 and sys.version_info[1] >= 6 or sys.version_info[0] > 2, 'needs Python >= v2.6'

import os
from datetime import timedelta, datetime
import json

class REQUIRED: pass

class BaseConfigurationUser(object):
    confValues = (
    )
    def __init__(self, agentConfig, checksLogger, rawConfig):
        self.agentConfig = agentConfig
        self.checksLogger = checksLogger
        self.rawConfig = rawConfig
        self.parseConfiguration()

    def parseConfiguration(self):
        self.fullyConfigured = True
        for configurationName, internalName, default in self.confValues:
            value = self.rawConfig['Main'].get(configurationName, default)
            if value is REQUIRED:
                self.checksLogger.debug('missing configuration setting %s; plugin %s will not run',
                                        configurationName, self.__class__.__name__)
                self.fullyConfigured = False
                return
            setattr(self, internalName, value)
        self.checksLogger.debug('%s plugin configured', self.__class__.__name__)

class BaseJSONMonitor(BaseConfigurationUser):
    confValues = (
        ('json_filename', 'filename', REQUIRED), # you would presumably like to override this in your subclass
    )
    defaultValues = (
        # add (string, scalar) tuples here; they will be dictified and sent in lieu of missing/erroneous values
    )
    maximumAge = timedelta(hours=2)
    def run(self):
        result = dict(self.defaultValues)
        try:
            if datetime.now() - datetime.fromtimestamp(os.stat(self.filename).st_mtime) > self.maximumAge:
                self.checksLogger.warning(
                    '%s plugin returning default values because %s is stale',
                    self.__class__.__name__,
                    self.filename
                )
            else:
                with open(self.filename) as handle:
                    result.update(json.load(handle))
        except Exception, error:
            self.checksLogger.error(
                '%s plugin caught %s:%s when loading %s',
                self.__class__.__name__,
                error.__class__.__name__,
                error,
                self.filename,
            )
        return result
