#! /usr/bin/env python

from database import Database, CursorFromConnectionFromPool as conn
from prettytable import PrettyTable
import command_functions as cm
import common_functions as cf
import invoice
import money
import owner
import product
import sale_report
import master
import transaction as tr
import pricelist_functions as plf


def get_input():
    while True:
        input_ = cf.prompt_dict("Enter input: ", cm.commands_dict, )
        if input_:
            return {"arg1": input_}

def chip():
    cf.clear_screen(msg="Chip")
    # input_ = {"arg1": 'plm'}
    input_ = None
    while True:
        cf.log_("start input_ is {}".format(input_))
        if not input_:
            input_ = get_input()
            cf.log_("input_.get('arg1') is {}".format(input_.get('arg1')))
        elif input_ == "back":
            input_ = None
            continue
        elif input_ == "quit":
            cf.log_("You quit")
            import sys
            sys.exit()
            break
        elif input_.get("arg1") == "slms":
            tr.view_summary()
            input_ = None
            continue
        elif input_.get("arg1") == "slmp":
            place = cf.prompt_("Enter place: ", cf.get_completer_list("place", "customer"), existing_="yes")
            tr.get_customer_balance(place=place)
            input_ = None
            continue
        elif input_.get("arg1") == "slm1":
            tr.get_customer_balance()
            input_ = None
            continue
        elif input_.get("arg1") == "test":
            # tr.view("sale_transaction")
            # tr.view("purchase_transaction")
            # tr.view_by_nickname("sale_transaction", "Kishor Light House")
            # master.add_saved("sale_invoice")
            input_ = None
            continue
        elif input_.get('arg1') in ['saved', 'unsaved']:
            if input_.get('arg1') == 'unsaved':
                sq = 'select id, owner_name, owner_place, amount_after_freight from sale_invoice where id not in (select id_invoice from sale_transaction where id_invoice is not null) and gst_invoice_no is null'
                sq_purchase = 'select id, owner_name, owner_place, amount_after_freight from purchase_invoice where id not in (select id_invoice from purchase_transaction where id_invoice is not null) and gst_invoice_no is null'
            elif input_.get('arg1') == 'saved':
                sq = 'select id, owner_name, owner_place, amount_after_freight from sale_invoice where id in (select id_invoice from sale_transaction where id_invoice is not null) and gst_invoice_no is null'
                sq_purchase = 'select id, owner_name, owner_place, amount_after_freight from purchase_invoice where id in (select id_invoice from purchase_transaction where id_invoice is not null) and gst_invoice_no is null'
            with conn() as cursor:
                cursor.execute(sq)
                result = cursor.fetchall()
            with conn() as cursor:
                cursor.execute(sq_purchase)
                result_purchase =  cursor.fetchall()
            for a_result in [result, result_purchase]:
                pt = PrettyTable(['id', 'name', 'place', 'amount'])
                pt.align['amount'] = 'r'
                for a in a_result:
                    pt.add_row(a)
                print(pt)
                print("Count: {}".format(len(a_result)))
            input_ = None
            continue

        elif input_.get("arg1") == "invoice_by_id":
            invoice_type = input_.get("arg3")
            invoice_id = input_.get("arg2")
            invoice_ = invoice.get_existing_invoice(invoice_type, invoice_id)
            invoice_.view_invoice_details(invoice_.fetch_invoice_details())
            input_ = cm.command_loop(invoice_)
            continue
        elif input_.get("arg1") == "todo":
            input_ = None
            continue
        elif input_.get("arg1") == "gbr":
            product_name = cf.prompt_("Enter product name: ", cf.get_completer_list("name", "product"), unique_="existing")
            product.get_buy_rate(product_name)
            input_ = None
            continue
        elif input_.get("arg1") == "sl":
            input_ = tr.ledger_operations("sale_transaction")
            continue
        elif input_.get("arg1") == "sbm":
            input_ = tr.get_a_balance("sale_transaction", master_=True)
            continue
        elif input_.get("arg1") == "sbma":
            input_ = tr.get_all_balances("sale_transaction", master_=True)
            continue
        elif input_.get("arg1") == "slg":
            input_ = tr.ledger_operations("sale_transaction", gst_=True)
            continue
        elif input_.get("arg1") == "slm":
            input_ = tr.ledger_operations("sale_transaction", master_="yes")
            continue
        elif input_.get("arg1") == "slmd":
            input_ = tr.ledger_operations("sale_transaction", master_="yes", date_='yes')
            continue
        elif input_.get("arg1") == "pl":
            input_ = tr.ledger_operations("purchase_transaction")
            continue
        elif input_.get("arg1") == "plg":
            input_ = tr.ledger_operations("purchase_transaction", gst_=True)
            continue
        elif input_.get("arg1") == "plm":
            input_ = tr.ledger_operations("purchase_transaction", master_="yes")
            continue
        elif input_.get("arg1") == "backup":
            print("This command is currently disabled")
            # master.export(only_backup=True)
            input_ = None
            continue
        elif input_.get("arg1") == "ex":
            confirm_ = cf.prompt_("Do you want to export? ", ['y', 'n'], unique_="existing")
            if confirm_ != 'y':
                print("You canceled. No changes were made.")
                input_ = None
                continue
            master.save_all_money()
            master.export()
            input_ = None
            continue
        elif input_.get("arg1") in ["rin", "ptin"]:
            if input_.get("arg1") == "rin":
                invoice_type = "receipt"
            elif input_.get("arg1") == "ptin":
                invoice_type = "payment"
            invoice_ = money.Money(invoice_type)
            input_ = None
            continue
        elif input_.get("arg1") in ["rie", "ptie"]:
            if input_.get("arg1") == "rie":
                invoice_type = "receipt"
            elif input_.get("arg1") == "ptie":
                invoice_type = "payment"
            invoice_id= owner.view(invoice_type, filter_type= "Search By Nickname")
            if invoice_id in ["quit", "back"]:
                input_ = {"arg1": input_}
                continue
            money_= money.Money(invoice_type, id_=invoice_id)
            money_.view_invoice_details(money_.fetch_invoice_details())
            while True:
                property_ = cf.prompt_("Enter property to edit/'delete' to delete record: ",money.sq_properties, empty_='yes')
                if property_ == "delete":
                    money_.delete_()
                    break
                if property_ in money.sq_properties:
                    money_.edit_property(property_)
                    continue
                if property_ in ["back", "quit"]:
                    break
            input_ = None
            continue
        elif input_.get("arg1")  in ["rip", "ptip"]:
            if input_.get("arg1") == "rip":
                invoice_type = "receipt"
                owner_type = "customer"
            elif input_.get("arg1") == "ptip":
                invoice_type = "payment"
                owner_type = "vendor"
            with conn() as cursor:
                cursor.execute("select r.date_, c.name, r.amount, r.medium, r.recipient, r.detail from {} as r join {} as c on c.id = r.id_owner where gst_invoice_no is null order by r.date_".format(invoice_type, owner_type))
                result = cursor.fetchall()
            column_list = ['Date', 'Name', 'Amount', 'Medium', 'Recipient', 'Detail']
            cf.pretty_table_multiple_rows(column_list, result)
            input_ = None
            continue
        elif input_.get("arg1") == "praa":
            input_ = product.set_property("abbr_name")
            if input_ in ["quit", "back"]:
                input_ = {"arg1": input_}
            continue
        elif input_.get("arg1") == "pra":
            input_ = product.set_property("abbr_name", by_name="yes")
            if input_ in ["quit", "back"]:
                input_ = {"arg1": input_}
            continue
        elif input_.get("arg1") == "prn":
            input_ = product.set_property("name", by_name="yes")
            if input_ in ["quit", "back"]:
                input_ = {"arg1": input_}
            continue
        elif input_.get("arg1") == "prc":
            while True:
                name = cf.prompt_("Enter New Product Name: ",cf.get_completer_list("name", "product"), unique_="yes")
                if name in ["quit", "back"]:
                    input_ = {"arg1": input_}
                    break
                input_ = product.create_product(name)
            continue
        elif input_.get("arg1") == "prde":
            input_ = cf.prompt_("Enter product name: ", cf.get_completer_list("name", "product"), unique_="existing")
            if input_ in ["quit", "back"]:
                input_ = {"arg1": input_}
                continue
            product.delete_product(input_)
            input_ = None
            continue
        elif input_.get("arg1") in ["sipn", "pipn", ","]:
            if input_.get("arg1") in ["sipn", ","]:
                invoice_type = "sale_invoice"
            elif input_.get("arg1") == "pipn":
                invoice_type = "purchase_invoice"
            invoice_id = owner.view(invoice_type, filter_type= "Search By Nickname")
            if invoice_id in ["quit", "back"]:
                input_ = {"arg1": input_}
                continue
            invoice_ = invoice.get_existing_invoice(invoice_type, invoice_id)
            invoice_.view_invoice_details(invoice_.fetch_invoice_details())
            input_ = cm.command_loop(invoice_)
            continue
        elif input_.get("arg1") in ["sip", "pip"]:
            if input_.get("arg1") == "sip":
                invoice_type = "sale_invoice"
            elif input_.get("arg1") == "pip":
                invoice_type = "purchase_invoice"
            invoice_id = owner.view(invoice_type)
            if invoice_id == "back":
                print("you chose to cancel")
                input_=None
                continue
            invoice_ = invoice.get_existing_invoice(invoice_type, invoice_id)
            invoice_.view_invoice_details(invoice_.fetch_invoice_details())
            input_ = cm.command_loop(invoice_)
            continue
        elif input_.get("arg1") in ["sil", "pil"]:
            if input_.get("arg1") == "sil":
                invoice_type = "sale_invoice"
            elif input_.get("arg1") == "pil":
                invoice_type = "purchase_invoice"
            last_invoice_id = owner.get_last_invoice_id(invoice_type)
            if not last_invoice_id:
                cf.log_("There are no previous invoices")
                input_ = None
                continue
            invoice_ = invoice.get_existing_invoice(invoice_type, last_invoice_id)
            print("reahced here0")
            invoice_.view_invoice_details(invoice_.fetch_invoice_details())
            print("reahced here")
            input_ = cm.command_loop(invoice_)
            continue
        elif input_.get("arg1") in ["cun", "ven"]:
            if input_.get("arg1") == "cun":
                invoice_type = "sale_invoice"
            elif input_.get("arg1") == "ven":
                invoice_type = "purchase_invoice"
            owner_type = cf.owner_type_d[invoice_type]
            id_ = owner.get_new_owner(owner_type)
            input_ = None
            continue
        elif input_.get("arg1") == "prn":
            input_ = cf.prompt_("Enter Product Name: ", cf.get_completer_list("name", "product"),  history_file='product_name.txt')
            if input_ in ["quit", "back"]:
                input_ = {"arg1": input_}
            else:
                input_ = product.Product.init_by_name(input_)
                input_ = None
            continue
        elif input_.get("arg1") in ["sin", "pin"]:
            if input_.get("arg1") == "sin":
                invoice_type = "sale_invoice"
            elif input_.get("arg1") == "pin":
                invoice_type = "purchase_invoice"
            invoice_ = invoice.get_new_invoice(invoice_type)
            input_  = cm.inside_invoice(invoice_)
            continue
        elif input_.get("arg1") == "plp":
            input_ = plf.assign_pricelist_to_product()
            if input_ in ["quit", "back"]:
                input_ = {"arg1": input_}
            continue
        elif input_.get("arg1") in ["cupln", "vepln"]:
            if input_.get("arg1") == "cupln":
                owner_type = "customer"
            elif input_.get("arg1") == "vepln":
                owner_type = "vendor"
            confirm_ = cf.prompt_("Change discount for: ", ['gst', 'non-gst'], unique_="existing")
            if confirm_ == "gst":
                gst_arg = True
            else:
                gst_arg = False
            plf.set_pricelist_discount_for_owner(owner_type, gst_=gst_arg)
            continue
        elif input_.get('arg1') == "q" or input_.get('arg1') == "quit":
            cf.log_("You entered 'q' to quit")
            import sys
            sys.exit()
            break
        elif input_.get('arg1') == "b" or input_.get('arg1') == "back":
            input_= None
            continue
        elif input_.get('arg1') == "ivp":
            invoice_ =  input_.get('arg2')
            result = invoice_.fetch_invoice_details()
            invoice_.view_invoice_details(result)
            l = len(result)
            no_of_results = 5
            v = l - no_of_results
            while True:
                view_command = cf.prompt_("View Previous/Next 5: (p/n)", [], empty_="yes")
                if view_command == "p":
                    previous_v = v
                    cf.log_("previous_v is {}".format(previous_v))
                    v = v - no_of_results
                    cf.log_("v is {}".format(v))
                    if not v < 0:
                        cf.log_("{}, {}".format(v,previous_v-1))
                        invoice.view_print(result[v:previous_v-1])
                        print("v, previous_v:\n{}, {}".format(v, previous_v))
                        continue
                    else:
                        invoice.view_print(result[:previous_v])
                        print("reached top")
                        v = l - no_of_results
                        continue
                elif view_command == "n":
                    if 'next_v' not in locals():
                        next_v = previous_v
                    else:
                        next_v = v
                    v = next_v + no_of_results
                    if len(result) > v:
                        print("v, next_v:\n{}, {}".format(v, next_v))
                        invoice.view_print(result[next_v:v])
                        continue
                    else:
                        invoice.view_print(result[v-no_of_results:])
                        print("reached bottom")
                        v = len(result) - no_of_results
                        continue
                else:
                    break
            input_  = cm.command_loop(invoice_)
            continue
        elif input_.get('arg1') in ["oli", "olim"]:
            owner_nickname = input_.get('arg2')
            last_invoice_ = input_.get('arg3')
            if input_.get('arg1') == 'olim':
                master_ = True
            else:
                master_ = False
            invoice_type = last_invoice_.invoice_type
            owner_type = last_invoice_.owner_type
            id_owner = owner.get_id_from_nickname(owner_type,  owner_nickname)
            invoice_id = owner.get_owner_last_invoice_id(invoice_type, id_owner, master_=master_)
            invoice_ = invoice.get_existing_invoice(invoice_type, invoice_id, master_=master_)
            sale_report.create_(invoice_, 'A6', master_=True)
            # invoice_.view_invoice_details(invoice_.fetch_invoice_details(master_=master_))
            if master_:
                input_ = cm.open_invoice_by_id(last_invoice_.id, invoice_type)
                continue
            input_ = cm.command_loop(invoice_)
            continue
        elif input_.get('arg1') == "ov":
            owner_nickname = input_.get('arg2')
            last_invoice_ = input_.get('arg3')
            invoice_type = last_invoice_.invoice_type
            owner_type = last_invoice_.owner_type
            id_owner = owner.get_id_from_nickname(owner_type,  owner_nickname)
            owner_=owner.get_existing_owner_by_id(owner_type, id_owner)
            owner_.display_basic_info()
            input_ = None
            continue
        elif input_.get('arg1') == "oai":
            owner_nickname = input_.get('arg2')
            last_invoice_ = input_.get('arg3')
            invoice_type = last_invoice_.invoice_type
            owner_type = last_invoice_.owner_type
            id_owner = owner.get_id_from_nickname(owner_type,  owner_nickname)
            owner_=owner.get_existing_owner_by_id(owner_type, id_owner)
            invoice_id = owner_.get_owner_invoice(invoice_type)
            input_ = cm.open_invoice_by_id(invoice_id, invoice_type)
            continue
        elif input_.get('arg1') == "oe":
            try:
                owner_nickname = input_.get('arg2')
                last_invoice_ = input_.get('arg3')

                # above two statements do not generate exception
                invoice_type = last_invoice_.invoice_type
            except Exception as e:
                cf.log_(e)
                owner_type = cf.prompt_('Select Owner Type: ', ["customer", "vendor"])
                if owner_type in ["quit", "back"]:
                    input_= {"arg1":"back"}
                owner_nickname = cf.prompt_("Enter Owner Nickname: ",cf.get_completer_list("nickname", owner_type), unique_="existing")
                id_owner = owner.get_id_from_nickname(owner_type,  owner_nickname)
                owner_=owner.get_existing_owner_by_id(owner_type, id_owner)
                while True:
                    owner_.edit_properties()
                input_ = None
                continue
            owner_type = last_invoice_.owner_type
            id_owner = owner.get_id_from_nickname(owner_type,  owner_nickname)
            owner_=owner.get_existing_owner_by_id(owner_type, id_owner)
            while True:
                owner_.edit_properties()
            input_ = None
            continue
        elif input_.get("arg1") ==  "osb":
            nickname = input_.get('arg2')
            last_invoice_ = input_.get('arg3')
            invoice_type = last_invoice_.invoice_type
            owner_product = cf.owner_product_from_invoice_type_d[invoice_type]
            owner_type = last_invoice_.owner_type
            id_owner = owner.get_id_from_nickname(owner_type, nickname, no_create="y")
            cm.sandbox(id_owner, owner_product)
            input_ = cm.open_invoice_by_id(last_invoice_.id, invoice_type)
            continue
        elif input_.get('arg1') == "on":
            owner_nickname = input_.get('arg2')
            last_invoice_ = input_.get('arg3')
            invoice_type = last_invoice_.invoice_type
            invoice_ = invoice.get_new_invoice(invoice_type, nickname=owner_nickname)
            input_ = cm.inside_invoice(invoice_)
            continue
        elif input_.get('arg1') == "op":
            owner_nickname = input_.get('arg2')
            last_invoice_ = input_.get('arg3')
            invoice_type = last_invoice_.invoice_type
            owner_type = last_invoice_.owner_type
            id_owner = owner.get_id_from_nickname(owner_type,  owner_nickname)
            invoice_id = owner.get_owner_last_invoice_id(invoice_type, id_owner)
            invoice_ = invoice.get_existing_invoice(invoice_type, invoice_id)
            cf.log_("reached op here")
            sale_report.create_(invoice_, 'A6')
            # go back to current invoice
            invoice_ = invoice.get_existing_invoice(invoice_type, last_invoice_.id)
            invoice_.view_invoice_details(invoice_.fetch_invoice_details())
            input_ = cm.command_loop(invoice_)
            # ask for invoice and print it
            pass
        elif input_.get('arg1') == "opl":
            input_ = None
            # set pricelist discount
            pass
        elif input_.get('arg1') == "ol":
            input_ = None
            pass
        else:
            cf.log_("Unknown command: {}".format(input_))
            input_ = None
            continue

if __name__ == "__main__":
    # result = cf.prompt_("Select Database: ", ['stack', 'chip'], unique_="existing", default)
    # if result == 'stack':
        # Database.initialise(database='stack', host='localhost', user='dba_tovak')
    # elif result =='chip':
    Database.initialise(database='chip', host='localhost', user='dba_tovak')
    # chip()
    while True:
        try:
            chip()
        except Exception as e:
            print(e)
