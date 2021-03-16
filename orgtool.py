import boto3
import json
import logging
import sys, getopt

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO, filename='orgtool.log')
logger = logging.getLogger('oustructure')

def export_policies(file,profile):
    session = boto3.Session(profile_name=profile)
    org = session.client('organizations')
    response = org.list_policies(
    Filter='SERVICE_CONTROL_POLICY'
    )
    logger.info(f'Inititalize Dict for SCPs')
    policies = {}

    for scp in response['Policies']:
        contentfile = f"scps/{scp['Name']}.json"
        
        responsepolicy = org.describe_policy(
            PolicyId=scp['Id']
            )
        content = responsepolicy['Policy']['Content']
        scpcontent = open(contentfile, "w")
        json.dump(content, scpcontent, indent = 6)
        scpcontent.close()
        logger.info(f'Created SCP Content File: {contentfile} in scps directory 🗂.')
        print(f'Created SCP Content File: {contentfile} in scps directory 🗂.')
        policies.setdefault('Scps', []).append({'Id': scp['Id'],'Name': scp['Name'],'Description': scp['Description'],'ContentFile':contentfile})
        logger.info(f'Add SCP {scp} to policies Dict.')
        print(f"Add SCP {scp['Name']} to policies Dict.")
    out_file = open(file, "w") 
    json.dump(policies, out_file, indent = 6) 
    out_file.close()
    logger.info(f'Created SCPs File: {file}.')
    print("\n************************")
    print(f'SCPs have been written to File: {file} 🗃.')

def import_policies(file,profile):
    session = boto3.Session(profile_name=profile)
    org = session.client('organizations')
    logger.info(f'Import Json file: {file}')    
    f = open(file,)
    data = json.load(f) 
    print("\n************************")
    print("\nImport-SCPs:")

    for scp in data['Scps']:
        print(f"- {scp['Name']}")
        f = open(scp['ContentFile'],)
        print(f"  - Import Json file: {scp['ContentFile']}.")
        logger.info(f"Import Json file: {scp['ContentFile']}.")  
        data = json.load(f)
        try:
            response = org.create_policy(
            Content=data,
            Description=scp['Description'],
            Name=scp['Name'],
            Type='SERVICE_CONTROL_POLICY'
            )
            logger.info(f"Created SCP with Name: {scp['Name']} - Id: {response['Policy']['PolicySummary']['Id']}.") 
            print(f"✅ Created SCP with Name: {scp['Name']} - Id: {response['Policy']['PolicySummary']['Id']}. \n\n") 
        except org.exceptions.DuplicatePolicyException:
            logger.info(f"SCP with Name: {scp['Name']} - already exist.") 
            print(f"ℹ SCP with Name: {scp['Name']} - already exist. \n\n") 
    print("\n************************")
    print(f'✅ SCPs have been imported.')

def get_ou_stucture(parent_id,profile):
    session = boto3.Session(profile_name=profile)
    org = session.client('organizations')
    paginator = org.get_paginator('list_organizational_units_for_parent')
    page_iterator = paginator.paginate(ParentId=parent_id)
    ous = {}
    ou_secondlevel = {}
    ou_thirdlevel = {}
    ou_fivelevel = {}
    ou_sixlevel = {}
    ou_sevenlevel = {}
    print("\n************************")
    print("\nOrganization-Structure: ")
    print("%s" % (parent_id))

    for page in page_iterator:
        for ou in page['OrganizationalUnits']:
            logger.info(f'Inititalize Dict for {ou}')
            ous.setdefault('Ous', []).append({'Id': ou['Id'],'Name': ou['Name'],'Children': {}})

    for idx, ou in enumerate(ous['Ous']):
        page_iterator = paginator.paginate(ParentId=ou['Id'])
        logger.info(f'Check {ou} for Children')
        for page in page_iterator:
            if page['OrganizationalUnits'] == []:
                ou_secondlevel = {'Children':'No-Children'}
                print(" - %s" % (ou['Name']))
            else:
                print(" - %s" % (ou['Name']))
                for ou_2l in page['OrganizationalUnits']:   
                    print(" - - %s" % (ou_2l['Name']))
                    ou_secondlevel.setdefault('Children', []).append({'Id': ou_2l['Id'],'Name': ou_2l['Name'],'Children': {}})       
            ous['Ous'][idx] = {'Id': ou['Id'],'Name': ou['Name'],'Children':ou_secondlevel['Children']}
            if ou_secondlevel == 'No-Children':
                ou_secondlevel = {}
            else:
                ou_secondlevel.clear()

            if ous['Ous'][idx]['Children'] == 'No-Children':
                logger.info('No-Children') 
            else:
                for idx2, ou3 in enumerate(ous['Ous'][idx]['Children']):
                    page_iterator2 = paginator.paginate(ParentId=ou3['Id'])
                    logger.info(f'Check {ou3} for Children')
                    for page in page_iterator2:
                        if page['OrganizationalUnits'] == []:
                            ou_thirdlevel = {'Children':'No-Children'}
                            logger.info(f'No-Children')
                            print(" - - - %s" % (ou3['Name']))
                        else:
                            logger.info(page['OrganizationalUnits'])
                            print(" - - - %s" % (ou3['Name']))
                            for ou_3l in page['OrganizationalUnits']:
                                print(" - - - - %s" % (ou_3l['Name']))
                                ou_thirdlevel.setdefault('Children', []).append({'Id': ou_3l['Id'],'Name': ou_3l['Name'],'Children': {}})       
                        ous['Ous'][idx]['Children'][idx2] = {'Id': ou3['Id'],'Name': ou3['Name'],'Children':ou_thirdlevel['Children']}
                        if ou_thirdlevel == {'Children':'No-Children'}:
                            ou_thirdlevel = {}
                        else:
                            ou_thirdlevel.clear()
                        
                        if ous['Ous'][idx]['Children'][idx2]['Children'] == 'No-Children':
                            logger.info('No-Children')
                        else:
                            for idx3, ou4 in enumerate(ous['Ous'][idx]['Children'][idx2]['Children']):
                                page_iterator3 = paginator.paginate(ParentId=ou4['Id'])
                                logger.info(f'Check {ou4} for Children')
                                for page in page_iterator3:
                                    if page['OrganizationalUnits'] == []:
                                        ou_fivelevel = {'Children':'No-Children'}
                                        logger.info(f'No-Children')
                                        print(" - - - - - %s" % (ou4['Name']))
                                    else:
                                        logger.info(page['OrganizationalUnits'])
                                        print(" - - - - - %s" % (ou4['Name']))
                                        for ou_4l in page['OrganizationalUnits']:
                                            print(" - - - - - - %s" % (ou_4l['Name']))
                                            ou_fivelevel.setdefault('Children', []).append({'Id': ou_4l['Id'],'Name': ou_4l['Name'],'Children': {}})
                                    ous['Ous'][idx]['Children'][idx2]['Children'][idx3] = {'Id': ou4['Id'],'Name': ou4['Name'],'Children':ou_fivelevel['Children']}                      
                                    if ou_fivelevel == {'Children':'No-Children'}:
                                        ou_fivelevel = {}
                                    else:
                                        ou_fivelevel.clear()
                                    
                                    if ous['Ous'][idx]['Children'][idx2]['Children'][idx3]['Children'] == 'No-Children':
                                        logger.info('No-Children')
                                    else:
                                        for idx4, ou5 in enumerate(ous['Ous'][idx]['Children'][idx2]['Children'][idx3]['Children']):
                                            page_iterator4 = paginator.paginate(ParentId=ou5['Id'])
                                            logger.info(f'Check {ou5} for Children')
                                            for page in page_iterator4:
                                                if page['OrganizationalUnits'] == []:
                                                    ou_sixlevel = {'Children':'No-Children'}
                                                    logger.info(f'No-Children')
                                                    print(" - - - - - %s" % (ou5['Name']))
                                                else:
                                                    logger.info(page['OrganizationalUnits'])
                                                    print(" - - - - - %s" % (ou5['Name']))
                                                    for ou_5l in page['OrganizationalUnits']:
                                                        print(" - - - - - - %s" % (ou_5l['Name']))
                                                        ou_sixlevel.setdefault('Children', []).append({'Id': ou_5l['Id'],'Name': ou_5l['Name'],'Children': {}})
                                                ous['Ous'][idx]['Children'][idx2]['Children'][idx3]['Children'][idx4] = {'Id': ou5['Id'],'Name': ou5['Name'],'Children':ou_sixlevel['Children']}                      
                                                if ou_sixlevel == {'Children':'No-Children'}:
                                                    ou_sixlevel = {}
                                                else:
                                                    ou_sixlevel.clear()
                                            if ous['Ous'][idx]['Children'][idx2]['Children'][idx3]['Children'][idx4]['Children'] == 'No-Children':
                                                logger.info('No-Children')
                                            else:
                                                for idx5, ou6 in enumerate(ous['Ous'][idx]['Children'][idx2]['Children'][idx3]['Children'][idx4]['Children']):
                                                    page_iterator5 = paginator.paginate(ParentId=ou6['Id'])
                                                    logger.info(f'Check {ou6} for Children')
                                                    for page in page_iterator5:
                                                        if page['OrganizationalUnits'] == []:
                                                            ou_sevenlevel = {'Children':'No-Children'}
                                                            logger.info(f'No-Children')
                                                            print(" - - - - - - %s" % (ou6['Name']))
                                                        else:
                                                            logger.info(page['OrganizationalUnits'])
                                                            print(" - - - - - - %s" % (ou6['Name']))
                                                            for ou_6l in page['OrganizationalUnits']:
                                                                print(" - - - - - - - %s" % (ou_6l['Name']))
                                                                ou_sevenlevel.setdefault('Children', []).append({'Id': ou_6l['Id'],'Name': ou_6l['Name'],'Children': {'Children':'No-Children'}})
                                                        ous['Ous'][idx]['Children'][idx2]['Children'][idx3]['Children'][idx4]['Children'][idx5] = {'Id': ou6['Id'],'Name': ou6['Name'],'Children':ou_sevenlevel['Children']}                      
                                                        if ou_sevenlevel == {'Children':'No-Children'}:
                                                            ou_sevenlevel = {}
                                                        else:
                                                            ou_sevenlevel.clear()    
    return ous

def export_structure(file,profile):
    session = boto3.Session(profile_name=profile)
    org = session.client('organizations')
    root_id = org.list_roots()['Roots'][0]['Id']
    logger.info('Query first level OUs')
    ous= get_ou_stucture(root_id,profile)
    out_file = open(file, "w") 
    json.dump(ous, out_file, indent = 6) 
    out_file.close()
    print("\n************************")
    logger.info(f'\n Write Ous to file: {file}')
    print(f'Ous have been written to {file}.')

def get_ou_id_by_name(name,parent_id,profile):
    session = boto3.Session(profile_name=profile)
    org = session.client('organizations')
    paginator = org.get_paginator('list_organizational_units_for_parent')
    page_iterator = paginator.paginate(ParentId=parent_id)
    session = boto3.Session(profile_name=profile)
    search_key = name
    logger.info(f'Search for OuID by name: {name}')
    for page in page_iterator:
        for ou in page['OrganizationalUnits']:
            for (key, value) in ou.items():
                    if value == search_key:
                            res = ou['Id']
                            logger.info(f'Got OuID: {res}')
    return(res)

def import_structure(file,profile):
    session = boto3.Session(profile_name=profile)
    org = session.client('organizations')
    logger.info(f'Import Json file: {file}')    
    f = open(file,)
    data = json.load(f) 
    
    root_id = org.list_roots()['Roots'][0]['Id']
    print("\n************************")
    print("\nOrganization-Structure: ")
    print(f'{root_id}')
    
    for firstlevel in data['Ous']: 
        try:
            response = org.create_organizational_unit(
            ParentId=root_id,
            Name=firstlevel['Name']
            )
            firstlevelou_id = response['OrganizationalUnit']['Id']
            firstlevelname= firstlevel['Name']
            logger.info(f'Created OU: {firstlevelou_id} - {firstlevelname} in {root_id}')
            print(f' - {firstlevelname}')
        except (org.exceptions.DuplicateOrganizationalUnitException):
            logger.info('OU already exist')
            firstlevelname = firstlevel['Name']
            print(f' - {firstlevelname}')
            firstlevelou_id = get_ou_id_by_name(firstlevel['Name'],root_id,profile)
        
        if firstlevel['Children'] == 'No-Children':
            logger.info(f'{firstlevelname} has no No-Children')
        else:
            for secondlevel in firstlevel['Children']:
                try:
                    response2 = org.create_organizational_unit(
                    ParentId=firstlevelou_id,
                    Name=secondlevel['Name']
                    )
                    secondlevelou_id = response2['OrganizationalUnit']['Id']
                    secondlevelname = secondlevel['Name']
                    logger.info(f'Created OU: {secondlevelname} with Id: {secondlevelou_id} {firstlevelname} in {firstlevelou_id}')
                    print(f' - - {secondlevelname}')
                except (org.exceptions.DuplicateOrganizationalUnitException):
                    secondlevelname = secondlevel['Name']
                    print(f' - - {secondlevelname}')
                    secondlevelou_id = get_ou_id_by_name(secondlevel['Name'],firstlevelou_id,profile)

                if secondlevel['Children'] == 'No-Children':
                    logger.info(f'{secondlevelname} has no No-Children')
                else:
                    for thirdlevel in secondlevel['Children']:
                        try:
                            response3 = org.create_organizational_unit(
                            ParentId=secondlevelou_id,
                            Name=thirdlevel['Name']
                            )
                            thirdlevellevelou_id = response3['OrganizationalUnit']['Id']
                            thirdlevelname = thirdlevel['Name']
                            logger.info(f'Created OU: {thirdlevelname} with Id: {thirdlevellevelou_id} {secondlevelname} in {secondlevelou_id}')
                            print(f'- - - {thirdlevelname}')
                        except (org.exceptions.DuplicateOrganizationalUnitException):
                            thirdlevelname = thirdlevel['Name']
                            print(f'- - - {thirdlevelname}')
                            thirdlevellevelou_id = get_ou_id_by_name(thirdlevel['Name'],secondlevelou_id,profile)

                        if thirdlevel['Children'] == 'No-Children':
                            logger.info(f'{thirdlevelname} has no No-Children')
                        else:
                            for fourlevel in thirdlevel['Children']:
                                try:
                                    response4 = org.create_organizational_unit(
                                    ParentId=thirdlevellevelou_id,
                                    Name=fourlevel['Name']
                                    )
                                    fourlevelou_id = response4['OrganizationalUnit']['Id']
                                    fourlevelname = fourlevel['Name']
                                    logger.info(f'Created OU: {fourlevelname} with Id: {fourlevelou_id} in {thirdlevellevelou_id}')
                                    print(f'- - - - {fourlevelname}')
                                except (org.exceptions.DuplicateOrganizationalUnitException):
                                    fourlevelname = fourlevel['Name']
                                    print(f'- - - - {fourlevelname}')
                                    fourlevelou_id = get_ou_id_by_name(fourlevel['Name'],thirdlevellevelou_id,profile)
                            
                            if fourlevel['Children'] == 'No-Children':
                                logger.info(f'{fourlevelname} has no No-Children')
                            else:
                                for fivelevel in fourlevel['Children']:
                                    try:
                                        response5 = org.create_organizational_unit(
                                        ParentId=fourlevelou_id,
                                        Name=fivelevel['Name']
                                        )
                                        fivelevelou_id = response5['OrganizationalUnit']['Id']
                                        fivelevelname = fivelevel['Name']
                                        logger.info(f'Created OU: {fivelevelname} with Id: {fivelevelou_id} in {thirdlevellevelou_id}')
                                        print(f'- - - - - {fivelevelname}')
                                    except (org.exceptions.DuplicateOrganizationalUnitException):
                                        fivelevelname = fivelevel['Name']
                                        print(f'- - - - - {fivelevelname}')
                                        fivelevelou_id = get_ou_id_by_name(fivelevel['Name'],fourlevelou_id,profile)

    f.close() 
    logger.info(f'\n OU Structure has been imported.')
    logger.info(f'\n********************************')

def main(argv):
    print('------------------------------------------------------------------------------')
    print('ORGTOOL for exporting and importing AWS organizations structure to / from Json')
    print('------------------------------------------------------------------------------')
    try:
        opts, args = getopt.getopt(argv,"hu:f:p:",["u=","f=","p="])
    except getopt.GetoptError:
        print('Usage:')
        print('Export: orgtool.py -u export -f <file.json> -p AWSPROFILE')
        print('Export SCPs: orgtool.py -u export-scps -p AWSPROFILE')
        print('Import: orgtool.py -u import -f <file.json> -p AWSPROFILE')
        print('Import SCPs: orgtool.py -u import-scps -f <file.json> -p AWSPROFILE')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Usage:')
            print('Export: orgtool.py -u export -f <file.json> -p AWSPROFILE')
            print('Export SCPs: orgtool.py -u export-scps -f <file.json> -p AWSPROFILE')
            print('Import: orgtool.py -u import -f <file.json> -p AWSPROFILE')
            print('Import SCPs: orgtool.py -u import-scps -f <file.json> -p AWSPROFILE')
            sys.exit()
        elif opt in ("-u", "--usage"):
            print(f'Current usage: {arg}')
            logger.info(f'Usage:{arg}')
            usage = arg
        elif opt in ("-f", "--file"):
            print(f'File {arg}')
            logger.info(f'File:{arg}')
            file = arg
        elif opt in ("-p", "--profile"):
            print(f'Profile {arg}')
            logger.info(f'Profile:{arg}')
            profile = arg
    if usage == 'export':
        logger.info('---------------------------------------------------')
        logger.info('NEW REQUEST: Export OUs to Json')
        export_structure(file,profile)
    elif usage == 'import':
        logger.info('---------------------------------------------------')
        logger.info('NEW REQUEST: Import OUs from Json')
        import_structure(file,profile)
    elif usage == 'export-scps':
        logger.info('---------------------------------------------------')
        logger.info('NEW REQUEST: Export Scps to Json')
        export_policies(file,profile)
    elif usage == 'import-scps':
        logger.info('---------------------------------------------------')
        logger.info('NEW REQUEST: Import Scps from Json')
        import_policies(file,profile)
    print('ℹ️: logs can be found in orgtool.log')

if __name__ == "__main__":
   main(sys.argv[1:])

