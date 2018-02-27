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

confirm_ = cf.prompt_("This", ['abc','acb', 'b'])
# Database.initialise(database='chip', host='localhost', user='dba_tovak')

# master.backup(drop_=True)
# a = Decimal(5.50)
# print(Decimal(a.quantize(Decimal("1"))))
# master.dropbox("~/.pgpass")
# import invoice


# urlparse.uses_netloc.append("postgres")
# url = urlparse.urlparse(os.environ["postgres://fdtktzvp:IO0OjVWeKhITpOSGgbAgFCBIxBTJqrfC@baasu.db.elephantsql.com:5432/fdtktzvp"])

# with conn() as cursor:
#     cursor.execute(sql.SQL("select max(id) from {} where id_owner = %s").format(invoice_table), (id_owner, ))
#     last_invoice_id = cursor.fetchone()[0]
# print(last_invoice_id)
# with conn() as cursor:
#     cursor.execute(sql.SQL("select max(id) from {} where id_owner = %s").format(invoice_table), (id_owner, ))
#     last_invoice_id = cursor.fetchone()[0]
# print(last_invoice_id)

# sq = "select name, place, sum(invoice_amount)-sum(money_amount)+master.customer.opening_balance as balance from master.sale_ledger_view join master.customer on master.customer.id = master.sale_ledger_view.id_owner where id = 13705 group by name, place, customer.opening_balance order by balance desc "
# sq = "select invoice_amount, money_amount, invoice_amount-money_amount from master.sale_ledger_view where id_owner = 13705"
# all_invoice_amount = "select sum(amount) from master.sale_transaction where id_voucher is null and id_owner = %s"
# all_receipt_amount = "select sum(amount) from master.sale_transaction where id_invoice is null and id_owner = %s"
# opening_balance = "select opening_balance from master.customer where id = %s"
# id_ = 13705
# with conn() as cursor:
#     cursor.execute(all_invoice_amount, (id_, ))
#     ia = cursor.fetchone()[0]
#     if ia is None: ia=0
# with conn() as cursor:
#     cursor.execute(all_receipt_amount, (id_,))
#     ra = cursor.fetchone()[0]
#     if ra is None: ra =0
# with conn() as cursor:
#     cursor.execute(opening_balance, (id_, ))
#     op = cursor.fetchone()[0]
#     if op is None: op = 0
# print("Balance = {}".format(ia+op-ra))

# list_ = ["a", "b", "c"]
# a = list_[-1]
# print(a)

# pt = PrettyTable(['a', 'b'])
# pt.add_row(['this', ''])
# print(pt)

# name_list = cf.get_completer_list("name", "customer")
# print(name_list)

# s = ff('shree', name_list)
# print(list(s))

# class some():
#     pass

# some2 = some()
# some2.this = "hwat"
# print(some2.this)
# style = Style.from_dict({
#     '': '#7CFC00',
#     'title': '#00aa00'
#     })

# prompt_fragments = [
#         ('class:title', 'Enter input: ')
#         ]
# input_ = cf.prompt(prompt_fragments, completer=[], style=style)
