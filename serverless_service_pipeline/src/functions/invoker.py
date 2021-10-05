import os
import json
import boto3
import pandas
import logging
import requests

from io import BytesIO
from sodapy import Socrata
from datetime import datetime, timedelta

SOCRATA_NORFOLK_FIELDS = [
    'service_request_number',
    'service_request_category',
    'service_request_type',
    'source',
    'status',
    'address',
    'creation_date',
    'modification_date',
]

SQS_CLIENT = boto3.client('sqs')
SOURCE     = 'socrata-norfolk'

DAILY_LOOKBACK_DAYS = int(os.environ['DAILY_LOOKBACK_DAYS'])
SQS_QUEUE           = os.environ['SQS_QUEUE']
SOCRATA_API_TOKEN   = os.environ['SOCRATA_API_TOKEN']

# Setup logger to work with both AWS CloudWatch and locally
if len(logging.getLogger().handlers) > 0:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def valid_message(msg):
    if not all([field in msg for field in SOCRATA_NORFOLK_FIELDS]):
        return False
    else:
        return True


def invoke(event, context):
    
    if event.get('backfill', False):
        
        if not isinstance(event.get('backfill', False), bool):
            raise ValueError('event["backfill"] must be explicitely of type bool')
        if not 'start_date' in event:
            raise ValueError('if backfill set to True event["start_date"] must be specified (yyyy-mm-dd)')
        if not 'end_date' in event:
            raise ValueError('if backfill set to True event["end_date"] must be specified (yyyy-mm-dd)')

        start_date = event['start_date']
        end_date   = event['end_date']

        start = start_date.split('T')[0] + f'T00:00:00.000'
        end   = end_date.split('T')[0]   + f'T23:59:59.999'

    else:

        logger.info(f"Preparing messages with lookback of {DAILY_LOOKBACK_DAYS} days")

        today     = datetime.now()
        
        delta = timedelta(days=DAILY_LOOKBACK_DAYS)
        date  = today - delta
        
        start = str(date ).split(' ')[0] + f'T00:00:00.000'
        end   = str(today).split(' ')[0] + f'T23:59:59.999'
    
    where_query = f'modification_date > "{start}" and modification_date <= "{end}"'

    client = Socrata("data.norfolk.gov", SOCRATA_API_TOKEN)
    
    msgs = client.get("nbyu-xjez", limit=2**32-1, where=where_query)
    
    logger.info(f"Sending {len(msgs)} messages to {SQS_QUEUE}")
    
    for msg in msgs:

        if "location" in msg:
            msg["address"] = msg["location"]
            msg.pop("location")
        else:
            msg["address"] = ""

        msg["source"] = SOURCE

        if not valid_message(msg):
            raise ValueError(f"{msg} doesn't match expected fields {SOCRATA_NORFOLK_FIELDS}")

        SQS_CLIENT.send_message(QueueUrl=SQS_QUEUE,
                                MessageBody=json.dumps(msg))
    
    return 
    
    
    
    
    
    
    
    
    
    
