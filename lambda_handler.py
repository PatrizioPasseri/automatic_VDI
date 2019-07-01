import boto3
import pprint
import secrets
import string

workdocs = boto3.client('workdocs')

def Registered_Users():
    Registered_Users={}
    response = workdocs.describe_users(
    OrganizationId='d-95672d33ae'
    )
    #pprint.pprint(response)
    Username = [X['Username'] for X in response['Users']]
    UserId = [X['Id'] for X in response['Users']]
    Registered_Users = dict(zip(Username,UserId))
    pprint.pprint(Registered_Users)

def Delete_user(userid):
    response = workdocs.delete_user(
        UserId=userid
    )
    pprint.pprint(response)

def Create_user(Username,EmailAddress,GivenName,Surname):
    password = ''.join([secrets.choice(string.ascii_letters + string.digits +'%&$#()!@') for i in range(8)])
    print(password)
    response = workdocs.create_user(
        OrganizationId='d-95672d33ae',
        Username=Username,
        EmailAddress=EmailAddress,
        GivenName=GivenName,
        Surname=Surname,
        Password=password
    )
    pprint.pprint(response)
