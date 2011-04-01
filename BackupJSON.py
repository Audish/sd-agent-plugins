#! /usr/bin/env python
# This is a Server Density plugin which reports what it founds in a JSON file created by a backup script.
# Author: yaniv.aknin@audish.com

import sys
assert sys.version_info[0] == 2 and sys.version_info[1] >= 6 or sys.version_info[0] > 2, 'needs Python >= v2.6'

from datetime import timedelta

from base import BaseJSONMonitor, REQUIRED

class BackupJSON(BaseJSONMonitor):
    confValues = (
        ('backup_json', 'filename', REQUIRED),
    )
    defaultValues = (
        ('mediaBackedUpFiles', 0),
        ('mediaBackedUpBytes', 0),
        ('databaseDumpDuration', 0),
        ('databaseDumpSize', 0),
        ('totalDuration', -1),
    )

if __name__ == '__main__':
    try:
        import argparse
    except ImportError:
        print('you could run this script to test it, if you had argparse installed')
        sys.exit(1)

    import logging

    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-a', '--alt-maximum-age', default=60*60*2, type=int) # 60*60*2 == 2 hours
    options = parser.parse_args(sys.argv[1:])

    logging.basicConfig()

    BackupJSON.maximumAge = timedelta(seconds=options.alt_maximum_age)

    plugin = BackupJSON(None, logging, dict(Main=dict(backup_json=options.filename)))
    print(plugin.run())
