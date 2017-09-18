import boto3
import gzip
import json
import logging
from tools import Arn

logging.basicConfig(level=logging.INFO)

SESSION = boto3.session.Session()


def lambda_handler(event, context):

    topic_arn       = 'arn:aws:sns:us-east-1:012345678910:my_access_denied_topic'

    # Extracted Bucket and Key from S3 event notification
    bucket  = event['Records'][0]['s3']['bucket']['name']
    key     = event['Records'][0]['s3']['object']['key']

    file_path = '/tmp/logfile.gz'

    boto3.client('s3').download_file(bucket, key, file_path)

    gzfile  = gzip.open(file_path, 'r')

    # Actual CloudTrail Logs
    records = json.loads(gzfile.readlines()[0])['Records']

    access_denied_records = check_records_for_error_code(records)
    send_access_denied_notifications(access_denied_records, topic_arn)


def check_records_for_error_code(records, error_codes = ['AccessDenied', 'AccessDeniedException','Client.UnauthorizedOperation']):

    matched_error_records = []

    for record in records:
        if record.get('errorCode', None) in error_codes:
            logging.debug(record)
            extracted_information = {}
            arn             = Arn(record['userIdentity'].get('arn', None))
            role_name       = arn.get_entity_name()
            service_name    = arn.get_service()
            extracted_information['arn']            = arn.get_full_arn()
            extracted_information['error_code']     = record['errorCode']
            extracted_information['denied_action']  = service_name + ':' + record['eventName']

            if not extracted_information in matched_error_records:
                logging.debug('extracted_information doesn\'t already exist in list of access denieds')
                matched_error_records.append(extracted_information)

    logging.debug(matched_error_records)
    return matched_error_records


def send_access_denied_notifications(access_denied_records, topic_arn):

    if access_denied_records:
        response = boto3.client('sns')\
                            .publish(   TopicArn=topic_arn,
                                        Message=json.dumps(access_denied_records),
                                        Subject='Automated AWS Notification - Access Denied')
