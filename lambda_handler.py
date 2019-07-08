import boto3
import pprint
import secrets
import string
import os
import logging
import json

from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

workdocs = boto3.client('workdocs')
workspaces = boto3.client('workspaces')
OrganizationId = os.environ['OrganizationId']
BundleId = os.environ['BundleId']
VolumeEncryptionKey = os.environ['VolumeEncryptionKey']

def Registered_UserDict():
    global Registered_Users
    Registered_Users={}
    response = workdocs.describe_users(
    OrganizationId=OrganizationId
    )
    Username = [X['Username'] for X in response['Users']]
    UserId = [X['Id'] for X in response['Users']]
    Registered_Users = dict(zip(Username,UserId))
    #pprint.pprint(Registered_Users)
    return(Registered_Users)

def Delete_user(Username):
    try:
        userid = (Registered_UserDict()[Username])
        response = workdocs.delete_user(
        UserId=userid
        )
    except KeyError as e:
        message = '{0}は存在しません。'.format(e)
        return(message)
    pprint.pprint(response)

def Create_user(Username,EmailAddress,GivenName,Surname):
    password = ''.join([secrets.choice(string.ascii_letters + string.digits +'%&$#()!@') for i in range(8)])
    try:
        response = workdocs.create_user(
            OrganizationId=OrganizationId,
            Username=Username,
            EmailAddress=EmailAddress,
            GivenName=GivenName,
            Surname=Surname,
            Password=password
        )
    except ClientError as e:
        print(e)
        return(e)
    print(password)
    pprint.pprint(response)

def Create_workspaces(Username,RunningMode,EmailAddress,GivenName,Surname):

    try:
        response = workspaces.create_workspaces(
            Workspaces=[
                {
                'DirectoryId': OrganizationId,
                'UserName': Username,
                'BundleId': BundleId,
                'VolumeEncryptionKey': VolumeEncryptionKey,
                'UserVolumeEncryptionEnabled': True,
                'RootVolumeEncryptionEnabled': True,
                'WorkspaceProperties': {
                    'RunningMode': RunningMode,
                    'RunningModeAutoStopTimeoutInMinutes': 60,
                    'RootVolumeSizeGib': 80,
                    'UserVolumeSizeGib': 50,
                    'ComputeTypeName': 'STANDARD'
                },
                'Tags': [
                    {
                        'Key': 'Project',
                        'Value': 'workspace'
                    },
                    {
                        'Key': 'workspace',
                        'Value': ''
                    }
                    ]
                },
            ]
        )
    except:
        pprint.pprint(response)

def Delete_workspaces():
    print("")

def S3_data(Username):
    s3 = boto3.client('s3')
    BUCKET_NAME = 'test-workspaces-data'
    OBJECT_KEY = 'data.csv'
    COMPRESSION_TYPE = 'NONE'
    query = 'SELECT * FROM S3Object s WHERE s.username=\'' + Username + '\''
    response = s3.select_object_content(
        Bucket=BUCKET_NAME,
        Key=OBJECT_KEY,
        ExpressionType='SQL',
        Expression=query,
        InputSerialization={
            'CSV': {
                'FileHeaderInfo': 'USE',
                'RecordDelimiter': '\n',
                'FieldDelimiter': ',',
            },
            'CompressionType': COMPRESSION_TYPE,
        },
        OutputSerialization={
            'JSON': {
            'RecordDelimiter': '\n'
            }
        }
    )
    for payload in response['Payload']:
        if 'Records' in payload:
            records = (payload['Records']['Payload'].decode('utf-8')).replace('\r"}','"},')
            print(records)
            print(type(records))

def User_list():
    global Userlist
    Userlist = []
    Registered_UserDict()
    Dict_Key = ['UserName','Workspaces','Deadline']
    response = workspaces.describe_workspaces(
        DirectoryId=OrganizationId,
    )
    Workspaces_User = [i['UserName'] for i in response['Workspaces']]
    for i in Registered_Users.keys():
        UserDict = {}
        if i in Workspaces_User:
            Workspaces_status = "〇"
            Deadline = ''
        else:
            Workspaces_status = ""
            Deadline = "None"
        Dict_value = [i,Workspaces_status,Deadline]
        UserDict = dict(zip(Dict_Key, Dict_value))
        Userlist.append(UserDict)
    return(Userlist)

def lambda_handler(event, context):
    logger.info(event)
    try:
        action = event['action']
    except:
        action = 'None'
    if action == 'List':
        User_list()
        response = {
        "isBase64Encoded": 'true',
        "statusCode": 200,
        "body": Userlist
        }
    elif action == 'Registration':
        Terget = event['Terget']
        for i in Terget:
            Username = event['Username']
            RunningMode = event['RunningMode']
            EmailAddress = event['EmailAddress']
            GivenName = event['GivenName']
            Surname = event['Surname']
            try:
                Registered_UserDict()[Username]
            except KeyError:
                Create_user(Username,EmailAddress,GivenName,Surname)
            Create_workspaces(Username,RunningMode,EmailAddress,GivenName,Surname)
    elif action == 'Delete':
        Terget = event['Terget']
        for i in Terget:
            Username = event['Username']
            Delete_user(Username)
    else:
        response ={
        "isBase64Encoded": 'true',
        "statusCode": 200,
        "body": "This action is not defined"  
        }
    response = json.dumps(response).encode('utf-8')
    return(response)
