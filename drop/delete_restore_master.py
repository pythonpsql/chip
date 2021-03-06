import sys
# print('This script has been incorporated in get_m.py and is not reduntant')
# sys.exit()
import os
import sys


f = sys.argv[1]
if os.path.exists(f):
    print("Backing up 'chip'")
    backup_command = "pg_dump -Fc -U dba_tovak -d chip -h localhost > backup/chip_full_db_backup.pgsql"
    os.system(backup_command)
    # sys.exit()
    print(f)

    delete_command = "psql -U dba_tovak -d chip -h localhost -c 'drop schema master cascade'"

    print(delete_command)
    confirm_ = input("Do you want to execute the above command? (y/n)").strip().lower()
    if confirm_ == "y":
        os.system(delete_command)
        restore_command = "pg_restore -U dba_tovak -h localhost -d chip " + f
        print(restore_command)
        os.system(restore_command)
        print("db restored")
    else:
        print('You canceled. No changes were made')
else:
    print("You need to specify a valid file path to restore data from")
    print("e.g. python delete_restore_db.py <filepath>")
