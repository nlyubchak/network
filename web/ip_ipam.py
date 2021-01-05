#!/usr/bin/python3
# -*- coding: utf-8 -*
import orionsdk
import requests
import json
import logging
import boto3
import os
import dns.resolver
from sys import exit


def lambda_handler(event, context):
    """
    Script assumes Solarwinds IPAM has required groups (subnets) configured in a special way:
    1) custom property "IsPublicIPAddress" should be set to "yes"
    2) location information should be filled in the following format:
    City (full city name), Country (as a country code top-level domain, per https://en.wikipedia.org/wiki/List_of_Internet_top-level_domains#Country_code_top-level_domains)
    e.g.
    "Moscow, RU" (no quotes)

    Script performs an API call to Orion Server via HTTPS (port 17778)
    Script uses "orionsdk" module - https://github.com/solarwinds/orionsdk-python
    """

    # define vars
    res = dns.resolver.Resolver(configure=False)
    res.nameservers = ['1.1.24.68',
                        '1.1.1.51']
    server = os.environ['SOLARWINDS_ORION_HOST']
    user = os.environ['SOLARWINDS_ORION_USER']
    passwd = os.environ['SOLARWINDS_ORION_PASS']
    verify = False
    s3_client = boto3.client('s3')
    bucket_name = os.environ['PA_EDL_AWS_S3_BUCKET']
    path = 'iprange/'
    out_file_json = 'meteo_public_ip_addresses.json'
    out_file_txt = 'meteo_public_ip_addresses.txt'

    # configure logging

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if verify is False:
        requests.packages.urllib3.disable_warnings(
            requests.packages.urllib3.exceptions.InsecureRequestWarning)

    # validate connectivity & authentication/authorization

    try:
        dns_response = res.query(server, 'a')
        if dns_response:
            server = dns_response[0].address
        else:
            raise ValueError("Unable to resolve server's DNS record")
        swis = orionsdk.SwisClient(server, user, passwd)
        swis.query("SELECT NodeID from Orion.Nodes")

        data = swis.query(
            "Select Address,CIDR,Location from IPAM.GroupNode gn INNER JOIN IPAM.GroupsCustomProperties gna on gn.GroupID=gna.GroupID where gna.IsPublicIPAddress='yes'")

        data = data['results']
        # filter out any 'None' results
        data = [x for x in data if x['Address'] is not None]
        # exit if data is empty
        if not data:
            raise ValueError('Data returned by Orion is empty, exiting')

        # create a json output (dict with keys as prefix location)

        result_json = {}

        for entry in data:
            if entry['Location'] in result_json.keys():
                result_json[entry['Location']].add(
                    entry['Address']+'/'+str(entry['CIDR']))
            else:
                result_json[entry['Location']] = set()
                result_json[entry['Location']].add(
                    entry['Address']+'/'+str(entry['CIDR']))

        # convert values back to array to support json serialization
        result_json = {k: list(v) for k, v in result_json.items()}
        s3_client.put_object(Bucket=bucket_name, Key=path +
                             out_file_json, Body=json.dumps(result_json), ContentType='application/json')

        # create a simple txt output of all prefixes for PAN EDL

        result_txt = set([entry['Address']+'/'+str(entry['CIDR']) +
                          ' #'+str(entry['Location']) for entry in data])

        s3_client.put_object(Bucket=bucket_name, Key=path +
                             out_file_txt, Body='\n'.join(result_txt), ContentType='text/html')
    except Exception as e:
        logger.exception('Error occurred: ' + str(e))
        exit(1)

    logger.info('Successful invocation')

    return ';'.join(result_txt)
