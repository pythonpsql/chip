from database import Database, CursorFromConnectionFromPool as conn
from prompt_toolkit.styles import Style
from psycopg2 import sql
from reportlab.lib import pagesizes
from prettytable import PrettyTable
from fuzzyfinder import fuzzyfinder as ff
import common_functions as cf
import owner
import product
import sys
import os
import master
from decimal import Decimal
import required.custom_data as custom_data

name_ = 'Barrel Nipple'
size = str(100)
name_size = name_ + " " + size
name_like = name_size + " " + "%" # to avoid 150 while looking for 15, a space is must

Database.initialise(database='chip', host='localhost', user='dba_tovak')

with conn() as cursor:
    cursor.execute("select cost from product where name = %s", (name_size,))
    cost = cursor.fetchone()[0]
    print(cost)

with conn() as cursor:
    cursor.execute("select name, cost from product where name like %s", (name_like,))
    result = cursor.fetchall()

for a in result:
    product_name = a[0]
    sub_size = product_name.split("x")[1]
    # print(sub_size)
    cost_sub_size = (Decimal(cost/12)*Decimal(sub_size)).quantize(Decimal("1.00"))
    # print(cost_sub_size)
    with conn() as cursor:
        cursor.execute("update product set cost = %s where name = %s", (cost_sub_size, product_name))
