#!/usr/bin/env python
'''
The MIT License (MIT)

Copyright (c) [2015] [Tom Tang]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import subprocess
import sys
import logging
import csv
import os
import argparse
import StringIO
import getpass

AP = argparse.ArgumentParser("senv", description="load environment variables from keychain and execute your command.")

AP_run = argparse.ArgumentParser("run", description="load environment variables from keychain and execute your command.")
AP_run.add_argument("account")
AP_run.add_argument("cmd", nargs="+")


AP_add = argparse.ArgumentParser("add",
    description="add or update environment variables to keychain.")
AP_add.add_argument("account")
AP_add.add_argument("variables", nargs="*", default=[])
AP_add.add_argument("--service", type=str, default=None)
AP_add.add_argument("--dry", action="store_true", default=False)
AP_add.add_argument("-i", "--interative", action="store_true", default=False)

AP_del = argparse.ArgumentParser("del",
    description="del environment variables from keychain.")
AP_del.add_argument("account")
AP_del.add_argument("variables", nargs="+")
AP_del.add_argument("--dry", action="store_true", default=False)

AP_show = argparse.ArgumentParser("show",
    description="show environment variables from keychain.")
AP_show.add_argument("account")
AP_show.add_argument("--unmask", default=False, action='store_true')


logging.basicConfig()
logger = logging.getLogger("senv")

cmd_wrapper = subprocess.call

def load_from_keychain_mac(account, verbose=False):
    cmd = ["security", "find-generic-password", "-ga", account]
    txt = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    if txt:
        for i in txt.splitlines():
            if i.startswith("password: "):
                return i.split(" ")[-1].strip('"\n')

def persist_to_keychain_mac(account, d, service_name=None):
    name = account
    if not service_name:
        service_name = account
    cmd = ["security", 
    "add-generic-password", 
    "-a", account,
    "-s", service_name,
    "-w", dump_variables(d),
    "-T","","-U"]

    return subprocess.call(cmd)


def to_env(new_envs):
    for k, v in new_envs.items():
        os.environ[k] = v

def xtract(user_pass_pair):
    idx = user_pass_pair.find('=')
    return user_pass_pair[:idx], user_pass_pair[idx+1:]

def load_variables(txt):
    ret = {}
    for line in csv.reader([txt]):
        d = dict([xtract(s) for s in line])
        ret.update(d)
    return ret

def dump_variables(d):
    lst = []
    for k in sorted(d.keys()):
        v = d[k]
        lst.append('='.join([k, v]))

    sio = StringIO.StringIO()
    csvf = csv.writer(sio)
    csvf.writerow(lst)
    return sio.getvalue().strip()

def run(argv):
    account = argv[0]
    cmds = argv[1:]
    secret_txt = load_from_keychain_mac(account)
    d = load_variables(secret_txt)
    to_env(d)
    sys.exit(cmd_wrapper(cmds))

def mask(s, start=2, end=2):
    if len(s) > 8:
        return s[:2] + '*' * (len(s) - start - end) + s[-2:]
    else:
        return '*' * 8

def show_variables(d, safe=True, **kwargs):
    for k, v in kwargs.items():
        print "[%s]: %s" % (k, v)
    print "===================="

    for k in sorted(d.keys()):
        v = d[k]
        if safe:
            print "%s=%s" % (k, mask(v))
        else:
            print "%s=%s" % (k, v)

def get_from_interactive():
    user = raw_input("variable: ")
    passwd = getpass.getpass("value: ")
    return '%s=%s' % (user, passwd)

def add(argv):
    args = AP_add.parse_args(argv)

    account = args.account
    variables = args.variables

    try:
        secret_txt = load_from_keychain_mac(account)
        d = load_variables(secret_txt)
    except:
        d = {}

    if len(variables) == 0 and not args.interative:
        sys.exit("Non interative mode require at least on variable=value", -1)

    if args.interative:
        variables.append(get_from_interactive())


    for k in args.variables:
        if '=' in k:
            name, value = xtract(k)
            d[name] = value
        else:
            print >> sys.stderr,\
                "[%s] is not following format name=value format" % k
    if args.dry:
        show_variables(d, account=account, service_name=args.service)
    else:
        persist_to_keychain_mac(
            account, d,
            service_name=args.service)


def delete(argv):
    args = AP_del.parse_args(argv)
    account = args.account
    secret_txt = load_from_keychain_mac(account)
    d = load_variables(secret_txt)

    for k in args.variables:
        del d[k]

    if args.dry:
        show_variables(d, account=account, service_name=args.service)
    else:
        persist_to_keychain_mac(
            account, d,
            service_name=account)


def show(argv):
    args =  AP_show.parse_args(argv)
    account = args.account
    try:
        secret_txt = load_from_keychain_mac(account)
    except:
        logger.error("Failed to retrive account: %s from keychain." % account)
        sys.exit(-1)

    d = load_variables(secret_txt)
    show_variables(d, account=account, safe=not(args.unmask))


ACTIONS = {
    'run': run,
    'del': delete,
    'add': add,
    'show': show,
}


def main():
    action = sys.argv[1]
    argv = sys.argv[2:]

    action_fun = ACTIONS.get(action, None)

    if not action_fun:
        sys.exit(
            "'%s' is unspported, only %s is allowed" % (action, ACTIONS.keys()))
    action_fun(argv)




if __name__ == '__main__':
    main()
