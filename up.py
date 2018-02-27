import master

file_ = "/home/tovak/env/my_env/chips_stack/backup/today.rtf"
# file_ = "/home/tovak/env/my_env/lib/python3.5/site_packages/pgadmin4"

# set datestyle = 'ISO, DMY';
# copy temp_vendor_product (product_name, vendor_name, timestamp_, rate, discount) from '/home/tovak/env/my_env/chips_stack/backup/from_vpr.csv' with (format csv);

master.dropbox(file_)
