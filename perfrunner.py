import os
import re
import types
import copy
import inspect
import traceback
import random
import string
import time
from subprocess import call

from os.path import expanduser

class PerfRunner(object):
    def __int__(self):

        # parse args
        self._args = self._parse_cli_args()

        # get commands
        commands = self._get_commands()

        # prepare resource group, sub-resources,
        # for vm, vnet with one subnet
        print('preparation work.')
        if 'vm' in self._args['resources'] or self._args['resources'] == 'all':
            print('create vnet.')
            call("az network vnet  create -g {0} -n ansiblevnet --adress-prefix 10.0.0.0/16 --subnet-name ansiblesubnet --subnet-prefix 10.0.0.24".format(self._args['resource_group']))
            call("az network vnet  create -g {0} -n azclivnet --adress-prefix 10.0.0.0/16 --subnet-name azclisubnet --subnet-prefix 10.0.0.24".format(self._args['resource_group']))

        # results
        results = dict()
        # in loop
        index = 0
        while index < self._args.count:
            for command in commands:
                print('start to run test ' + command)
                # measure time start
                start = time.time()

                # run command
                return_code = call(command)

                if return_code != 0:
                    exit(1)

                # measure time end
                end = time.time()

                latency = end - start

                results[command] = latency
        
        print('test done!')

    def _parse_cli_args(self):
        parser = argparse.ArgumentParser(
                    description='Produce an Ansible Inventory file for an Azure subscription')

        parser.add_argument('--tool', action='store', default='all',
                            help='tools to be tested: (all, azcli, ansible)')
        parser.add_argument('--operations', action='store', default='all',
                            help='operations to be tested: (create, update, delete)')
        parser.add_argument('--resources', action='store', default='all',
                            help='resources to be tested: (vm, storageaccount)')
        parser.add_argument('--count', action='store', default=2,
                            help='test repeat times')
        parser.add_argument('--resource_group', action='store', default='ansibleperftest',
                            help='resource group name')
        return parser.parse_args()

    def _get_commands(self, tools, operations, resources, resourcegroup):
        result = []
        variations = dict()

        for t in tools:
            for o in operations:
                random = random.choice(string.ascii_lowercase)
                for r in resources:
                    variations[[t, r, o].join('_')] = random

        for v in variations.keys():
            if v == 'azcli_vm_create':
                # preparation, create vnet
                cmd = "az vm create -g {0} -n vm{1} -size Standard_DS1_v2 --vnet-name azclivnet --image UbuntuLTS".format(resourcegroup, variations[v])
            if v == 'azcli_vm_update':
                cmd = "az vm update -g {0} -n vm{1} --set tags.tagName=test".format(resourcegroup, variations[v])
            if v == "azcli_vm_delete":
                cmd = "az vm delete -g {0} -n vm{1}".format(resourcegroup, variations[v])
            if v == "ansible_vm_create":
                cmd = "ansible-playbook .\playbooks\vm_create.yml --extra-vars resource_group={0} name={1}".format(resourcegroup, 'vm' + variations[v])
            if v == "ansible_vm_create":
                cmd = "ansible-playbook .\playbooks\vm_create.yml --extra-vars resource_group={0} name={1}".format(resourcegroup, 'vm' + variations[v])
            if v == "ansible_vm_update":
                cmd = "ansible-playbook .\playbooks\vm_update.yml --extra-vars resource_group={0} name={1}".format(resourcegroup, 'vm' + variations[v])
            if v == "ansible_vm_delete":
                cmd = "ansible-playbook .\playbooks\vm_delete.yml --extra-vars resource_group={0} name={1}".format(resourcegroup, 'vm' + variations[v])

def main():
    PerfRunner()


if __name__ == '__main__':
    main()