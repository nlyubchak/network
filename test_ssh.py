#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from netmiko import ConnectHandler
from getpass import getpass
import time
import multiprocessing
import re

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

net_connect = ConnectHandler(device_type='cisco_ios',ip='10.50.0.249',username=global_username,password=global_password)
net_connect.find_prompt()
output = net_connect.send_command("show ip int brief")
print(output)
