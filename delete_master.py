import os
import sys
import common_functions as cf
import hurry.filesize
import time

def size_print(file_):
    time.sleep(2)
    get_size_cmd = "stat --printf='%s' " + file_
    print(get_size_cmd)
    get_size = os.system(get_size_cmd)
    print("get_size is {}".format(get_size))
    print("Size: {}".format(hurry.filesize.size(get_size)))

def backup_master():
    backup_folder = os.path.join(cf.project_dir, "backup")
    temp_name = cf.get_current_timestamp().replace("/", "")
    temp_name = temp_name.replace(":", "")
    temp_name = temp_name.replace(" ", "_")
    master_backup_file_name = "master_schema_" + temp_name + ".pgsql"
    master_backup_file = os.path.join(backup_folder, master_backup_file_name)
    backup_command = "pg_dump -Fc -U dba_tovak -d chip -h localhost -n master > " + master_backup_file
    print(master_backup_file)
    os.system(backup_command)
    size_print(master_backup_file)
    compress_file_name = master_backup_file + ".7z"
    compress_ = "7z a " + compress_file_name + " " + master_backup_file +  " -p"
    print(compress_)
    confirm_ = cf.prompt_("Do you want to run the command? (y/n): ", ['y', 'n'], default_='y', unique_='existing')
    if confirm_ == 'n': return None
    os.system(compress_)
    size_print(compress_file_name)
    remote_folder = '/db/master/'
    dropbox_command = "cd ~/git_clones/Dropbox-Uploader/ && ./dropbox_uploader.sh upload " + compress_file_name + " " + remote_folder
    print(dropbox_command)
    confirm_ = cf.prompt_("Do you want to run the command? (y/n): ", ['y', 'n'], default_='y', unique_='existing')
    if confirm_ == 'n': return None
    os.system(dropbox_command)

def delete_master():
    delete_command = "psql -U dba_tovak -d chip -h localhost -c 'drop schema master cascade'"
    confirm_ = cf.prompt_("Do you want to run the command? (y/n): ", ['y', 'n'], default_='y', unique_='existing')
    if confirm_ == 'n': return None
    os.system(delete_command)

def dropbox(master_backup_file):
    remote_folder = '/db/'
    print('master_backup_file: {}'.format(master_backup_file))
    dropbox_backup = cf.prompt_("Do you want to backup to Dropbox? (y/n): ", ['y', 'n'], default_='y', unique_='existing')
    if dropbox_backup == 'n': return None
    compress_file_name = master_backup_file + ".7z"
    compress_ = "7z a " + compress_file_name + " " + master_backup_file +  " -p"
    print(compress_)
    confirm_ = cf.prompt_("Do you want to run the command? (y/n): ", ['y', 'n'], default_='y', unique_='existing')
    if confirm_ == 'n': return None
    os.system(compress_)
    dropbox_command = "cd ~/git_clones/Dropbox-Uploader/ && ./dropbox_uploader.sh upload " + compress_file_name + " " + remote_folder
    print(dropbox_command)
    confirm_ = cf.prompt_("Do you want to run the command? (y/n): ", ['y', 'n'], default_='y', unique_='existing')
    if confirm_ == 'n': return None
    os.system(dropbox_command)

if __name__ == "__main__":
    backup_master()

