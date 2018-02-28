mkdir drop
mv delete_* drop
mkdir required
mv custom_data.py required/
mkdir temp_
mv invoices gst_invoices temp_
mv fonts/ required/
mv not_main_project/ transfer_from_old/ required/
rm transfer_public_to_master.py
mv assign_gst_name_customer.py required/
# fix pause button script


# update .gitignore
# __pycache__
# not_main_project/*
# required/*
# temp_/*
# transfer_from_old/*
# trace_results/*
# *.txt
# trace_*
# invoices/*
# fonts/*
# unused/*
# auto-suggest/*
# htmlcov/*
# __init__.py
# sql/*
# backup/*
# tags
# *.log
# *.pgsql
# *.pyc
# custom_data.py
# gst_invoices/*
# fonts/some_pic.png
# *.csv
# *.sql
