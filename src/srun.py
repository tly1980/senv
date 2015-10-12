#!/usr/bin/env python
import subprocess
import sys
import logging
import csv
import os

logging.basicConfig()
logger = logging.getLogger("srun")

def sh_call(cmd, shell=True, verbose=True, rd_stderr=False):
    try:
        logger.info("sh_call: %s" % cmd)
        if not rd_stderr:
            txt = subprocess.check_output(cmd, shell=shell)
        else:
            txt = subprocess.check_output(cmd,
                shell=shell, stderr=subprocess.STDOUT)
        if verbose and txt:
            print >> sys.stderr, txt
        return txt, 0
    except subprocess.CalledProcessError, e:
        logger.error("failed@ : %s" % cmd, exc_info=True)
        return None, e.returncode

cmd_wrapper = subprocess.call

def load_from_keychain_mac(item_name, verbose=False):
    txt, code = sh_call(
        "security find-generic-password -ga %s" % item_name, verbose=verbose, rd_stderr=True)
    if txt:
        for i in txt.splitlines():
            if i.startswith("password: "):
                return i.split(" ")[-1].strip('"\n')

def to_env(new_envs):
    for k, v in new_envs.items():
        os.environ[k] = v

def load_variables(txt):
    def xtract(user_pass_pair):
        idx = user_pass_pair.find('=')
        return user_pass_pair[:idx], user_pass_pair[idx+1:]

    ret = {}
    for line in csv.reader([txt]):
        d = dict([xtract(s) for s in line])
        ret.update(d)
    return ret

def main():
    item_name = sys.argv[1]
    cmd = ' '.join(sys.argv[2:])
    secret_txt = load_from_keychain_mac(item_name)
    d = load_variables(secret_txt)
    to_env(d)
    sys.exit(cmd_wrapper(cmd, shell=True))

if __name__ == '__main__':
    main()
