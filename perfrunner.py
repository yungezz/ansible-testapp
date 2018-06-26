import argparse
import os
import types
import copy
import random
import string
import time
import subprocess

from os.path import expanduser

class PerfRunner(object):
    def __init__(self):

        # parse args
        self._args = self._parse_cli_args()

        # get commands
        azcli_commands = self._get_azcli_commands(self._args.resource_group, 'UbuntuLTS', 'Standard_DS1_v2')
        ansible_commands = self._get_ansible_commands(self._args.resource_group, "UbuntuLTS", 'Standard_DS1_v2')


        # results
        results = dict()

        # in loop
        index = 0
        while index < self._args.count:
            index = index + 1
            for item in azcli_commands:
                for command in item:
                    print('start to run ' + command)
                    # measure time start
                    start = time.time()

                    # run az cli command
                    return_code = subprocess.check_call(item[command], stdout=subprocess.PIPE, shell=True)

                    # measure time end
                    end = time.time()
                    latency = end - start

                    results[command] = latency
                    print(command + "======================================")
                    print(latency)
            
            for it in ansible_commands:
                for cmd in it:
                    print('start to run ansible commands: ')
                    
                    return_code = subprocess.check_call(it[cmd], stdout=subprocess.PIPE, shell=True)

                    print("ansible command done!================================")
        
        print('test done!')

    def _parse_cli_args(self):
        parser = argparse.ArgumentParser(
                    description='Produce an Ansible Inventory file for an Azure subscription')

        parser.add_argument('--count', action='store', default=2,
                            help='test repeat times')
        parser.add_argument('--resource_group', action='store', default='ansibleperftest',
                            help='resource group name')
        parser.add_argument('--output', action='store', default='.\testresult.txt',
                            help='output file name')
        return parser.parse_args()

    def _get_azcli_commands(self, resourcegroup, imagename, size):
        result = []
        seed = ''.join(random.choice(string.ascii_lowercase) for i in range(5))

        vm_name = 'vm' + seed

        result.append({ 'create_resourcegroup': "az group create -n {0} -l eastus".format(resourcegroup) })
        result.append({ 'create_vnet': "az network vnet create -g {0} -n {1} --address-prefix 10.0.0.0/16".format(resourcegroup, vm_name) })
        result.append({ 'create_subnet': "az network vnet subnet create -g {0} -n {1} --vnet-name {2} --address-prefix 10.0.0.0/24".format(resourcegroup, vm_name, vm_name) })
        result.append({ 'create_vm': "az vm create -g {0} -n {1} --size Standard_DS1_v2 --vnet-name {2} --image UbuntuLTS".format(resourcegroup, vm_name, vm_name) })
        result.append({ 'update_vm': "az vm update -g {0} -n {1} --set tags.testTag=xxxx".format(resourcegroup, vm_name) })
        result.append({ 'delete_vm': "az vm delete -g {0} -n {1} -y".format(resourcegroup, vm_name) })

        return result

    def _get_ansible_commands(self, resourcegroup, image, size):
        result = []
        seed = ''.join(random.choice(string.ascii_lowercase) for i in range(5))

        vm_name = 'vm' + seed
        playbook = "./playbooks/vm_create.yml"
        logfile = "./ansible.output"

        result.append({ 'ansiblevm': "ansible-playbook {0} --extra-vars resource_group={1} vm_name={2} >>  {3}".format(playbook, resourcegroup, vm_name, logfile) })

def main():
    PerfRunner()


if __name__ == '__main__':
    main()
