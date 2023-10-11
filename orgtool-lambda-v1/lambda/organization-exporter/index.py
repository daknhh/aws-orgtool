import boto3
import json
import logging
import os

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT,  level=logging.INFO,  filename='orgtool.log')
logger = logging.getLogger('oustructure')

bucketname = os.environ['BUCKETNAME']
objectname = os.environ['OBJECT']


def get_organization_structure(parent_id, org, level=1):
    paginator = org.get_paginator('list_organizational_units_for_parent')
    page_iterator = paginator.paginate(ParentId=parent_id)
    print(f"\nOrganization-Structure (Level {level}): ")
    print(f"{parent_id}")
    if (level == 1):
        ous = {'Ous': []}
    else:
        ous = []
    for page in page_iterator:
        for ou in page['OrganizationalUnits']:
            tags = get_tags_for_resource(ou['Id'], org)
            accounts = get_accounts_for_ou(ou['Id'], org)
            scps = get_scpforou(ou['Id'], org)['SCPs']
            children = get_organization_structure(ou['Id'], org, level+1)
            if (children == [] or children == {'Ous': []}):
                children = "No-Children"
            ou_structure = {
                'Id': ou['Id'],
                'Name': ou['Name'],
                'Tags': tags['Tags'],
                'SCPs': scps,
                'Accounts': accounts['Accounts'],
                'Children': children
            }
            if (level == 1):
                ous['Ous'].append(ou_structure)
            else:
                ous.append(ou_structure)
    return ous


def export_structure(file,  org, s3):
    root_id = org.list_roots()['Roots'][0]['Id']
    logger.info('Query first level OUs')
    ous = get_organization_structure(root_id, org)
    print("\n************************")
    s3.put_object(
        Body=json.dumps(ous),
        Bucket=bucketname,
        Key=objectname,
        ACL='bucket-owner-full-control',
        ServerSideEncryption='AES256',
    )
    logger.info(f'\n Write Ous to s3: {bucketname} - {objectname}')


def get_scpforou(ou_id,  org):
    response = org.list_policies_for_target(
        TargetId=ou_id,
        Filter='SERVICE_CONTROL_POLICY')
    scp = {}
    scp.setdefault('SCPs', [])
    for policy in response['Policies']:
        if policy['Name'] == 'FullAWSAccess':
            logger.info('\n AWS SCP Found: FullAWSAccess')
        else:
            scp.setdefault('SCPs', []).append({'Name': policy['Name']})
    return scp


def get_tags_for_resource(ressource_id, org):
    response = org.list_tags_for_resource(
        ResourceId=ressource_id)
    tags = {}
    tags.setdefault('Tags', [])
    for tag in response['Tags']:
        tags.setdefault('Tags', []).append(tag)
    return tags


def get_accounts_for_ou(ou, org):
    paginator = org.get_paginator('list_accounts_for_parent')
    page_iterator = paginator.paginate(ParentId=ou)
    accounts = {}
    accounts.setdefault('Accounts', [])
    for page in page_iterator:
        for account in page['Accounts']:
            accounttags = get_tags_for_resource(account['Id'], org)
            accounts['Accounts'].append({
                'Id': account['Id'],
                'Tags': accounttags['Tags'],
                'Email': account['Email'],
                'Name': account['Name'],
            })
    return accounts


def get_ou_id_by_name(name,  parent_id,  org):
    paginator = org.get_paginator('list_organizational_units_for_parent')
    page_iterator = paginator.paginate(ParentId=parent_id)
    search_key = name
    logger.info(f'Search for OuID by name: {name}')
    for page in page_iterator:
        for ou in page['OrganizationalUnits']:
            for (key,  value) in ou.items():
                if value == search_key:
                    res = ou['Id']
                    logger.info(f'Got OuID: {res}')
    return (res)

# ------------------------------------------------------------------------------
# lambda_handler
# ------------------------------------------------------------------------------


def lambda_handler(event, context):
    session = boto3.Session()
    org = session.client('organizations')
    s3 = session.client('s3')
    export_structure(objectname, org, s3)
