from database import CursorFromConnectionFromPool as conn
from psycopg2 import sql
from prettytable import  PrettyTable
import common_functions as cf
import invoice
import money
import owner
import master
import sale_report
import ledger_report

properties = ['id', 'type', 'id_invoice', 'id_voucher', 'date_']

def view(transaction_type, **kwargs):
    gst_ = kwargs.get('gst_', '')
    if transaction_type == "sale_transaction":
        m = "Receipt"
    elif transaction_type == "purchase_transaction":
        m = "Payment"
    columns = ['ID', 'Date','Type', 'Owner ID', 'Invoice ID', m + ' ID', ' Amount']
    if gst_:
        result = cf.cursor_(sql.SQL("select id, date_, type, id_owner, id_invoice, id_voucher, amount from {}").format(sql.Identifier(transaction_type)))
    else:
        result = cf.cursor_(sql.SQL("select id, date_, type, id_owner, gst_invoice_no, id_voucher, amount from {}").format(sql.Identifier(transaction_type)))
    cf.pretty_table_multiple_rows(columns, result)


def view_by_nickname(transaction_type, nickname, **kwargs):
    gst_ = kwargs.get('gst_', '')
    if transaction_type == "sale_transaction":
        m = "Receipt"
        owner_type = "customer"
    else:
        m = "Payment"
        owner_type = "vendor"
    columns = ['ID', 'Date','Type', 'Invoice ID', m + ' ID', ' Amount']
    if gst_:
        result = cf.cursor_(sql.SQL("select t.id,t.date_,t.type, t.id_invoice, t.id_voucher, t.amount from {} as t where t.id_owner = %s where t.gst_invoice_no is not null").format(sql.Identifier(transaction_type)),  arguments=(owner.get_id_from_nickname(owner_type, nickname,no_create="yes"), ))
    else:
        result = cf.cursor_(sql.SQL("select t.id,t.date_,t.type, t.id_invoice, t.id_voucher, t.amount from {} as t where t.id_owner = %s where t.gst_invoice_no is null").format(sql.Identifier(transaction_type)),  arguments=(owner.get_id_from_nickname(owner_type, nickname,no_create="yes"), ))
    cf.pretty_table_multiple_rows(columns, result)


def get_owner(tr_type, owner_type):
    nickname = cf.prompt_("Enter {} nickname: ".format(owner_type), cf.get_completer_list("nickname", owner_type), unique_="existing")
    if nickname == "quit": return "quit", None
    owner_ = owner.get_existing_owner_by_nickname(owner_type, nickname)
    return owner_

def get_view(transaction_type, **kwargs):
    master_ = kwargs.get('master_', '')
    gst_= kwargs.get('gst_', '')
    if transaction_type == "sale_transaction":
        if gst_:
            view_ = sql.Identifier("gst_sale_ledger_view")
        else:
            view_ = sql.Identifier("sale_ledger_view")
    elif transaction_type == "purchase_transaction":
        if gst_:
            view_ = sql.Identifier("gst_purchase_ledger_view")
        else:
            view_ = sql.Identifier("purchase_ledger_view")
    if master_:
        view_ = sql.SQL("master.") + view_
    return view_

def get_owner_type(tr_type, **kwargs):
    if tr_type == "sale_transaction": owner_type = "customer"
    if tr_type == "purchase_transaction": owner_type = "vendor"
    return owner_type

def get_a_balance(tr_type, **kwargs):
    owner_type = get_owner_type(tr_type, **kwargs) # customer | vendor
    view_ = get_view(tr_type, **kwargs)
    owner_ = get_owner(tr_type, owner_type)
    id_owner = owner_.id
    if tr_type == "sale_transaction":
        with conn() as cursor:
            cursor.execute("select o.name,o.place, sum(invoice_amount)-sum(money_amount)+ o.opening_balance as tb from master.sale_ledger_view as slv join master.customer as o on o.id=slv.id_owner where id_owner=%s group by slv.id_owner, o.name, o.place, o.opening_balance order by tb desc", (id_owner,))
            result = cursor.fetchall()
        pt = PrettyTable(['Name', 'Place', 'Balance'])
        for a in result:
            pt.add_row(a)
        print(pt)


    # print(invoice_amount)
    # print(money_amount)
    # print(opening_balance)

def get_all_balances(tr_type,   **kwargs):
    if tr_type == "sale_transaction":
        with conn() as cursor:
            cursor.execute("select o.name,o.place, sum(invoice_amount)-sum(money_amount)+ o.opening_balance as tb from master.sale_ledger_view as slv join master.customer as o on o.id=slv.id_owner group by slv.id_owner, o.name, o.place, o.opening_balance order by tb desc")
            result = cursor.fetchall()
        pt = PrettyTable(['Name', 'Place', 'Balance'])
        for a in result:
            pt.add_row(a)
        print(pt)



    # owner_type = get_owner_type(tr_type, **kwargs) # customer | vendor
    # view_ = get_view(tr_type, **kwargs)
    # with conn() as cursor:
    #     cursor.execute("select id, name, place from {} order by name, place".format(owner_type))
    #     all_owner_id = cursor.fetchall()
    # pt = PrettyTable(['Name', 'Place', 'Balance'])
    # for a in all_owner_id:
    #     id_owner = a[0]
    #     # print(a[1] + " " + a[2])
    #     try:
    #         balance = get_a_balance(tr_type, id_owner=id_owner, master_=True)
    #         pt.add_row([a[1], a[2], round(balance, 0)])
    #     except Exception as e:
    #         print(e)
    # print(pt)
    # # print(opening_balance)

def get_ledger_result(view_, id_owner, **kwargs):
    gst_ = kwargs.get('gst_', '')
    if gst_:
        sq = sql.SQL("select date_, gst_invoice_no, invoice_amount, money_amount, ts-tr+gst_opening_balance, gst_opening_balance  from {} where id_owner = %s").format(view_)
    else:
        sq = sql.SQL("select date_, id_, invoice_amount, money_amount, ts-tr+opening_balance, opening_balance  from {} where id_owner = %s").format(view_)

    with conn() as cursor:
        cursor.execute(sq , (id_owner, ))
        return cursor.fetchall()

def get_ledger_result_by_date(view_, id_owner, date_, **kwargs):
    gst_ = kwargs.get('gst_', '')
    if gst_:
        sq = sql.SQL("select date_, gst_invoice_no, invoice_amount, money_amount, ts-tr+gst_opening_balance  from {} where id_owner = %s and date_ >= %s").format(view_)
    else:
        sq = sql.SQL("select date_, id_, invoice_amount, money_amount, ts-tr+opening_balance  from {} where id_owner = %s and date_ >= %s").format(view_)
    with conn() as cursor:
        cursor.execute(sq , (id_owner, date_))
        return cursor.fetchall()

def get_opening_balance(view_, id_owner, result, **kwargs):
    date_ = kwargs.get('date_', '')
    gst_ = kwargs.get('gst_', '')
    if not date_: return result[0][5]
    if gst_:
        with conn() as cursor:
            cursor.execute(sql.SQL("select ts-tr+gst_opening_balance from {} where id_owner = %s and date_ < %s order by date_ desc, id desc limit 1").format(view_), (id_owner, date_))
        result = cursor.fetchone()
    else:
        with conn() as cursor:
            cursor.execute(sql.SQL("select ts-tr+opening_balance from {} where id_owner = %s and date_ < %s order by date_ desc, id desc limit 1").format(view_), (id_owner, date_))
        result = cursor.fetchone()
    print('opening balance is {}'.format(result))
    return result[0]

def print_ledger(result, owner_type, opening_balance):
    if owner_type == "customer": money = 'Receipt'
    if owner_type == "vendor": money = 'Payment'
    columns = ['Date', 'id_', 'Invoice', money, 'Balance']
    right_align_columns = ['id', 'Invoice', money, 'Balance']
    left_align_columns=['Date']
    pt = PrettyTable(columns)
    print('OB is {}'.format(opening_balance))
    pt.add_row(['Opening', '','','',str(opening_balance)])
    # pt.set_style(PLAIN_COLUMNS)
    for a in result:
        a0 = cf.reverse_date(str(a[0]))
        if a[2] is None:
            a2 = ''
        else:
            a2 = a[2]
        if a[3] is None:
            a3 = ''
        else:
            a3 = a[3]
        pt.add_row([a0, a[1], a2, a3, a[4]])
    pt.align = 'r'
    for l in left_align_columns:
        pt.align[l] = 'l'
    # for r in right_align_columns:
    #     pt.align[r] = 'r'
    print(pt)

def command_loop(tr_type, owner_, result, opening_balance, view_, **kwargs):
    master_ = kwargs.get("master_", '')
    id_owner = owner_.id
    owner_type = owner_.owner_type
    if tr_type == "sale_transaction":
        invoice_type = "sale_invoice"
        money_type = "receipt"
    if tr_type == "purchase_transaction":
        invoice_type = "purchase_invoice"
        money_type = "payment"
    while True:
        input_ = cf.prompt_("Enter Ledger Command: ", ['p', 'pi', 'pm', 'n','ng', 'pr', 'del'], unique_="existing")
        if input_ ==  "del":
            master.backup()
            if master_:
                invoice_type = sql.SQL("master.") + sql.Identifier(invoice_type)
                money_type = sql.SQL("master.") + sql.Identifier(money_type)
                owner_type = sql.SQL("master.") + sql.Identifier(owner_type)
            date_list = [str(e[0]) for e in result]
            date_ = cf.prompt_("Enter Starting Date: ", date_list, unique_="existing")
            result = get_ledger_result_by_date(view_, id_owner, date_)
            opening_balance = get_opening_balance(view_, id_owner,  result, date_=date_)
            with conn() as cursor:
                cursor.execute(sql.SQL("select id_invoice, id_voucher from {} where id_owner = %s and date_ < %s ").format(view_), (id_owner, date_))
                result = cursor.fetchall()
            invoice_list = [a[0] for a in result if a[0] is not None]
            invoice_list = tuple(invoice_list)
            voucher_list = [a[1] for a in result if a[1] is not None]
            voucher_list = tuple(voucher_list)
            print(invoice_list)
            print(voucher_list)
            print(opening_balance)
            if invoice_list:
                with conn() as cursor:
                    cursor.execute(sql.SQL("delete from {} where id in %s ").format(invoice_type), (invoice_list, ))
            if voucher_list:
                with conn() as cursor:
                    cursor.execute(sql.SQL("delete from {} where id in %s ").format(money_type), (voucher_list, ))
            with conn() as cursor:
                cursor.execute(sql.SQL("update {} set opening_balance = %s where id = %s").format(owner_type), (opening_balance, owner_.id))

        if input_ == "n":
            print('issuing command "slm"')
            return {'arg1': 'slm'}
        if input_ == "ng":
            print('issuing command "slg"')
            return {'arg1': 'slg'}
        if input_ == "p":
            ledger_report.create_(result, 'A6', owner_, opening_balance, **kwargs)
            continue
        if input_ in ["back", "quit"]: return input_
        if input_ in [ "pi", "pr"]:
            invoice_dict = {str(a[1]) if a[2]  not in [None, 0] else None: str(a[2]) if a[2]  not in [None, 0] else None for a in result}
            invoice_dict = {k:v for k,v in invoice_dict.items() if k is not None}
            # money_list = [a[1] if a[3] is not None for a in result]
            invoice_id = cf.prompt_dict("Select Invoice: ", invoice_dict)
            if invoice_id in ["back", "quit"]: return invoice_id
            invoice_ = invoice.get_existing_invoice(invoice_type, invoice_id, master_=master_)
            if input_ == "pi":
                invoice_.view_invoice_details(invoice_.fetch_invoice_details(master_=master_))
            elif input_ == "pr":
                sale_report.create_(invoice_, 'A6', master_=master_)
        if input_ == "pm":
            invoice_dict = {str(a[1]) if a[3]  not in [None, 0] else None: str(a[3]) if a[3]  not in [None, 0] else None for a in result}
            invoice_dict = {k:v for k,v in invoice_dict.items() if k is not None}
            # money_list = [a[1] if a[3] is not None for a in result]
            input_ = cf.prompt_dict("Select Invoice: ", invoice_dict)
            if input_ in ["back", "quit"]: return input_
            if invoice_type == "sale_invoice": money_type = "receipt"
            if invoice_type == "purchase_invoice": money_type = "payment"
            money_ = money.Money(money_type, id_=input_, **kwargs)
            money_details = money_.fetch_invoice_details(**kwargs)
            money_.view_invoice_details(money_details)

        # result = invoice_.fetch_invoice_details(master_=master_)
        # print(len(result))
        # if len(result) > 19:
        #     sale_report.create_(invoice_, 'A5', master_=master_)
        # else:
        #     sale_report_A6.create_(invoice_, master_=master_)
    return None

def view_summary():
    with conn() as cursor:
        cursor.execute("select name, place, sum(invoice_amount)-sum(money_amount)+master.customer.opening_balance as balance from master.sale_ledger_view join master.customer on master.customer.id = master.sale_ledger_view.id_owner group by name, place, customer.opening_balance order by balance desc")
        result = cursor.fetchall()
    columns = ['name', 'place', 'balance']
    cf.pretty_(columns, result, right_align = ['balance'])
        # ob_list = [r[3] for r in result]
        # print(ob_list)
        # print("Frist OB: {}".format(result[3]))
        # t = 0
        # for a in ob_list:
        #     t = t + a
        # print(t)

        # import csv
        # with open('total_check.csv', 'wt') as csv_file:
        #     writer = csv.writer(csv_file, delimiter = ',')
        #     for a in result:
        #         # csv_file.write(str(a))
        #         writer.writerow(a)
    right_align_columns = ['balance']
    left_align_columns = ['name', 'place']
    pt = PrettyTable(columns)
    for a in result:
        if a[2] is None:
            a2 = ''
        else:
            a2  = a[2]
        pt.add_row([a[0], a[1], a2])
    pt.align = 'l'
    for r in right_align_columns:
        pt.align[r] = 'r'
    print(pt)

def get_public_totals():
    with conn() as cursor:
        cursor.execute("select sum(invoice_amount), sum(money_amount) from sale_ledger_view ")
        result = cursor.fetchone()
        if result[0] is None:
            result_0 = 0
        else:
            result_0 = result[0]
        if result[1] is None:
            result_1 = 0
        else:
            result_1 = result[1]
    return result_0, result_1

def get_master_totals():
    with conn() as cursor:
        cursor.execute("select sum(invoice_amount), sum(money_amount) from master.sale_ledger_view ")
        result = cursor.fetchone()
    with conn() as cursor:
        cursor.execute("select sum(opening_balance) from master.customer")
        total_opening_balance = cursor.fetchone()[0]
    return result[0], result[1], total_opening_balance

def ledger_operations(tr_type, **kwargs):
    owner_type = get_owner_type(tr_type, **kwargs) # customer | vendor
    # print('got_owner_type')
    view_ = get_view(tr_type, **kwargs) # sale_ledger_view | purchase_ledger_view | master.sale_ledger_view | master.purchase_ledger_view
    # print('got_view_')
    owner_ = get_owner(tr_type, owner_type) # owner object
    # print('got_owner')
    id_owner = owner_.id
    print('got_owner_type')
    result = get_ledger_result(view_, id_owner, **kwargs)
    date_ = kwargs.get('date_', '')
    gst_ = kwargs.get('gst_','')
    if date_:
        date_list = [str(e[0]) for e in result]
        date_ = cf.prompt_("Enter Starting Date: ", date_list)
        result = get_ledger_result_by_date(view_, id_owner, date_, gst_=gst_)
    if result:
        opening_balance = get_opening_balance(view_, id_owner,  result, date_=date_, gst_=gst_)
        print_ledger(result, owner_type, opening_balance)
        input_ = command_loop(tr_type, owner_, result, opening_balance, view_, **kwargs)
        return input_
    else:
        print('No result')
