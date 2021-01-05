#!/usr/bin/python3
# -*- coding: utf-8 -*
import urllib.request
import logging
import boto3
import os
import json
from bs4 import BeautifulSoup
from sys import exit

# configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):

    # define vars
    s3_client = boto3.client('s3')
    bucket_name = os.environ['PA_EDL_AWS_S3_BUCKET']
    path = 'iprange/'
    out_file = 'ips-ms-azure.txt'

    try:
        sources = []
        urls = ['https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519',
                'https://www.microsoft.com/en-us/download/confirmation.aspx?id=57064', 'https://www.microsoft.com/en-us/download/confirmation.aspx?id=57062']
        for url in urls:
            req = urllib.request.Request(
                url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = response.read().decode('utf-8')
            soup = BeautifulSoup(data, features="html.parser")
            for link in soup.find_all('a'):
                source = link.get('href')
                if 'ServiceTags_' in source:
                    sources.append(source)
                    break
            else:
                raise ValueError('Unable to extract IP source location URL')
        ips = ""
        for source in sources:
            req = urllib.request.Request(
                source, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = response.read().decode('utf-8')
            json_data = json.loads(data)
            ip = '\n'.join(['\n'.join(entry['properties']['addressPrefixes'])
                            for entry in json_data['values'] if entry['name'] == "AzureCloud"])
            ips += ip+'\n'

        if not ips:
            raise ValueError('Unable to extract IP information from source')
       # s3_client.put_object(Bucket=bucket_name, Key=path+out_file, Body=ips, ContentType='text/html')
        print(ips)
    except Exception as e:
        logger.exception('Error occured: ' + str(e))
        exit(1)
    logging.info('Successful invocation')
