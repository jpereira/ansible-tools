#!/usr/bin/python
# Author: Jorge Pereira <jpereiran@gmail.com>
# -*- coding: utf-8 -*-

__author__ = 'Jorge Pereira <jpereiran@gmail.com>'
__version__ = "0.1a"

import json
import sys
import argparse
import os, errno
import traceback
import shutil

from ansible.module_utils._text import to_native
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.inventory.host import Host
from ansible.inventory.group import Group
from ansible.parsing.yaml.objects import AnsibleBaseYAMLObject, AnsibleSequence, AnsibleMapping, AnsibleUnicode
from collections import defaultdict

tab_size = None
ignore_vars = [ "env", "group_names", "inventory_hostname", "inventory_hostname_short" ]

def ident_as_usual(tab, str):
    return (' ' * (tab_size * tab)) + str + ":\n"

def ident_as_the_key(tab, key, val):
    indent = ' ' * (tab_size * tab)
    lines = json.dumps(val, sort_keys=True, indent=tab_size, separators=(',', ': '))
    _val = '\n'.join(indent + line for line in lines.splitlines())
    return ("%s%s: %s\n") % (indent, key, _val.strip())

def filter_vars(k):
    if k in ignore_vars:
        return True
    return False

def _main():
    global tab_size

    parser = argparse.ArgumentParser(
        description = "Convert the Ansible inventory from INI to yML format",
    )
    parser.add_argument(
        "-i",
        dest = "inventory_file",
        help = "Inform the Ansible Vault Password",
        required = True
    )
    parser.add_argument(
        "-d",
        dest = "dest_inventory_path",
        help = "Destination to save the inventory files (Default will be on $PWD)",
        required = False
    )
    parser.add_argument(
        "-g",
        dest = "group",
        help = "Filter by specific GROUP",
    )
    parser.add_argument(
        "-p",
        dest = "vault_password",
        help = "Inform the Ansible Vault Password or file with password",
    )
    parser.add_argument(
        "-t",
        dest = "tab_size",
        type = int,
        help = "Number of tab spaces",
        default = 4,
    )

    args = parser.parse_args()
    tab_size = args.tab_size

    try:
        #  Ansible: initialize needed objects
        variable_manager = VariableManager()
        loader = DataLoader()

        if args.vault_password:
            if os.path.isfile(args.vault_password):
                with open(args.vault_password, "r") as f:
                    args.vault_password = f.readlines()[0].rstrip()
                    f.close()

            print("** Passing Vault Password: '%s'") % (args.vault_password)
            loader.set_vault_password(args.vault_password)

        #  Ansible: Load inventory
        inventory = Inventory(
            loader = loader,
            variable_manager = variable_manager,
            host_list = args.inventory_file,
        )
    except Exception as e:
        print ("** ERROR: Missing the '--vault-password'??\n %s\n") % str(e)
        sys.exit(-1)

    try:
        groups = {}

        if args.group:
            _group = inventory.get_group(args.group)
            if not _group:
                print("** ERROR: No such group '%s' in inventory file '%s', exiting.") % \
                    (args.group, args.inventory_file)
                sys.exit(-1)

            groups[args.group] = _group
        else:
            groups = inventory.get_groups()

        for group in groups:
            if group == "all":
                continue

            # start the file
            output = ""
            output += "###################################################################################################\n"
            output += ("# Converted from '%s[%s]'\n") % (args.inventory_file, group)
            output += "###################################################################################################\n"
            output += ("%s:\n") % group

            group_ref = inventory.get_group(group)

            # children or hosts?
            if group_ref.child_groups:
                output += ident_as_usual(1, "children")
                for group_name in sorted(group_ref.child_groups):
                    output += ident_as_usual(2, group_name.get_name())
            else:
                group_ips = group_ref.hosts
                if not group_ips:
                    continue
                output += ""
                output += ident_as_usual(1, "hosts")
                for group_ip in sorted(group_ips):
                    if filter_vars(group_ip):
                        continue
                    output += ident_as_usual(2, group_ip.get_name())
                    _ip_host_vars = inventory.get_host_vars(group_ip, return_results=True) # group_vars/$group
                    _ip_vars = inventory.get_vars(to_native(group_ip))                     # host key1=var1
                    group_ip_vars = dict(_ip_host_vars.items() + _ip_vars.items())
                    if not group_ip_vars:
                        continue
                    for k, v in group_ip_vars.items():
                        if filter_vars(k):
                            continue
                        output += ident_as_the_key(3, k, v)

            # group_vars/$service
            output += "\n"
            output += ident_as_usual(1, "vars")
            group_vars = inventory.get_group_vars(group_ref, return_results=True)
            if group_vars:
                for k, v in sorted(group_vars.items()):
                    if filter_vars(k):
                        continue
                    output += ident_as_the_key(2, k, v)
            output += "\n"
            output += ("# End for %s\n") % group

            if not args.dest_inventory_path:
                print(output)
            else:
                dest = args.dest_inventory_path + "/" + group + ".yml"
                print("Generating " + dest)

                try:
                    dest_dir = os.path.dirname(dest)
                    os.makedirs(dest_dir)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise

                f = file(dest, "w+")
                f.write(output)
                f.close()

        # Should save the 'group_vars/all' ?
        src = "group_vars/all"
        if args.dest_inventory_path and os.path.isfile(src):
            dest = args.dest_inventory_path + "/" + src
            print("Copying '%s' to '%s'") % (src, dest)
            try:
                dest_dir = os.path.dirname(dest)
                os.makedirs(dest_dir)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            shutil.copyfile(src, dest)

    except Exception as e:
        print ("** ERROR: %s\n") % str(e)
        traceback.print_exc()
    # end _main()

if __name__ == "__main__":
  _main()
