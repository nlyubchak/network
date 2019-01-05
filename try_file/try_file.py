#!/usr/bin/python3
# -*- coding: utf-8 -*-

from getpass import getpass
import netmiko
import re
import sys

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def make_connection (ip, username, password):
	try:
		netmiko.ConnectHandler(device_type='cisco_ios', ip=ip, username=username, password=password)
	except:
		print((ip) + " - " + bcolors.FAIL + "Cannot connect to this device." + bcolors.ENDC)
		return ip
	return netmiko.ConnectHandler(device_type='cisco_ios', ip=ip, username=username, password=password)

def get_ip (input):
	return(re.findall(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)', input))

		
def get_ips (file_name):
	try:
		for line in open(file_name, 'r').readlines():
			line = get_ip(line)
			for ip in line:
				ips.append(ip)
	except:
		print((file_name) + " - " + bcolors.FAIL + "Couldn't open or read file ip.txt" + bcolors.ENDC)
		sys.exit("Couldn't open or read file ip.txt")

def to_doc_a(file_name, varable):
	f=open(file_name, 'a')
	f.write(varable)
	f.write('\n')
	f.close()
	

def to_doc_w(file_name, varable):
	f=open(file_name, 'w')
	f.write(varable)
	f.close()	
	
#This will be a list of the devices we want to SSH to
ips = []
#Pull the IPs.txt is a list of the IPs we want to connect to
#This function pulls those IPs out of the txt file and puts them into a list
get_ips("IPs.txt")

#Prompt user for account info
username = input("Username: ")
password = getpass()
file_name = "results.csv"
#Clearing all the old info out of the results.csv file 
to_doc_w(file_name, "")

#Make a for loop to hit all the devices, for this we will be looking at the IOS it's running
for ip in ips:
	#Connect to a device
	net_connect = make_connection(ip, username, password)
	#Run a command and set that to output
	try:
		output = net_connect.send_command_expect('show ver | i .bin')
		#Using the split command to cut up the output based on a space
		for each_word in output.split(" "):
		#Then find the part with .bin in it, which will be the IOS file name
			if ".bin" in each_word:
			#And tie that file name to a varable
				ver = each_word
	except:
		ver = "unreachible"

		#Next we'll set a varable to the IP and the IOS with a "," between them, perfect for CSVs.
	results = ip + "," + ver
	#Next we will append the output to the results file
	to_doc_a(file_name, results)
	