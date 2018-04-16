#!/bin/bash

# Scheduled database dumps to ensure you have a clean backup.

# The --lock-tables flag is used and will locks all tables for the duration of the mysqldump, it a bad option 
# to use on a live environment, but, in the early hours of the morning it should not be an isse. 

# Run following command after creating the file
# chmod + mariadb-backup.sh

# Setup a cron job using the root user, e.g. sudo crontab -e
# 32 0 * * * /home/ubuntu/mariadb-backup.sh

# To uncompress the SQL dumps use the command line tool, e.g. gunzip <filename.sql.gz>

# Note MariaDB doesn't support mysql_config_editor like MySQL :D

OUTPUT="/home/ubuntu/dbs"

rm $OUTPUT/*gz

databases=`mysql -u root -e "SHOW DATABASES;" | tr -d "| " | grep -v Database`

for db in $databases; do
    if [[ "$db" != "information_schema" ]] && [[ "$db" != "performance_schema" ]] && [[ "$db" != "mysql" ]] && [[ "$db" != _* ]] ; then
        echo "Dumping database: $db"
        mysqldump -u root --lock-tables --databases $db >  $OUTPUT/`date +%Y%m%d`.$db.sql
        gzip $OUTPUT/`date +%Y%m%d`.$db.sql
    fi
done

