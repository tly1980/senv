#!/usr/bin/env python
import subprocess
import sys
import logging
import csv
import os
import argparse
import StringIO

AP = argparse.ArgumentParser("srun", description="load environment variables from keychain and execute your command.")

AP_run = argparse.ArgumentParser("run", description="load environment variables from keychain and execute your command.")
AP_run.add_argument("account")
AP_run.add_argument("cmd", nargs="+")


AP_add = argparse.ArgumentParser("add",
    description="add or update environment variables to keychain.")
AP_add.add_argument("account")
AP_add.add_argument("variables", nargs="+")
AP_add.add_argument("--service", type=str, default=None)
AP_add.add_argument("--dry", action="store_true")

AP_del = argparse.ArgumentParser("del",
    description="del environment variables from keychain.")
AP_del.add_argument("account")
AP_del.add_argument("variables", nargs="+")

AP_show = argparse.ArgumentParser("show",
    description="show environment variables from keychain.")
AP_show.add_argument("account")
AP_show.add_argument("--unmask", default=False, action='store_true')


logging.basicConfig()
logger = logging.getLogger("srun")

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

def run(args):
    account = args.account
    secret_txt = load_from_keychain_mac(account)
    d = load_variables(secret_txt)
    to_env(d)
    sys.exit(cmd_wrapper(args.cmd))

def mask(s, start=2, end=2):
    if len(s) > 8:
        return s[:2] + '*' * (len(s) - start - end) + s[-2:]
    else:
        return '*' * 8

def show_variables(d, safe=True, **kwargs):
    for k, v in kwargs.items():
        print "%s: %s" % (k, v)
    print "===================="

    for k in sorted(d.keys()):
        v = d[k]
        if safe:
            print "%s=%s" % (k, mask(v))
        else:
            print "%s=%s" % (k, v)

def add(args):
    account = args.account
    secret_txt = load_from_keychain_mac(account)
    d = load_variables(secret_txt)

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

def show(args):
    account = args.account
    secret_txt = load_from_keychain_mac(account)
    d = load_variables(secret_txt)

    show_variables(d, safe=not(args.unmask))


def main():
    action = sys.argv[1]
    argv = sys.argv[2:]
    if action == 'run':
        run(
            AP_run.parse_args(argv))
    elif action == 'add':
        add(
            AP_add.parse_args(argv))
    elif action == 'show':
        show(
            AP_show.parse_args(argv))

if __name__ == '__main__':
    main()
