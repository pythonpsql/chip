from database import Database, CursorFromConnectionFromPool as conn
from psycopg2 import sql
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit import prompt
from decimal import Decimal, ROUND_HALF_UP
from prettytable import PrettyTable
import colored
import common_functions as cf
import pricelist_functions as plf
import owner
import invoice
import product
import money
import invoice_detail
import barrel_nipple
import extension
import sale_report
import gst_report
import command_dict


commands_dict = command_dict.commands_dict

commands_list = [*commands_dict]
comm_completer = WordCompleter(commands_list, meta_dict=commands_dict)

#command_ = prompt("Enter command: ", history=FileHistory('command_history.txt'), auto_suggest = AutoSuggestFromHistory())
starting_list = ['v', 'va','vp', 'eq', 'er', 'ed', 'egn', 'p', 'pg', 'del', 'set_bn_rates', 'set_ex_rates', 'delete', 'save', 'pack','makegst', 'cash_r', 'invoice_r', 'unpack', 'packed', 'unpacked', 'pack_n', 'date', 'set_owner_gst_number', 'set_gst_invoice_number', 'cash_memo', 'credit_memo', 'set_gst_name']
startswith_list = ['fr ', 'lr ', 'bn ', ',', 'ex ', 'pr ']

def sandbox(id_owner, owner_product):
    # TODO add feature to modify or add new rates
    result = cf.cursor_(sql.SQL("select distinct p.name from product as p join {} as op on op.id_product = p.id where op.id_owner = %s").format(sql.Identifier(owner_product)), arguments= (id_owner, ))
    product_custom_owner_list = [element[0] for element in result]
    while True:
        product_name = cf.prompt_("Enter Product Name: ", product_custom_owner_list, unique_="existing")
        if product_name == "quit": break
        if product_name == "back": break
        product_id = product.get_id_from_name(product_name)
        rate, discount = invoice_detail.get_previous_rate_discount(id_owner, owner_product, product_id)
        cf.log_("Rate: {}\nDiscount: {}".format(rate, discount))

def test():
    customer_= owner.Owner("customer", id_=46)
    customer_.set_properties()

def open_invoice_by_id(invoice_id, invoice_type):
    invoice_ = invoice.get_existing_invoice(invoice_type, invoice_id)
    return inside_invoice(invoice_)

def inside_invoice(invoice_):
    invoice_.view_invoice_details(invoice_.fetch_invoice_details())
    return command_loop(invoice_)

def command_loop(invoice_):
    cf.log_("inside command_loop")
    while True:
        command_ = get_command(invoice_)
        if command_ == 'q':
            import sys
            sys.exit()
        if command_.startswith("."):
            command_ = command_[1:]
        if command_.startswith("/"):
            command_ = command_[1:]
            return {'arg1': 'invoice_by_id', 'arg2': command_, 'arg3': invoice_.invoice_type}
        if command_.startswith("\\"):
            command_ = command_[1:]
            return {'arg1': 'invoice_by_id', 'arg2': command_, 'arg3': invoice_.invoice_type}
        cf.log_("command_loop.command_ is {}".format(command_))
        if command_ == "quit": return {"arg1": "quit"}
        if command_ == "back": return {"arg1": "back"}
        cf.clear_screen()
        print("Previous command: {}".format(colored.stylize(command_, colored.fg('blue'))))
        command_details = classify_command(command_, invoice_)
        if command_details.get('arg1') == "quit": return command_details
        if command_details.get('arg1') == "back": return command_details
        if command_details.get('arg1') == "continue":
            continue
        else:
            # owner_name and invoice_
            cf.log_("command_loop returns {}".format(command_details))
            return command_details

def get_command(invoice_):
    # invoice_result = owner.get_filter_result("Unsaved Invoices", "sale_invoice")
    if invoice_.invoice_type == "sale_invoice":
        invoice_list  = owner.get_all_gst_invoices("sale_invoice")
        estimate_list = owner.get_all_unsaved_invoices("sale_invoice")
    elif invoice_.invoice_type == "purchase_invoice":
        invoice_list  = owner.get_all_gst_invoices("purchase_invoice")
        estimate_list = owner.get_all_unsaved_invoices("purchase_invoice")

    invoice_dict = {}
    estimate_dict = {}

    for a in invoice_list:
        invoice_dict[str(a[4])] = "{}, {}, {}, {}".format(str(a[0]), str(a[2]), str(a[3]), str(a[1]))
    for a in estimate_list:
        estimate_dict[str(a[3])] = "{}, {}, {}".format(str(a[1]), str(a[2]), str(a[0]))

    invoice_list = [str(a[4]) for a in invoice_list] # do not unpack dict with * to get this list because dictionary is always unsorted
    estimate_list = [str(a[3]) for a in estimate_list] # do not unpack dict with * to get this list because dictionary is always unsorted
    # invoice_result = owner.get_all_unsaved_invoices(invoice_.invoice_type)
    # invoice_list = [str(a[3]) for a in invoice_result]
    # invoice_dict = {}
    # for a in invoice_result:
    #     invoice_dict[str(a[3])] = "{}, {}, {}".format(str(a[0]), str(a[1]), str(a[2]))
    cf.log_("inside get command")
    owner_product = cf.owner_product_from_invoice_type_d[invoice_.invoice_type]
    owner_product_list, owner_product_dict = product.get_owner_product_dict(owner_product, invoice_.owner.id)
    # owner_product_abbr_list, owner_product_abbr_dict = product.get_owner_product_abbr_dict(owner_product, invoice_.owner.id)
    owner_nickname_list = cf.get_completer_list("nickname", invoice_.owner_type)
    # invoice_command_list = owner_product_list + owner_product_abbr_list + owner_nickname_list
    invoice_command_list = owner_product_list +  owner_nickname_list + starting_list + startswith_list + ['b', 'q']
    # creating dict with None values
    owner_nickname_dict = dict.fromkeys(owner_nickname_list)
    # invoice_command_dict = {**owner_product_dict, **owner_product_abbr_dict, **owner_nickname_dict}
    invoice_command_dict = {**owner_product_dict,  **owner_nickname_dict}
    return cf.prompt_dict("Enter {} command:".format(invoice_.invoice_type), invoice_command_dict, list_=invoice_command_list, invoice_list = invoice_list, invoice_dict=invoice_dict, estimate_list=estimate_list, estimate_dict=estimate_dict)

def classify_command(command_, invoice_):
    cf.log_("inside classify_command")
    owner_nickname_list = cf.get_completer_list("nickname", invoice_.owner_type)
    # Possible Return Values:
        # 1. ["continue", "continue"]
        # 2. ["owner_name", invoice_]
        # 3. ["quit", "quit"]
    # Take care to check for starting list on top since the single letter inputs will hold true for product_list and owner_list
    if any([command_.startswith(n) for n in startswith_list]):
        cf.log_("command_ starts with a startswith_list value")
        return startswith_command(command_, invoice_)
    if command_ in starting_list:
        cf.log_("command_ is in starting list")
        return starting_command(command_, invoice_)
    if command_ in owner_nickname_list:
        owner_nickname = command_
        owner_type = invoice_.owner_type
        owner_command = cf.prompt_dict("Enter {}[{}] command: ".format(owner_type, owner_nickname), command_dict.owner_commands[owner_type])
        owner_command = "o" + owner_command
        return {"arg1": owner_command, "arg2": owner_nickname, "arg3": invoice_}
    else:
    # elif command_.lower() in [name.lower() for name in self.product_list]:
        product_qty = command_.split()[-1]
        product_name = " ".join(command_.split()[:-1])
        try:
            cf.log_("Creating new invoice_detail")
            i_detail_ = invoice_detail.get_new_invoice_detail_by_product(invoice_, product_name, product_qty)
            invoice_.update_invoice_with_sub_total()
            i_detail_.view_()
        except Exception as e:
            cf.log_(e)

        return {"arg1": "continue"}


def starting_command( input_, invoice_):
    cf.log_("inside starting command")
    # possible return values:
        # 1. ["continue", "continue"]
        # 2. [invoice_command, invoice_]
    if input_ == "pack_n":
        if invoice_.invoice_type == "sale_invoice":
            detail_table ="si_detail"
            owner_type = "customer"
        if invoice_.invoice_type == "purchase_invoice":
            detail_table ="pi_detail"
            owner_type = "vendor"
        new_invoice = invoice.get_new_invoice(invoice_.invoice_type, nickname=owner.get_nickname_from_id(owner_type, invoice_.owner.id))
        sq= "update {} set id_invoice = %s  where id_invoice = %s and packed is not null returning id"
        with conn() as cursor:
            cursor.execute(sq.format(detail_table), (new_invoice.id, invoice_.id, ))
            delete_list = cursor.fetchall()
        new_invoice.update_invoice_with_sub_total()
        invoice_.update_invoice_with_sub_total()
    if input_ in ["makegst"]:
        invoice_.makegst()
    if input_ in ["cash_r", "invoice_r"]:
        if invoice_.invoice_type == "sale_invoice":
            money_type = "receipt"
            medium = input_
            with conn() as cursor:
                cursor.execute("select id from {} where detail = %s". format(money_type), (str(invoice_.id), ))
                result = cursor.fetchall()
                print(result)
                if len(result) == 1:
                    with conn() as cursor:
                        cursor.execute("update {} set amount = %s  where detail = %s returning id".format(money_type), (invoice_.amount_after_freight, str(invoice_.id)))
                        result = cursor.fetchall()
                    cf.log_("Receipt Entry updated with id {}".format(result))
                    print("Receipt entry updated")
                    # money_ = money.Money('receipt', id_= result[0][0])
                    # money_.save()
                elif len(result) > 1:
                    print("Multiple Entries present")
                else:
                    date_ = money.get_date()
                    sq = "insert into {} (date_, id_owner, amount, recipient, detail, medium) values (%s,%s, %s, %s, %s, %s) returning id"
                    result = cf.execute_(sq, [money_type], arg_=(date_, invoice_.owner.id, invoice_.amount_after_freight, "self", invoice_.id, medium ), fetch_="y")[0]
                    print("Receipt entry created")
                    cf.log_("Receipt Entry created with id {}".format(result))
                    # money_ = money.Money('receipt', id_= result[0])
                    # money_.save()

    if input_ in ["pack", "unpack"]:
        property_ = "packed"
        if invoice_.invoice_type == "sale_invoice":
            detail_table ="si_detail"
        if invoice_.invoice_type == "purchase_invoice":
            detail_table ="pi_detail"
        sq_pack = "select product_name, packed, product_qty from {} where id_invoice = %s and packed is null order by id"
        sq_unpack = "select product_name, packed, product_qty from {} where id_invoice = %s and packed is not null order by id"
        if input_ == "pack":
            sq = sq_pack
        elif input_ == "unpack":
            sq = sq_unpack
        while True:
            with conn() as cursor:
                cursor.execute(sq.format(detail_table), (invoice_.id, ))
                result = cursor.fetchall()
            invoice_product_name_list = [element[0] for element in result]
            invoice_product_name_qty_dict = {element[0]: str(element[2]) for element in result}
            product_name = cf.prompt_dict("Edit Product: ", invoice_product_name_qty_dict)
            if product_name in invoice_product_name_list:
                if input_ == "pack":
                    detail_table_id = invoice_.get_detail_table_id(product_name, packed="yes") # returns id of  items which are not packed
                elif input_ == "unpack":
                    detail_table_id = invoice_.get_detail_table_id(product_name, unpacked="yes")
                i_detail_ = invoice_detail.get_existing_invoice_detail_by_id(invoice_, detail_table_id)
                i_detail_.edit_property(property_)
            else:
                break
    if input_ in ["packed", "unpacked"]:
        if invoice_.invoice_type == "sale_invoice":
            detail_table ="si_detail"
        if invoice_.invoice_type == "purchase_invoice":
            detail_table ="pi_detail"
        sq_packed = "select product_name from {} where id_invoice = %s and packed is not null order by id"
        sq_unpacked = "select product_name from {} where id_invoice = %s and packed is null order by id"
        if input_ == "packed":
            sq = sq_packed
        elif input_ == "unpacked":
            sq = sq_unpacked
        with conn() as cursor:
            cursor.execute(sq.format(detail_table), (invoice_.id,))
            result = cursor.fetchall()
        pt = PrettyTable([input_])
        for a in result:
            a0 = colored.stylize(a[0], colored.fg('green')) if input_ == "packed" else a[0]
            pt.add_row([a0])
        print(pt)

    if input_ == 'vp':
        return {"arg1": "ivp", "arg2": invoice_}
    if input_ == "save":
        print("invoice_.gst_invoice_no: {}".format(invoice_.gst_invoice_no))
        if not invoice_.gst_invoice_no or invoice_.gst_invoice_no == 'None':
            invoice_.save()
            print('saved')
        else:
            print('This is a GST Invoice.')
            invoice_.gst_save()
            print('saved')
        return {"arg1": "continue"}
    if input_ == "delete":
        confirm_ = cf.prompt_("Are you sure you want to delete this invoice? (y/n):", ['y', 'n'], unique_="existing")
        if confirm_ == "y":
            invoice_.delete_()
        else:
            print("You canceled. The invoice was not deleted")
        return {"arg1": "back"}

    if input_ == "set_ex_rates":
        get_product_id = cf.psql_("select id from product where name = 'Extension'")
        id_product = get_product_id[0][0]
        owner_product = cf.owner_product_from_invoice_type_d[invoice_.invoice_type]
        id_owner = invoice_.owner.id
        # sq = "select rate, gst_rate from {} where id_owner = %s and id_product in (3593, 3595, 3598, 3600, 3628, 3639, 3636, 3578, 3663)".format(owner_product)
        sq = "select rate, gst_rate from {} where id_owner = %s and id_product = %s".format(owner_product)
        result = cf.psql_(sq, arg_=(invoice_.owner.id, id_product ))
        print(result)

        confirm_ = cf.prompt_("Select type of rate to edit: ", ["gst", "non_gst"], unique_="existing")
        get_rate = cf.prompt_("Enter rate for Extension: ", [])
        if confirm_ == "gst":
            gst_arg = True
        else:
            gst_arg = False
        extension.set_owner_product_rate(owner_product, id_product, id_owner, get_rate, gst_=gst_arg)

    if input_ == "set_bn_rates":
        get_product_id = cf.psql_("select id from product where name in ('Barrel Nipple 15', 'Barrel Nipple 20', 'Barrel Nipple 25', 'Barrel Nipple 32', 'Barrel Nipple 40', 'Barrel Nipple 50', 'Barrel Nipple 65', 'Barrel Nipple 80', 'Barrel Nipple 100' )")
        print(get_product_id)
        owner_product = cf.owner_product_from_invoice_type_d[invoice_.invoice_type]
        id_owner = invoice_.owner.id
        get_product_id = tuple(get_product_id)
        # sq = "select rate, gst_rate from {} where id_owner = %s and id_product in (3593, 3595, 3598, 3600, 3628, 3639, 3636, 3578, 3663)".format(owner_product)
        sq = "select rate, gst_rate from {} where id_owner = %s and id_product in %s".format(owner_product)
        result = cf.psql_(sq, arg_=(invoice_.owner.id, get_product_id))
        print(result)

        product_name = "Barrel Nipple " + cf.prompt_("Enter Barrel Nipple Size to edit rate of: ", ['15', '20', '25', '32', '40', '50', '65', '80', '100'], unique_="existing")
        confirm_ = cf.prompt_("Select type of rate to edit: ", ["gst", "non_gst"], unique_="existing")
        get_rate = cf.prompt_("Enter rate for {}: ".format(product_name), [])
        id_product = cf.psql_("select id from product where name = %s", arg_=(product_name, ))
        id_product = id_product[0][0]
        if confirm_ == "gst":
            gst_arg = True
        else:
            gst_arg = False
        barrel_nipple.set_owner_product_rate(owner_product, id_product, id_owner, get_rate, gst_=gst_arg)

    if input_ == "del":
        result = invoice_.fetch_invoice_details()
        invoice_product_name_list = [element[0] for element in result]
        product_name = cf.prompt_("Edit Product: ", invoice_product_name_list, unique_="existing")
        detail_table_id = invoice_.get_detail_table_id(product_name)
        print(invoice_.invoice_type)
        i_detail_ = invoice_detail.get_existing_invoice_detail_by_id(invoice_, detail_table_id)
        i_detail_.delete_()
        invoice_.update_invoice_with_sub_total()
        result = invoice_.fetch_invoice_details()
        invoice_.view_invoice_details(result)
    if input_ == "v":
        # view all invoice detail items
        result = invoice_.fetch_invoice_details()
        invoice_.view_invoice_details(result)
    if input_ == "va":
        # view all invoice detail items
        result = invoice_.fetch_invoice_details()
        invoice_.view_invoice_details(result, all_="yes")
    if input_ == "p":
        invoice_.update_invoice_with_sub_total()
        # create pdf of invoice
        sale_report.create_(invoice_, 'A6')
    if input_ == "pg":
        gst_report.create_(invoice_, 'A5')
        # result = invoice_.fetch_invoice_details()
        # print(len(result))
        # if len(result) > 19:
        #     sale_report.create_(invoice_)
        # else:
        #     sale_report_A6.create_(invoice_)
    if input_ == "date":
        invoice_.edit_property("date_")
        result = invoice_.fetch_invoice_details()
        invoice_.view_invoice_details(result)
    if input_ == "set_owner_gst_number":
        invoice_.owner.set_gst_number()
    if input_ == "set_gst_name":
        invoice_.owner.set_gst_name()
    if input_ == "set_gst_invoice_number":
        invoice_.set_gst_invoice_number()
    if input_ == "cash_memo":
        invoice_.set_memo_type("cash")
    if input_ == "credit_memo":
        invoice_.set_memo_type("credit")
    if input_.startswith("e"):
        result = invoice_.fetch_invoice_details()
        editable_properties = {"q": ["product_qty", "Quantity"], "r": ["product_rate", "Rate"], "d":["product_discount", "Discount"], "gn": ["product_gst_name", "GST Name"]}
        property_ = editable_properties[input_[1:]][0]
        invoice_product_name_list = [element[0] for element in result]
        product_name = cf.prompt_("Edit Product: ", invoice_product_name_list)
        if product_name in invoice_product_name_list:
            detail_table_id = invoice_.get_detail_table_id(product_name)
            i_detail_ = invoice_detail.get_existing_invoice_detail_by_id(invoice_, detail_table_id)
            if invoice_.gst_invoice_no is None:
                gst_arg = False
            else:
                gst_arg = True
            i_detail_.edit_property(property_, gst_=gst_arg)
        else:
            cf.log_("Product Name is not in this invoice. No edits were made")
    return {"arg1": "continue"}

def startswith_command(input_, invoice_):
    # Possible Return Values:
        # 1. ["continue", "continue"]
    if input_.startswith('pr '):
        no_of_prints = int(input_.split("pr ")[1])
        if no_of_prints < 3:
            invoice_.update_invoice_with_sub_total()
            # create pdf of invoice
            sale_report.create_(invoice_, 'A6', no_of_print=no_of_prints)
    if input_.startswith('lr '):
        transport_lr_no = input_.split(" ")[1]
        invoice_.transport_lr_no = transport_lr_no
        cf.log_("transport_lr_no is {}".format(transport_lr_no))
        cf.cursor_(sql.SQL("update {} set (transport_lr_no) = (%s) where id = %s returning id").format(sql.Identifier(invoice_.invoice_type)), arguments=(transport_lr_no, invoice_.id))


    if input_.startswith('fr '):
        freight = input_.split(" ")[1]
        cf.log_("freight is {}".format(freight))
        try:
            if not float(freight).is_integer:
                freight = float(freight)
        except Exception as e:
            cf.log_(e)
            cf.log_("Incorrect value for freight")
            return {"arg1": "continue"}
        invoice_.set_freight(Decimal(freight))
        invoice_.update_invoice_with_sub_total()
        invoice_.view_invoice_details(invoice_.fetch_invoice_details())
    if input_.startswith('bn '):
        print('invoice_.gst_invoice_no is {}'.format(invoice_.gst_invoice_no))
        if invoice_.gst_invoice_no is None:
            bn = barrel_nipple.BarrelNipple(input_, invoice_)
        else:
            bn = barrel_nipple.BarrelNipple(input_, invoice_, gst_=True)

        invoice_.update_invoice_with_sub_total()
        invoice_.view_invoice_details(invoice_.fetch_invoice_details())
    if input_.startswith('ex '):
        print('invoice_.gst_invoice_no is {}'.format(invoice_.gst_invoice_no))
        if invoice_.gst_invoice_no is None:
            ex = extension.Extension(input_, invoice_)
        else:
            ex = extension.Extension(input_, invoice_, gst_=True)
        # after implementing init_by_id in invoice_detail, the following code can be used as starting point to see only the added Extension items
        '''
        id_result = ex.invoice_detail_id_list
        id_list = [element for tupl in id_result for element in tupl]
        cf.log_(id_list)
        temp_list = []
        for id_ in id_list:
            i_detail_ = invoice_detail.InvoiceDetail(invoice_, product_name, id_=id_list)
            temp_list.append(i_detail_.get_detail_values())
        cf.log_(temp_list)
        '''
        invoice_.update_invoice_with_sub_total()
        invoice_.view_invoice_details(invoice_.fetch_invoice_details())
    if input_.startswith(','):
        if input_ == ",,":
            return {"arg1": ","}
        return {"arg1": input_.split(",")[1]}
    return {"arg1": "continue"}

def ending_command( input_):
    result = self.fetch_invoice_details()
    # split input_ into command_ and product_name
    product_name = " ".join(input_.split()[:-1])
