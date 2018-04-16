## Overview

This is for managing AWS EC2 EBS volume snapshots. It consists of a "snapshot creator", a "snapshot manager" for deleting old archives and a "snapshot copier" that moves them to another region. 

## Functionality:

- Automatic snapshots (on whatever schedule you prefer)
- Automated expiration of old snapshots
- Ability to configure retention period on a per EC2 instance basis (applying to all volumes attached to said instance)
- Ability to manually tag individual snapshots to be kept indefinitely (regardless of instance retention configuration)
- Does not require a job/management instance; no resources to provision to run snapshot jobs (leverages AWS Lambda)
- Allows you to make cross-region backups (for disaster recovery)

## Implementation Details

A set of three Python (v2.7) based functions are provided to run in AWS Lambda and create snapshot backups and cross-region copies. They are intended to be run on a regular basis (i.e. daily). You should schedule this in AWS CloudWatch under Events. 

AWS Lambda requires access to your resources. When creating your first function, you will create an execution role and then can copy paste in the policy permissions found in this repository.  

Backup configuration is done through tags you place on EC2s. Simply add a tag 'Backup' with the value 'Yes' on instances that should have their volumes backed up.  

There are also two shell scripts for dumping MySQL and MariaDB databases. The idea of exporting the databases is improved consistency, snapshots start and end after some time. If you have large databases and dependant on your schema types, you might want to skip table locking.  

## Tags You Can Use On EC2s

Retention: Number of days backups should be kept for.  
Backup: The script is looking for keyword Yes, then it will create a snapshot.  

## Tags The Snapshots Are Given Automatically

CreatedOn: The date it was created. Required to make cross-region backups.  
DeleteOn: The date the snapshot should be deleted.  
Type: With the keyword 'Automated'.   

## Tags You Can Use On Snapshots

KeepForever: With any value will keep the snapshot from being deleted.

## Files:

Each file implements a single AWS Lambda function.

- ebs-snapshot-creator.py
- ebs-snapshot-manager.py
- ebs-snapshot-cross-region.py

## Related:

This solution was forked from joshtrichards/aws-ebs-snapshots-lambda and was extended. It is based on code originally posted by Ryan S. Brown in [Scheduling EBS Snapshots - Part I](https://serverlesscode.com/post/lambda-schedule-ebs-snapshot-backups/) and [Part II](https://serverlesscode.com/post/lambda-schedule-ebs-snapshot-backups-2/). The main change is that I created the cross-region script, to achieve that I 
introduced a new CreatedOn tag. 

- [AWS auto snapshot script by Joe Richards](https://github.com/viyh/aws-scripts/blob/master/lambda_autosnap.py)
- [AWS EBS Backup Job Run by Lambda by Chris Machler](http://www.evergreenitco.com/evergreenit-blog/2016/4/19/aws-ebs-backup-job-run-by-lambda)
- [DevOps Backup in Amazon EC2](https://medium.com/aws-activate-startup-blog/devops-backup-in-amazon-ec2-190c6fcce41b#.hyo4nyqur)
- [AWS volume snapshots across multiple regions](https://mattyboy.net/general/aws-volume-snapshots-across-multiple-regions/)
- [EBS Snapshots: Crash-Consistent Vs. Application-Consistent](http://www.n2ws.com/blog/ebs-snapshots-crash-consistent-vs-application-consistent.html)
- [N2WS CPM](http://www.n2ws.com/products-services/pricing-registration.html)
- [lambda-expire-snapshots](https://github.com/RideAmigosCorp/lambda-expire-snapshots)
- [Rackspace's Snappy for EBS Snapshots](https://github.com/rackerlabs/ebs_snapper) & (http://blog.rackspace.com/automate-ebs-snapshots-with-snapper)

## Other Relevant Resources (especially if you're going to customize):

- [Boto 3 Docs for EC2](https://boto3.readthedocs.io/en/latest/reference/services/ec2.html)

