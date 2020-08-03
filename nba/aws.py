import boto3
import json
import os

s3 = boto3.resource('s3', aws_access_key_id=os.environ['aws_access_key'],
                    aws_secret_access_key=os.environ['aws_secret_access_key'])
s3_obj = boto3.client('s3', aws_access_key_id=os.environ['aws_access_key'],
                      aws_secret_access_key=os.environ['aws_secret_access_key'])
sns = boto3.client('sns', aws_access_key_id=os.environ['aws_access_key'],
                   aws_secret_access_key=os.environ['aws_secret_access_key'])


def write_obj(obj, key):
    print('write {} to s3'.format(key))
    s3 = boto3.client('s3')
    s3.put_object(
        Body=json.dumps(obj, default=str),
        Bucket='nba-matchups-data',
        Key=key
    )


def key_exists_in_s3(key):
    response = s3_obj.list_objects_v2(
        Bucket='nba-matchups-data',
        MaxKeys=1,
        Prefix=key
    )
    if response['KeyCount'] == 1: return True
    else: return False


# Create an SNS client
def write_sns(message):
    # print('sns disabled atm')
    # Publish a simple message to the specified SNS topic
    response = sns.publish(
        TopicArn='arn:aws:sns:us-east-1:557026794806:Daily-NBA-Matchups',
        Message=message
    )

    # Print out the response
    print('Response from SNS: {}'.format(response))


def read_obj(key):
    print('reading {} from s3'.format(key))
    s3_clientobj = s3_obj.get_object(Bucket='nba-matchups-data', Key=key)
    s3_clientdata = s3_clientobj['Body'].read().decode('utf-8')
    return json.loads(s3_clientdata)
