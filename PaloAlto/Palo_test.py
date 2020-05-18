#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
from getpass import getpass

from netmiko import ConnectHandler

start_time = time.time()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

global_username = input("Enter Username: ")
global_password = getpass()

net_connect = ConnectHandler(device_type='paloalto_panos', ip='10.104.253.15', username=global_username, password=global_password)

net_connect.find_prompt()
output = net_connect.send_command("show interface all")
print(output)
