
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


Database.initialise(database='chip', host='localhost', user='dba_tovak')

def get_a_product(product_name):
    with conn() as cursor:
        sq = "select id, name, cost from product where name = %s"
        cursor.execute(sq, (product_name,))
        return cursor.fetchone()

def get_all_products():
    with conn() as cursor:
        sq = "select id, name, cost from product"
        cursor.execute(sq)
        return  cursor.fetchall()
    # cf.pretty_(['id', 'name', 'cost'], result)

    # print(result)
def set_product_cost(a):
    cost_before_discount = cf.prompt_("Enter cost for {}: ".format(a[1]), [], default_=str(a[2]), empty_="yes")
    if cost_before_discount == "None":
        cost_before_discount = None
    if cost_before_discount:
        discount = cf.prompt_("Enter discount for {}: ".format(a[1]), [], default_=str(0), empty_="yes")
        if discount:
            discount = float(discount)
            cost = (Decimal(cost_before_discount) * Decimal(1 - discount/100)).quantize(Decimal("1.00"))
        else:
            cost = cost_before_discount
        transport_cost = cf.prompt_("Enter Tranport Cost for {}: ".format(a[1]), [], default_=str(0), empty_="yes")
        timestamp_ = cf.get_current_timestamp()
        final_cost = (Decimal(cost) + Decimal(transport_cost)).quantize(Decimal("1.00"))
        with conn() as cursor:
            cursor.execute("update product set (purchase_cost, cost, timestamp_) = (%s, %s, %s) where id = %s returning name, cost, timestamp_", (cost, timestamp_, a[0]))
            result = cursor.fetchall()
        cf.pretty_(['name', 'cost', 'final_cost', 'timestamp_'], result)

# product.get_buy_rate(invoice_detail_.product_name)
if __name__ == "__main__":
    while True:
        product_name = cf.prompt_("Choose Product or 'a' for all: ", cf.get_completer_list("name", "product"))
        if product_name == "a":
            result = get_all_products()
            for a in result:
                print(a)
                product.get_buy_rate(a[1])
                set_product_cost(a)
        else:
            a = get_a_product(product_name)
            product.get_buy_rate(product_name)
            set_product_cost(a)


