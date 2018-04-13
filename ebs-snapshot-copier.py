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

	# open a client connection to the destination 
	addl_ec = boto3.client('ec2', region_name=copy_region)
	addl_snap = addl_ec.copy_snapshot(
	    SourceRegion=source_region,
	    SourceSnapshotId=snap['SnapshotId'],
	    Description=snap['Description'],
	    DestinationRegion=copy_region
	)

	if (addl_snap):
	    print "\t\tSnapshot copy %s created in %s of [%s] from %s" % ( addl_snap['SnapshotId'], copy_region, snap['Description'], source_region )
	# TODO: copy tags over
	#to_tag[retention_days].append(addl_snap['SnapshotId'])
	


