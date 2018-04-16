

from database import Database, CursorFromConnectionFromPool as conn
from psycopg2 import sql
from prettytable import PrettyTable
from fuzzyfinder import fuzzyfinder as ff
import common_functions as cf
import owner
import product
import sys
import os
import master
from decimal import Decimal


Database.initialise(database='chip', host='localhost', user='dba_tovak')

def update_gst_opening_balance(type_):
    owner_ = cf.prompt_("Enter Owner Name: ", cf.get_completer_list("nickname", type_.lower()), unique_="existing")
    balance_ = cf.prompt_("Enter amount: ", [])
    with conn() as cursor:
        cursor.execute("update {} set gst_opening_balance = %s where nickname = %s returning name, gst_opening_balance".format(type_), (balance_, owner_))
        result = cursor.fetchall()
    cf.pretty_(['name', 'balance'], result)


def update_opening_balance(type_):
    owner_ = cf.prompt_("Enter Owner Name: ", cf.get_completer_list("nickname", type_.lower()), unique_="existing")
    balance_ = cf.prompt_("Enter amount: ", [])
    with conn() as cursor:
        cursor.execute("update {} set opening_balance = %s where nickname = %s returning name, opening_balance".format("master."+type_), (balance_, owner_))
        result = cursor.fetchall()
    cf.pretty_(['name', 'balance'], result)

if __name__ == "__main__":
    Database.initialise(database='chip', host='localhost', user='dba_tovak')
    while True:
        type_ = cf.prompt_("Enter Owner Type: ", ["Customer", "Vendor"], unique_="existing")
        opening_bal_type = cf.prompt_("Enter balance type: ", ["gst", "other"], unique_="existing")
        if opening_bal_type == "gst":
            update_gst_opening_balance(type_)
        elif opening_bal_type == "other":
            update_opening_balance(type_)

