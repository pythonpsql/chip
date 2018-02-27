import common_functions as cf
from psycopg2 import sql
from prettytable import PrettyTable

def make_dr_entries():
    debtors_list = cf.cursor_(sql.SQL("select distinct name_place from bank.debtor"))
    debtors_list = [i[0] for i in debtors_list]
    result = cf.cursor_(sql.SQL("select date_, desc_, ref_cheque, amount, type_, id from bank.bank_statement where type_ = 'CR' and debtor_name is null order by id" ))
    for result in result:
        date_ = result[0]
        print(date_)
        desc_ = str(result[1])
        ref_cheque = str(result[2])
        amount = result[3]
        type_ = str(result[4])
        id_ = result[5]
        cf.pretty_table_print(['date', 'desc', 'ref_cheque','amount', 'type'], [str(date_), desc_, ref_cheque, str(amount), type_])
        options_list = get_options_list(amount)
        print(options_list)
        action = cf.prompt_("Enter debtor: ", debtors_list, empty_= "yes")
        if action == "back":
            continue
        if action == "quit":
            break
        if action in debtors_list:
            receipt_entry = cf.cursor_(sql.SQL("insert into bank.receipt (date_, name_place, amount) values (%s, %s, %s) returning id"), arguments = (date_, action, amount))
            print(receipt_entry)
            with conn() as cursor:
                cursor.execute("update bank.bank_statement set (debtor_name) = (%s) where id = %s returning id", (action, id_))
                debtor_name_entry = cursor.fetchone()[0]
            print(debtor_name_entry)

def add_pre_gst_balances():
    # one time use only
    while True:
        debtors_list = cf.cursor_(sql.SQL("select distinct name_place from bank.debtor"))
        debtors_list = [i[0] for i in debtors_list]
        action = cf.prompt_("Enter debtor: ", debtors_list, empty_= "yes")
        if action == "back":
            continue
        if action == "quit":
            break
        amount = cf.prompt_("Enter amount: ", [])
        if amount == "back":
            continue
        if amount == "quit":
            break
        result = cf.cursor_(sql.SQL("insert into bank.debtor (date_, name_place, amount) values (%s, %s, %s) returning id"), arguments=('2017-06-30', action, amount))
        print(result)

def send_to_sale_led():
    # one time use only
    result = cf.cursor_(sql.SQL("select date_, name_place, amount from bank.debtor"))
    for a in result:
        sq = "insert into bank.sale_led (type_, date_, name_place, amount) values (%s, %s, %s, %s) returning id"
        with conn() as cursor:
            cursor.execute(sq, ("invoice", a[0], a[1], a[2]))

def send_receipt_to_sale_led():
    # one time use only
    result = cf.cursor_(sql.SQL("select date_, name_place, amount from bank.receipt"))
    for a in result:
        sq = "insert into bank.sale_led (type_, date_, name_place, amount) values (%s, %s, %s, %s) returning id"
        with conn() as cursor:
            cursor.execute(sq, ("receipt", a[0], a[1], a[2]))


def add_year_end_balances():
    # one time use only
    debtors_list = cf.cursor_(sql.SQL("select distinct name_place from bank.debtor"))
    debtors_list = [i[0] for i in debtors_list]
    while True:
        action = cf.prompt_("Enter debtor: ", debtors_list, empty_= "yes")
        if action == "back":
            continue
        if action == "quit":
            break
        amount = cf.prompt_("Enter amount: ", [])
        if amount == "back":
            continue
        if amount == "quit":
            break
        result = cf.cursor_(sql.SQL("insert into bank.debtor (date_, name_place, amount) values (%s, %s, %s) returning id"), arguments=('2017-03-31', action, amount))
        print(result)

def view_ledger():
    debtors_list = cf.cursor_(sql.SQL("select distinct name_place from bank.debtor"))
    debtors_list = [i[0] for i in debtors_list]
    while True:
        action = cf.prompt_("Enter debtor: ", debtors_list, empty_= "yes")
        if action == "back":
            continue
        if action == "quit":
            break
        with conn() as cursor:
            cursor.execute("select date_, invoice_amount, receipt_amount, ts-tr from bank.sale_led_view where name_place = %s", (action, ))
            result = cursor.fetchall()
        columns = ['date','invoice_amount', 'receipt_amount','balance']
        right_align_columns = [ 'invoice_amount', 'receipt_amount', 'balance']
        left_align_columns=['date']
        pt = PrettyTable(columns)
        # pt.set_style(PLAIN_COLUMNS)
        for a in result:
            a0 = cf.reverse_date(str(a[0]))
            if a[1] is None:
                a1 = ''
            else:
                a1 = a[1]
            if a[2] is None:
                a2 = ''
            else:
                a2 = a[2]
            pt.add_row([a0, a1, a2, a[3]])
        pt.align = 'r'
        for l in left_align_columns:
            pt.align[l] = 'l'
        # for r in right_align_columns:
        #     pt.align[r] = 'r'
        print(pt)
        # cf.pretty_table_multiple_rows(columns, result)

def get_options_list(amount):
    result = cf.cursor_(sql.SQL("select name_place from bank.debtor where amount = %s"), arguments=(amount, ))
    return [i[0] for i in result]

if __name__ == "__main__":
    from database import Database, CursorFromConnectionFromPool as conn
    Database.initialise(database='chip', host='localhost', user='dba_tovak', password='j')
    # make_dr_entries()
    try:
        view_ledger()
    except Exception as e:
        print(e)

