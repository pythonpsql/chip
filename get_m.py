#! /usr/bin/env python3
import os
import common_functions as cf
import datetime
import time

get_date = cf.prompt_("Select: ", ['today', 'yesterday'], unique_ = "existing")
if get_date == 'yesterday':
    yesterday = datetime.date.today() - datetime.timedelta(1)
elif get_date == 'today':
    yesterday = datetime.date.today()
print(yesterday.strftime('%Y.%m.%d'))
folder_name = str(yesterday).replace("-", ".") + ".7z"
remote_folder = "db/" +  folder_name
dropbox_command = "cd ~/git_clones/Dropbox-Uploader/ && ./dropbox_uploader.sh download " +  remote_folder
os.system(dropbox_command)
time.sleep(2)
local_folder = "~/git_clones/Dropbox-Uploader/" +  folder_name
print(local_folder)
unzip_command = "7z x " + local_folder
os.system(unzip_command)
