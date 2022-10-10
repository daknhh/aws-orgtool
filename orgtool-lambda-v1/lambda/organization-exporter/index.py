import boto3
import json
import logging
import sys
import os

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT,  level=logging.INFO,  filename='orgtool.log')
logger = logging.getLogger('oustructure')

bucketname = os.environ['BUCKETNAME']
objectname = os.environ['OBJECT']

def get_ou_stucture(parent_id,  org):
    paginator = org.get_paginator('list_organizational_units_for_parent')
    page_iterator = paginator.paginate(ParentId=parent_id)
    ous = {}
    ou_secondlevel = {}
    ou_thirdlevel = {}
    ou_fivelevel = {}
    ou_sixlevel = {}
    ou_sevenlevel = {}
    management_account_ou = {}

    print("\n************************")
    print("\nOrganization-Structure: ")
    print("%s" % (parent_id))

    
    accounts = get_accounts_for_ou(parent_id, org)
    management_account_ou = {'Id': "management-account-ou", 'Name': "management-account", 'SCPs': "None", 'Tags': "None", 'Accounts': accounts['Accounts']}

    for page in page_iterator:
        for ou in page['OrganizationalUnits']:
            logger.info(f'Inititalize Dict for {ou}')
            tags = get_tagsforou(ou['Id'], org)
            accounts = get_accounts_for_ou(ou['Id'], org)
            ous.setdefault('Ous',  []).append({'Id': ou['Id'], 'Name': ou['Name'], 'Tags': tags['Tags'], 'Accounts': accounts['Accounts'], 'Children': {}})
    for idx,  ou in enumerate(ous['Ous']):
        page_iterator = paginator.paginate(ParentId=ou['Id'])
        logger.info(f'Check {ou} for Children')
        for page in page_iterator:
            scp = get_scpforou(ou['Id'], org)
            tags = get_tagsforou(ou['Id'], org)
            accounts = get_accounts_for_ou(ou['Id'], org)
            if page['OrganizationalUnits'] == []:
                ou_secondlevel = {'Children': 'No-Children'}
                print(" - %s" % (ou['Name']))
            else:
                print(" - %s" % (ou['Name']))
                for ou_2l in page['OrganizationalUnits']:
                    print(" - - %s" % (ou_2l['Name']))
                    ou_secondlevel.setdefault('Children',  []).append({'Id': ou_2l['Id'], 'Name': ou_2l['Name'], 'SCP': scp, 'Tags': tags, 'Accounts': accounts, 'Children': {}})
            ous['Ous'][idx] = {'Id': ou['Id'], 'Name': ou['Name'], 'SCPs': scp['SCPs'], 'Tags': tags['Tags'], 'Accounts': accounts['Accounts'], 'Children': ou_secondlevel['Children']}
            if ou_secondlevel == 'No-Children':
                ou_secondlevel = {}
            else:
                ou_secondlevel.clear()

            if ous['Ous'][idx]['Children'] == 'No-Children':
                logger.info('No-Children')
            else:
                for idx2,  ou3 in enumerate(ous['Ous'][idx]['Children']):
                    scp = get_scpforou(ou3['Id'], org)
                    tags = get_tagsforou(ou3['Id'], org)
                    accounts = get_accounts_for_ou(ou3['Id'], org)
                    page_iterator2 = paginator.paginate(ParentId=ou3['Id'])
                    logger.info(f'Check {ou3} for Children')
                    for page in page_iterator2:
                        if page['OrganizationalUnits'] == []:
                            ou_thirdlevel = {'Children': 'No-Children'}
                            logger.info('No-Children')
                            print(" - - - %s" % (ou3['Name']))
                        else:
                            logger.info(page['OrganizationalUnits'])
                            print(" - - - %s" % (ou3['Name']))
                            for ou_3l in page['OrganizationalUnits']:
                                print(" - - - - %s" % (ou_3l['Name']))
                                ou_thirdlevel.setdefault('Children',  []).append({'Id': ou_3l['Id'], 'Name': ou_3l['Name'], 'Tags': tags, 'Accounts': accounts, 'Children': {}})
                        ous['Ous'][idx]['Children'][idx2] = {'Id': ou3['Id'], 'Name': ou3['Name'], 'SCPs': scp['SCPs'], 'Tags': tags['Tags'], 'Accounts': accounts['Accounts'], 'Children': ou_thirdlevel['Children']}
                        if ou_thirdlevel == {'Children': 'No-Children'}:
                            ou_thirdlevel = {}
                        else:
                            ou_thirdlevel.clear()

                        if ous['Ous'][idx]['Children'][idx2]['Children'] == 'No-Children':
                            logger.info('No-Children')
                        else:
                            for idx3,  ou4 in enumerate(ous['Ous'][idx]['Children'][idx2]['Children']):
                                scp = get_scpforou(ou4['Id'], org)
                                tags = get_tagsforou(ou4['Id'], org)
                                accounts = get_accounts_for_ou(ou4['Id'], org)
                                page_iterator3 = paginator.paginate(ParentId=ou4['Id'])
                                logger.info(f'Check {ou4} for Children')
                                for page in page_iterator3:
                                    if page['OrganizationalUnits'] == []:
                                        ou_fivelevel = {'Children': 'No-Children'}
                                        logger.info('No-Children')
                                        print(" - - - - - %s" % (ou4['Name']))
                                    else:
                                        logger.info(page['OrganizationalUnits'])
                                        print(" - - - - - %s" % (ou4['Name']))
                                        for ou_4l in page['OrganizationalUnits']:
                                            print(" - - - - - - %s" % (ou_4l['Name']))
                                            ou_fivelevel.setdefault('Children',  []).append({'Id': ou_4l['Id'], 'Name': ou_4l['Name'], 'Tags': tags, 'Accounts': accounts, 'Children': {}})
                                    ous['Ous'][idx]['Children'][idx2]['Children'][idx3] = {'Id': ou4['Id'], 'Name': ou4['Name'], 'SCPs': scp['SCPs'], 'Tags': tags['Tags'], 'Accounts': accounts['Accounts'], 'Children': ou_fivelevel['Children']}
                                    if ou_fivelevel == {'Children': 'No-Children'}:
                                        ou_fivelevel = {}
                                    else:
                                        ou_fivelevel.clear()

                                    if ous['Ous'][idx]['Children'][idx2]['Children'][idx3]['Children'] == 'No-Children':
                                        logger.info('No-Children')
                                    else:
                                        for idx4,  ou5 in enumerate(ous['Ous'][idx]['Children'][idx2]['Children'][idx3]['Children']):
                                            scp = get_scpforou(ou5['Id'], org)
                                            tags = get_tagsforou(ou5['Id'], org)
                                            accounts = get_accounts_for_ou(ou5['Id'], org)
                                            page_iterator4 = paginator.paginate(ParentId=ou5['Id'])
                                            logger.info(f'Check {ou5} for Children')
                                            for page in page_iterator4:
                                                if page['OrganizationalUnits'] == []:
                                                    ou_sixlevel = {'Children': 'No-Children'}
                                                    logger.info('No-Children')
                                                    print(" - - - - - %s" % (ou5['Name']))
                                                else:
                                                    logger.info(page['OrganizationalUnits'])
                                                    print(" - - - - - %s" % (ou5['Name']))
                                                    for ou_5l in page['OrganizationalUnits']:
                                                        print(" - - - - - - %s" % (ou_5l['Name']))
                                                        ou_sixlevel.setdefault('Children',  []).append({'Id': ou_5l['Id'], 'Name': ou_5l['Name'], 'Tags': tags, 'Accounts': accounts, 'Children': {}})
                                                ous['Ous'][idx]['Children'][idx2]['Children'][idx3]['Children'][idx4] = {'Id': ou5['Id'], 'Name': ou5['Name'], 'SCPs': scp['SCPs'], 'Tags': tags['Tags'], 'Accounts': accounts['Accounts'], 'Children': ou_sixlevel['Children']}
                                                if ou_sixlevel == {'Children': 'No-Children'}:
                                                    ou_sixlevel = {}
                                                else:
                                                    ou_sixlevel.clear()
                                            if ous['Ous'][idx]['Children'][idx2]['Children'][idx3]['Children'][idx4]['Children'] == 'No-Children':
                                                logger.info('No-Children')
                                            else:
                                                for idx5,  ou6 in enumerate(ous['Ous'][idx]['Children'][idx2]['Children'][idx3]['Children'][idx4]['Children']):
                                                    scp = get_scpforou(ou6['Id'], org)
                                                    tags = get_tagsforou(ou6['Id'], org)
                                                    accounts = get_accounts_for_ou(ou6['Id'], org)
                                                    page_iterator5 = paginator.paginate(ParentId=ou6['Id'])
                                                    logger.info(f'Check {ou6} for Children')
                                                    for page in page_iterator5:
                                                        if page['OrganizationalUnits'] == []:
                                                            ou_sevenlevel = {'Children': 'No-Children'}
                                                            logger.info('No-Children')
                                                            print(" - - - - - - %s" % (ou6['Name']))
                                                        else:
                                                            logger.info(page['OrganizationalUnits'])
                                                            print(" - - - - - - %s" % (ou6['Name']))
                                                            for ou_6l in page['OrganizationalUnits']:
                                                                print(" - - - - - - - %s" % (ou_6l['Name']))
                                                                ou_sevenlevel.setdefault('Children',  []).append({'Id': ou_6l['Id'], 'Name': ou_6l['Name'], 'Tags': tags, 'Accounts': accounts, 'Children': {'Children': 'No-Children'}})
                                                        ous['Ous'][idx]['Children'][idx2]['Children'][idx3]['Children'][idx4]['Children'][idx5] = {'Id': ou6['Id'], 'Name': ou6['Name'], 'SCPs': scp['SCPs'], 'Tags': tags['Tags'], 'Accounts': accounts['Accounts'], 'Children': ou_sevenlevel['Children']}
                                                        if ou_sevenlevel == {'Children': 'No-Children'}:
                                                            ou_sevenlevel = {}
                                                        else:
                                                            ou_sevenlevel.clear()
    print(f"- Adding Management Account to export in fake management-account-ou")
    ous['Ous'].append(management_account_ou)
    return ous


def export_structure(file,  org, s3):
    root_id = org.list_roots()['Roots'][0]['Id']
    logger.info('Query first level OUs')
    ous = get_ou_stucture(root_id, org)

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


def get_tagsforou(ressource_id, org):
    response = org.list_tags_for_resource(
        ResourceId=ressource_id)
    tags = {}
    tags.setdefault('Tags', [])
    for tag in response['Tags']:
        tags.setdefault('Tags', []).append(tag)
    return tags


def get_accounts_for_ou(ou, org):
    response = org.list_accounts_for_parent(
        ParentId=ou)
    accounts = {}
    accounts.setdefault('Accounts', [])
    for account in response['Accounts']:
        accounttags = get_tagsforou(account['Id'], org)
        accounts.setdefault('Accounts', []).append({'Id': account['Id'], 'Tags': accounttags['Tags'],'Email': account['Email'], 'Name': account['Name']})
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
    return(res)

# ------------------------------------------------------------------------------
# lambda_handler
# ------------------------------------------------------------------------------
def lambda_handler(event, context):
    session = boto3.Session()
    org = session.client('organizations')
    s3 = session.client('s3')
    export_structure(objectname, org, s3)