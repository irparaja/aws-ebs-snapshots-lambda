import boto3
import re
import collections
import datetime

# Source Region - the region our instances are running in that we're backing up
source_region = 'eu-central-1' 
copy_region = 'eu-west-1'

ec = boto3.client('ec2')
iam = boto3.client('iam')

def lambda_handler(event, context):
    account_ids = list()
    try:
        """
        You can replace this try/except by filling in `account_ids` yourself.
        Get your account ID with:
        > import boto3
        > iam = boto3.client('iam')
        > print iam.get_user()['User']['Arn'].split(':')[4]
        """
        iam.get_user()
    except Exception as e:
        # use the exception message to get the account ID the function executes under
        account_ids.append(re.search(r'(arn:aws:sts::)([0-9]+)', str(e)).groups()[1])

    today_fmt = datetime.date.today().strftime('%Y-%m-%d')

        # limit snapshots to process to ones marked for deletion on this day
        # AND limit snapshots to process to ones that are automated only
        # AND exclude automated snapshots marked for permanent retention
    filters = [
        { 'Name': 'tag:CreatedOn', 'Values': [today_fmt] },
        { 'Name': 'tag:Type', 'Values': ['Automated'] },
    ]
    snapshot_response = ec.describe_snapshots(OwnerIds=account_ids, Filters=filters)

    for snap in snapshot_response['Snapshots']:
        
        CreatedOn = ""
        Type = "Automated"
        DeleteOn = ""

        for tag in snap['Tags']:
            if tag['Key'] == 'CreatedOn':
                CreatedOn = tag['Value']
                
            if tag['Key'] == 'Type':
                Type = tag['Value']
                
            if tag['Key'] == 'DeleteOn':
                DeleteOn = tag['Value']

        print "\tCopying %s created from %s of [%s] to %s" % ( snap['SnapshotId'], source_region, snap['Description'], copy_region )

        addl_ec = boto3.client('ec2', region_name=copy_region)

        addl_snap = addl_ec.copy_snapshot(
            SourceRegion=source_region,
            SourceSnapshotId=snap['SnapshotId'],
            Description=snap['Description'],
            DestinationRegion=copy_region
        )

        addl_ec.create_tags(
            Resources=[addl_snap['SnapshotId']],
            Tags=[
                { 'Key': 'CreatedOn', 'Value': CreatedOn },
                { 'Key': 'DeleteOn', 'Value': DeleteOn },
                { 'Key': 'Type', 'Value': Type },
            ]
        )

    delete_on = datetime.date.today().strftime('%Y-%m-%d')
        # limit snapshots to process to ones marked for deletion on this day
        # AND limit snapshots to process to ones that are automated only
        # AND exclude automated snapshots marked for permanent retention
    filters = [
        { 'Name': 'tag:DeleteOn', 'Values': [delete_on] },
        { 'Name': 'tag:Type', 'Values': ['Automated'] },
    ]
    snapshot_response = addl_ec.describe_snapshots(OwnerIds=account_ids, Filters=filters)

    for snap in snapshot_response['Snapshots']:
        skipping_this_one = False
        
        for tag in snap['Tags']:
            if tag['Key'] == 'KeepForever':
                skipping_this_one = True
                continue

        if skipping_this_one == True:
            print "\tSkipping snapshot %s (marked KeepForever)" % snap['SnapshotId']
            # do nothing else
        else:
            print "\tDeleting snapshot %s" % snap['SnapshotId']
            addl_ec.delete_snapshot(SnapshotId=snap['SnapshotId'])
