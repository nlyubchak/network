#!/usr/bin/python3
# -*- coding: utf-8 -*
import re
import logging
import os
import boto3
import urllib
import tempfile
import dns.resolver
from smb.SMBHandler import SMBHandler
from smb.SMBConnection import SMBConnection
from sys import exit

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):

    server = os.environ['DCS_SMB_HOST']
    res = dns.resolver.Resolver(configure=False)
    res.nameservers = ['1.1.24.68',
                       '1.1.1.51']
    dns_response = res.query(server, 'a')

    share = "Network"
    port = 445
    domain = 'meteo'
    username = os.environ['DCS_SMB_USER']
    password = os.environ['DCS_SMB_PASS']
    file_name = "DCs.csv"

    s3_client = boto3.client('s3')
    bucket_name = os.environ['PA_EDL_AWS_S3_BUCKET']
    path = 'iprange/'
    out_file = 'meteo-dcs.txt'

    try:
        if dns_response:
            server = dns_response[0].address
        else:
            raise ValueError("Unable to resolve server's DNS record")
        conn = SMBConnection(
            username, password, 'AWS:LAMBDA:PA_EDL', server, domain, is_direct_tcp=True)
        conn.connect(server, 445)
        file_obj = tempfile.NamedTemporaryFile(mode='w+b', delete=False)
        file_attributes, copysize = conn.retrieveFile(
            share, file_name, file_obj)
        file_obj.seek(0)
        data = file_obj.read().decode('utf-8')
        ips = re.findall(
            '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:\/\d{1,2})?', data)
        if ips:
            ips = [[text.strip('"') for text in line.split(',')]
                   for line in data.split()[1:]]
            payload = '\n'.join(
                set(f"{entry[1]} #{entry[0]}" for entry in ips))
            s3_client.put_object(Bucket=bucket_name,
                                 Key=path+out_file, Body=payload, ContentType='text/html')
        else:
            raise ValueError('Unable to extract IP info')
    except Exception as e:
        logger.exception('Error occurred: ' + str(e))
        exit(1)
    finally:
        file_obj.close()
        conn.close()

    logger.info('Successful Invocation')
