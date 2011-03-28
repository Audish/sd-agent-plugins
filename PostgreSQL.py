#! /usr/bin/env python
# This is a Server Density PostgreSQL plugin, loosely based on Server Density's own MySQL plugin
# Author: yaniv.aknin@audish.com,

import sys
assert sys.version_info[0] == 2 and sys.version_info[1] >= 6 or sys.version_info[0] > 2, 'needs Python >= v2.6'

from datetime import datetime, timedelta
from contextlib import closing
from collections import namedtuple

import psycopg2

SLOW_QUERY_DELTA = timedelta(minutes=5)

PostgreSQLStatActivity = namedtuple('PostgreSQLStatActivity', 'db_oid, name, pid, user_oid, user_name, current_query, query_wait_status, transaction_start_time, query_start_time, process_start_time, client_address, client_port')
'select * from pg_stat_activity;'

class REQUIRED: pass

class PostgreSQL(object):
    confValues = (
        ('postgresql_server', 'database', REQUIRED),
        ('postgresql_user', 'user', REQUIRED),
        ('postgresql_password', 'password', REQUIRED),
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

    def makeConnectionKwargs(self):
        return dict((attribute, getattr(self, attribute))
                    for attribute in ('database', 'user', 'password')
                    if getattr(self, attribute) is not None)

    def run(self):
        result = {}
        with closing(psycopg2.connect(**self.makeConnectionKwargs())) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute('select * from pg_stat_activity;')
                pgStatus = [PostgreSQLStatActivity(*element) for element in cursor.fetchall()]
                result['connections'] = len(pgStatus)
                result['slowQueries'] = len(tuple(self.yieldSlowQueries(pgStatus)))
        return result

    def yieldSlowQueries(self, pgStatus):
        for connection in pgStatus:
            if connection.current_query == '<IDLE>':
                continue
            execution_time = datetime.now(connection.query_start_time.tzinfo) - connection.query_start_time
            if execution_time > SLOW_QUERY_DELTA:
                yield connection
                self.checksLogger.warning('%s processes slow query %r for %ds', connection.name,
                                          connection.current_query, execution_time.seconds)

if __name__ == '__main__':
    try:
        import argparse
    except ImportError:
        print('you could run this script to test it, if you had argparse installed')
        sys.exit(1)

    import logging

    parser = argparse.ArgumentParser()
    parser.add_argument('server')
    parser.add_argument('user')
    parser.add_argument('password')
    options = parser.parse_args(sys.argv[1:])

    logging.basicConfig()

    plugin = PostgreSQL(
        None,
        logging,
        dict(Main=dict(('postgresql_%s' % (argument,), getattr(options, argument))
                       for argument in ('server', 'user', 'password')))
    )
    print(plugin.run())
