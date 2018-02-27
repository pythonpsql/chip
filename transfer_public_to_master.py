import os
import sys

f = sys.argv[1]
if os.path.exists(f):
    print(f)
    # delete public schema of chip
    drop_command = "psql -U dba_tovak -d chip -h localhost -c 'drop schema public cascade'"
    os.system(drop_command)
    print('Deleted schema public of chip db')

    # create public schema in chip
    create_public = "psql -U dba_tovak -d chip -h localhost -c 'create schema public'"
    os.system(create_public)
    print('Created schema public in chip db')

    # restore public from shop
    restore_public = "pg_restore -d chip -h localhost -U dba_tovak " + f
    os.system(restore_public)
    print('Restored schema public from given file')



