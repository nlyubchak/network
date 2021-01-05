#!/usr/bin/python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib.request
import base64
import ssl
import re
import logging
import os
import boto3
import dns.resolver
from sys import exit

# configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):

    # define vars

    ctx = ssl._create_unverified_context()
    res = dns.resolver.Resolver(configure=False)
    res.nameservers = ['1.1.2.68',
                       '10.1.1.51']
    server = os.environ['WIK_COM_HOST']
    username = os.environ['WIK_COM_USER']
    password = os.environ['WIK_COM_PASS']
    s3_client = boto3.client('s3')
    bucket_name = os.environ['PA_EDL_AWS_S3_BUCKET']
    path = 'iprange/'
    out_file = 'global-url-blacklist.txt'

    try:
        dns_response = res.query(server, 'a')
        if dns_response:
            server = dns_response[0].address
            download_url = 'https://' + server + \
                '/pages/viewpage.action?pageId=12'
        else:
            raise ValueError("Unable to resolve server's DNS record")
        req = urllib.request.Request(download_url)
        credentials = ('%s:%s' % (username, password))
        encoded_credentials = base64.b64encode(credentials.encode('ascii'))
        req.add_header('Authorization', 'Basic %s' %
                       encoded_credentials.decode("ascii"))
        with urllib.request.urlopen(req, context=ctx) as response:
            data = response.read().decode('utf-8')
            soup = BeautifulSoup(data, features="html.parser")
            block = soup.select("[class~=preformattedContent]")
            if block:
                s3_client.put_object(
                    Bucket=bucket_name, Key=path+out_file, Body='\n'.join(set(block[0].text.split('\n'))), ContentType='text/html')
            else:
                raise ValueError('Unable to extract URL information from page')
    except Exception as e:
        logger.exception('Error occurred: ' + str(e))
        exit(1)

    logging.info('Successful Invocation')
