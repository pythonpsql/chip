import common_functions as cf
# file_ = "/home/tovak/env/my_env/chips_stack/backup/today.rtf"
# file_ = "/home/tovak/env/my_env/lib/python3.5/site_packages/pgadmin4"

# set datestyle = 'ISO, DMY';
# copy temp_vendor_product (product_name, vendor_name, timestamp_, rate, discount) from '/home/tovak/env/my_env/chips_stack/backup/from_vpr.csv' with (format csv);
import os
def dropbox(local_file, **kwargs):
    project_dir = os.path.dirname(os.path.abspath(__file__))
    remote_folder = kwargs.get('remote_folder', '')
    remote_folder = '/' + remote_folder
    print('local_file: {}'.format(local_file))
    dropbox_backup = cf.prompt_("Do you want to backup to Dropbox? (y/n): ", ['y', 'n'], default_='y', unique_='existing')
    if dropbox_backup == 'n': return None
    compress_file_name = local_file + ".7z"

    compress_ = "7z a " + compress_file_name + " " + local_file +  " -p"
    print(compress_)
    confirm_ = cf.prompt_("Do you want to run the command? (y/n): ", ['y', 'n'], default_='y', unique_='existing')
    if confirm_ == 'n': return None
    os.system(compress_)
    temp_file= os.path.join(project_dir, compress_file_name)
    dropbox_command = "cd ~/git_clones/Dropbox-Uploader/ && ./dropbox_uploader.sh upload " + temp_file + " " + remote_folder
    print(dropbox_command)
    confirm_ = cf.prompt_("Do you want to run the command? (y/n): ", ['y', 'n'], default_='y', unique_='existing')
    if confirm_ == 'n': return None
    os.system(dropbox_command)

if __name__ == "__main__":
    import sys

    f = sys.argv[1]
    if os.path.exists(f):
        print(f)
    dropbox(f)
