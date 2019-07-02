import boto3
import pprint
import secrets
import string
import os
from botocore.exceptions import ClientError

workdocs = boto3.client('workdocs')
workspaces = boto3.client('workspaces')
OrganizationId = os.environ['OrganizationId']
BundleId = os.environ['BundleId']
VolumeEncryptionKey = os.environ['VolumeEncryptionKey']

def Registered_UserDict():
    Registered_Users={}
    response = workdocs.describe_users(
    OrganizationId=OrganizationId
    )
    Username = [X['Username'] for X in response['Users']]
    UserId = [X['Id'] for X in response['Users']]
    Registered_Users = dict(zip(Username,UserId))
    pprint.pprint(Registered_Users)
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
    pprint.pprint(response)

def Create_workspaces(Username,RunningMode,EmailAddress,GivenName,Surname):
    try:
        Registered_UserDict()[Username]
    except KeyError:
        Create_user(Username,EmailAddress,GivenName,Surname)
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
