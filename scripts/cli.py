#!/usr/bin/env python
from openstack_account.client import AccountSetup

import argparse
import logging
import os
import sys
import yaml

log_format = '%(asctime)s-%(levelname)s-%(message)s'
log = logging.getLogger('openstack_account')
log.setLevel(logging.INFO)
handle = logging.StreamHandler()
handle.setLevel(logging.INFO)
form = logging.Formatter(log_format)
handle.setFormatter(form)
log.addHandler(handle)

def parse_args():
    p = argparse.ArgumentParser(description='Create & Setup OpenStack Accounts')
    p.add_argument('--username', help='OpenStack Auth username')
    p.add_argument('--password', help='OpenStack Auth password')
    p.add_argument('--tenant-name', help='OpenStack Auth tenant name')
    p.add_argument('--auth-url', help='OpenStack Auth keystone url')
    p.add_argument('--debug', action='store_true', help='Show debug output')

    sub = p.add_subparsers(dest='command', help='Command')
    imp = sub.add_parser('import', help='Import config')
    imp.add_argument('config_file', help='Config file to import')
    exp = sub.add_parser('export', help='Export config')
    exp.add_argument('config_file', help='Export output file')
    return p.parse_args()

def get_env_args(args):
    # Check environment for variables if not set on command line
    args.username = args.username or os.getenv('OS_USERNAME')
    args.password = args.password or os.getenv('OS_PASSWORD')
    args.tenant_name = args.tenant_name or os.getenv('OS_TENANT_NAME')
    args.auth_url = args.auth_url or os.getenv('OS_AUTH_URL')
    must_have = ['username', 'password', 'tenant_name', 'auth_url']
    for item in must_have:
        if not getattr(args, item):
            log.error('Need arg:%s' % item)
            sys.exit('')
    return args

def main():
    log.debug('Reading CLI args')
    args = get_env_args(parse_args())
    if args.debug:
        log.setLevel(logging.DEBUG)
    log.debug('Initialzing Account Setup')
    a = AccountSetup(args.username,
                     args.password,
                     args.tenant_name,
                     args.auth_url,)
    if args.command == 'import':
        with open(args.config_file, 'r') as f:
            log.debug('Loading configs from:%s' % args.config_file)
            config_data = yaml.load(f)
            a.import_config(config_data)
    elif args.command == 'export':
        data = a.export_config()
        with open(args.config_file, 'w') as f:
            log.debug('Writing data to file:%s' % args.config_file)
            f.write(yaml.dump(data))