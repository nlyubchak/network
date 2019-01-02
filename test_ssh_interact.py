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

try:
    f = open('ip.txt')
    connection_data=[]
    filelines = f.read().splitlines()
    for line in filelines:
if line == "": continue
        if line[0] == "#": continue
        conn_data = line.split(',')
        ipaddr=conn_data[0].strip()
        username=global_username
        password=global_password
        if len(conn_data) > 1 and conn_data[1].strip() != "": username = conn_data[1].strip()
        if len(conn_data) > 2 and conn_data[2].strip() != "": password = conn_data[2].strip()
        connection_data.append((ipaddr, username, password))
    f.close()
except:
    sys.exit("Couldn't open or read file ip.txt")


failed_file = open('fail.txt', 'w')
for item in routers_with_issues:
    if item != None:
      failed_file.write("%s\n" % item)
      print(item)

device = {
    'device_type': 'cisco_ios',
    'ip': ip_address.strip(),
    'username': username,
    'password': password,
    'port': 22, }
try:
    config_ok = True

    net_connect = ConnectHandler(**device)

net_connect.find_prompt()
output = net_connect.send_command("show ip int brief")
print(output)


# procedure drouter
def doRouter(connection_data):

    ip_address = connection_data[0]
    username = connection_data[1]
    password = connection_data[2]

ip_check = re.findall("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$", ip_address)
if ip_check == []:
    print(bcolors.FAIL + "Invalid IP - " + str(ip_address) + bcolors.ENDC)
    return ip_address