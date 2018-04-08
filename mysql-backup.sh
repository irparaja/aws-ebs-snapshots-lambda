#!/bin/bash

# Use the following command to securely setup login for your root user:
# mysql_config_editor set --login-path=/home/ubuntu --host=localhost --user=root --password

# Check the mysql login is setup
# mysql_config_editor print --all

# Setup cron job using the standard user
# 32 0 * * * /home/ubuntu/mysql-backup.sh

USER="root"

OUTPUT="/home/ubuntu/dbs"

rm "$OUTPUTDIR/*gz" > /dev/null 2>&1

databases=`mysql --login-path=$OUTPUT  -e "SHOW DATABASES;" | tr -d "| " | grep -v Database`

for db in $databases; do
    if [[ "$db" != "information_schema" ]] && [[ "$db" != "performance_schema" ]] && [[ "$db" != "mysql" ]] && [[ "$db" != _* ]] ; then
        echo "Dumping database: $db"
        mysqldump --login-path=$OUTPUT --databases $db >  $OUTPUT/`date +%Y%m%d`.$db.sql
        gzip $OUTPUT/`date +%Y%m%d`.$db.sql
    fi
done

