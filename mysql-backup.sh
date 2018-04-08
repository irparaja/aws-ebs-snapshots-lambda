#!/bin/bash

# You need to give in the USER and OUTPUT folder below.
# Then, use the following command to securely setup auto login for the script (you will be prompted for the password):
# mysql_config_editor set --login-path=/home/ubuntu --host=localhost --user=root --password

# Check the mysql login is configured:
# mysql_config_editor print --all

# Setup a cron job using the standard user, e.g. crontab -e
# 32 0 * * * /home/ubuntu/mysql-backup.sh

# To uncompress the SQL dumps use the command line tool, e.g. gunzip <filename.sql.gz>

USER="root"

OUTPUT="/home/ubuntu/dbs"

rm $OUTPUT/*gz

databases=`mysql --login-path=$OUTPUT  -e "SHOW DATABASES;" | tr -d "| " | grep -v Database`

for db in $databases; do
    if [[ "$db" != "information_schema" ]] && [[ "$db" != "performance_schema" ]] && [[ "$db" != "mysql" ]] && [[ "$db" != _* ]] ; then
        echo "Dumping database: $db"
        mysqldump --login-path=$OUTPUT --databases $db >  $OUTPUT/`date +%Y%m%d`.$db.sql
        gzip $OUTPUT/`date +%Y%m%d`.$db.sql
    fi
done

