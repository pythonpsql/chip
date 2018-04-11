
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

# update product set cost = round(product_pricelist.value*0.5,2) from product_pricelist where product_pricelist.id_product = product.id and product_pricelist.id_pricelist=4;
# update product set cost = round(product_pricelist.value*0.5,2) from product_pricelist where product_pricelist.id_product = product.id and product_pricelist.id_pricelist=1;
# also repeat for id_pricelistr 2 and 3
# update product set cost = (select cost from product where name = 'Socket 50') where name like 'Red. Socket 50%')
name_ = 'Extension 25'
sizes = ['40', '50', '65', '80', '100', '125', '150']
name_list = []
for a in sizes:
    name_list.append("Extension " + a)
print(name_list)

Database.initialise(database='chip', host='localhost', user='dba_tovak')

with conn() as cursor:
    cursor.execute("select cost from product where name = %s", (name_,))
    cost = cursor.fetchone()[0]
    print(cost)


for product_name in name_list:
    sub_size = product_name.split("Extension ")[1]
    # print(sub_size)
    size_dict = {
            '40': 1.50,
            '50': 2,
            '65': 2.50,
            '80': 3,
            '100': 4,
            '125': 5,
            '150': 6
            }
    cost_sub_size = Decimal(Decimal(cost)*Decimal(size_dict[sub_size])).quantize(Decimal("1.00"))
    print(sub_size)
    print(cost_sub_size)
    with conn() as cursor:
        cursor.execute("update product set cost = %s where name = %s", (cost_sub_size, product_name))

for a in name_list:
    with conn() as cursor:
        cursor.execute("select name, cost from product where name like %s", (a,))
        result = cursor.fetchall()
        print(result)
