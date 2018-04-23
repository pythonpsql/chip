#! /usr/bin/env python3
import os
import common_functions as cf
import datetime
import time
import glob


def get_date():
    today = datetime.date.today()
    get_date = cf.prompt_("Select: ", ['today', 'yesterday', 'other'], unique_ = "existing")
    if get_date == 'yesterday':
        the_date = today - datetime.timedelta(1)
    elif get_date == 'today':
        the_date = today
    elif get_date == 'other':
        while True:
            the_date = cf.prompt_("Enter date: ", [], default_=str(today))
            confirm_ = cf.prompt_("Confirm date {} (y/n): ".format(the_date), [])
            if confirm_ == "y":
                break
    print(the_date)
    return the_date

def get_date_separated_by_dot(the_date):
    return str(the_date).replace("-", ".")

def get_file_name(date_by_dot):
    return date_by_dot + ".7z"

def download_file(remote_folder_name, remote_file):
    print("Downloading {} ...".format(remote_file))
    remote_file_path = remote_folder_name + "/" + remote_file
    dropbox_command = "cd ~/git_clones/Dropbox-Uploader/ && ./dropbox_uploader.sh download " +  remote_file_path
    os.system(dropbox_command)

def extract_file(remote_file):
    local_folder = "~/git_clones/Dropbox-Uploader/" + remote_file
    print("Extracting {} ...".format(local_folder))
    unzip_command = "7z x " + local_folder + " -obackup/"
    os.system(unzip_command)

def backup():
    backup_command = "pg_dump -Fc -U dba_tovak -d chip -h localhost > backup/chip_full_db_backup.pgsql"
    os.system(backup_command)
    print('Backup successfully completed')

def delete_public():
    delete_command = "psql -U dba_tovak -d chip -h localhost -c 'drop schema public cascade'"
    print(delete_command)
    confirm_ = input("Do you want to execute the above command? (y/n)").strip().lower()
    if confirm_ == "y":
        os.system(delete_command)
    else:
        print('You canceled. No changes were made')

def create_empty_public():
    create_command = "psql -U dba_tovak -d chip -h localhost -c 'create schema public'"
    print("Creating empty 'public'")
    os.system(create_command)

def delete_master():
    delete_command = "psql -U dba_tovak -d chip -h localhost -c 'drop schema master cascade'"
    print(delete_command)
    confirm_ = input("Do you want to execute the above command? (y/n)").strip().lower()
    if confirm_ == "y":
        os.system(delete_command)
    else:
        print('You canceled. No changes were made')

def select_file(the_date, type_):
    assert type_ in ['public', 'master']
    file_list = []
    for name in glob.glob('backup/' + the_date + '/' + type_ + '_*'):
        file_list.append(name)
    print(file_list)
    return cf.prompt_("select file: ", file_list, unique_="existing")


def restore_file(file_):
    restore_command = "pg_restore -U dba_tovak -h localhost -d chip " + file_
    print(restore_command)
    confirm_ = input("Do you want to execute the above command? (y/n)").strip().lower()
    if confirm_ == "y":
        os.system(restore_command)
        print("{} restored".format(file_))
    else:
        print('You canceled. No changes were made')


if __name__ == "__main__":
    remote_folder_name = "db"
    the_date = get_date()
    date_by_dot = get_date_separated_by_dot(the_date)
    remote_file = get_file_name(date_by_dot)
    download_file(remote_folder_name, remote_file)
    time.sleep(2)
    extract_file(remote_file)
    backup()
    delete_master()
    master_file = select_file(date_by_dot, type_='master')
    restore_file(master_file)
    delete_public()
    create_empty_public()
    public_file = select_file(date_by_dot, type_='public')
    restore_file(public_file)
