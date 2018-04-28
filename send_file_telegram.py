import os

def os_(string_):
    print("running bash command: {}".format(string_))
    os.system(string_)

def send_file_telegram(file_path):
    os_('telegram-cli -W -e "send_file "' + file_path)

# os_('date')
# os_('telegram-cli -W -e "msg Neha test"')
# send_file_telegram("/home/tovak/env/my_env/chip/temp_/invoices/24495.pdf")
def send_msg_telegram(message_, me=True):
    import custom.custom_data as cd
    c1 = cd.contact1
    message_ = '\"send_file ' + c1 +  " " +  "\'"+  "\'" + '\"'
    # message_ = 'msg ' + c1 +  " " +  "\'"+ message_ + "\'"
    print(message_)

send_msg_telegram('some\nthis', me=True)
