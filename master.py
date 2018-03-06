from database import Database, CursorFromConnectionFromPool as conn
from psycopg2 import sql
from prettytable import PrettyTable
import colored
import command_functions as cm
import common_functions as cf
import invoice
import invoice_detail
import money
import owner
import product
import sale_report
import transaction
import money
import os

properties_dict = {
        "product": product.properties,
        "customer": owner.sq_properties,
        "vendor": owner.sq_properties,
        "sale_invoice": invoice.sq_properties,
        "si_detail": invoice_detail.properties_for_update,
        "sale_transaction": transaction.properties,
        "receipt": money.sq_properties,
        "purchase_invoice": invoice.sq_properties,
        "pi_detail": invoice_detail.properties_for_update,
        "purchase_transaction": transaction.properties,
        "payment": money.sq_properties
        }

before_record_count = {}
after_record_count = {}

def save_all_money():
    # saves non_gst money only
    for i in ['receipt', 'payment']:
        with conn() as cursor:
            cursor.execute("select id from {} where gst_invoice_no is null".format(i))
            all_id = cursor.fetchall()
            for a in all_id:
                a = a[0]
                money_ = money.Money(i, id_=a)
                money_.save()


def save_invoice_as_pdf(invoice_type):
    if invoice_type in ["sale_invoice"]:
        transaction_table = "sale_transaction"
    elif invoice_type in ["purchase_invoice"]:
        transaction_table = "purchase_transaction"
    sq = 'select id from {} where id in (select id_invoice from {} where id_invoice is not null)'.format(invoice_type, transaction_table)
    with conn() as cursor:
        cursor.execute(sq)
        all_saved_invoices = cursor.fetchall()
        for a in all_saved_invoices:
            print(a)
            invoice_a = invoice.get_existing_invoice(invoice_type, a[0])
            print(invoice_a)
            # sale_report.create_(invoice_a, 'A6', )
    return all_saved_invoices

def backup(**kwargs):
    backup_folder = os.path.join(cf.project_dir, "backup")
    backup_folder = os.path.join(backup_folder, (cf.get_current_date()).replace("/", "."))
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    temp_name = cf.get_current_timestamp().replace("/", "")
    temp_name = temp_name.replace(":", "")
    temp_name = temp_name.replace(" ", "_")
    print(temp_name)
    master_backup_file_name = "master_" + temp_name + ".pgsql"
    public_backup_file_name = "public_" + temp_name + ".pgsql"
    master_backup_file = os.path.join(backup_folder, master_backup_file_name)
    master_backup_command= 'pg_dump -Fc -U dba_tovak -d chip -h localhost -n master > ' + master_backup_file
    os.system(master_backup_command)
    public_backup_file = os.path.join(backup_folder, public_backup_file_name)
    public_backup_command = 'pg_dump -Fc -U dba_tovak -d chip -h localhost -n public > ' + public_backup_file
    os.system(public_backup_command)
    drop_ = kwargs.get('drop_', '')
    if drop_:
        dropbox(backup_folder)
    return master_backup_file,  public_backup_file

def update_stock(table_, saved_id_table_tuple):
    return None
    assert table_ in ["sale_invoice", "purchase_invoice"]
    if table_ == "sale_invoice":
        detail_table = "si_detail"
    elif table_ == "purchase_invoice":
        detail_table = "pi_detail"
    print('Updating date_ in {}...'.format(detail_table))
    date_sq = "update {} as dt set date_ = (select date_ from {} as t where t.id = dt.id_invoice)".format(detail_table, table_)
    with conn() as cursor:
        cursor.execute(date_sq)
    print("Inserting {} values in stock table...".format(detail_table))
    if detail_table == "si_detail":
# <<<<<<< HEAD
# =======
#         # table_ = sql.SQL('master.') + sql.identifier("stock")
# >>>>>>> 5bcc23706a8fd2a3ca03f355d28ce66ab4c84f0b
        sq = "insert into master.stock (id_si_detail, id_product, product_name, product_unit, qty_sale, date_) select id, id_product, product_name, product_unit, product_qty, date_ from si_detail where si_detail.id_invoice in %s"
        with conn() as cursor:
            cursor.execute(sq, (saved_id_table_tuple, ))
    elif detail_table == "pi_detail":
        sq = "insert into master.stock (id_pi_detail, id_product, product_name, product_unit, qty_purchase, date_) select id, id_product, product_name, product_unit, product_qty, date_ from pi_detail where pi_detail.id_invoice in %s"
        with conn() as cursor:
            cursor.execute(sq, (saved_id_table_tuple, ))


def export(**kwargs):
    only_backup = kwargs.get('only_backup', '')
    public_invoice_total, public_receipt_total = transaction.get_public_totals()
    master_invoice_total_before, master_receipt_total_before, master_opening_balance_before = transaction.get_master_totals()
    master_backup_file, public_backup_file = backup()
    print('finished backup')
    get_before_record_count()
    update_master()
    delete_public()
    get_after_record_count()
    show_summary()
    master_invoice_total, master_receipt_total, master_opening_balance = transaction.get_master_totals()
    pt = PrettyTable(['invoice_total', 'invoice_total_master_before', 'invoice_total_master_after'])
    pt.add_row([public_invoice_total, master_invoice_total_before, master_invoice_total])
    print(pt)
    pt = PrettyTable(['receipt_total', 'receipt_total_master_before', 'receipt_total_master_after'])
    pt.add_row([public_receipt_total, master_receipt_total_before, master_receipt_total])
    print(pt)
    print("Opening Balance: {}".format(master_opening_balance))
    print("Estimated results:\n\tInvoice Total: {}\n\tReceipt Total: {}".format(public_invoice_total+master_invoice_total_before, public_receipt_total+master_receipt_total_before))
    backup(drop_=True)


def update_master():
    # order of tables is very important. Incorrect order leads to key conflicts among tables
    # This is the main reason why saved_id_sale_tuple and ..._purchase_tuple have not been refactored
    add_and_modify_existing("product")
    add_and_modify_existing("customer")
    add_and_modify_existing("vendor")
    print("Product, Customer and Vendor tables have been modified if there were any modifications")
    # add only estimates
    saved_id_sale_tuple = add_saved("sale_invoice")
    if saved_id_sale_tuple:
        try:
            update_stock("sale_invoice", saved_id_sale_tuple)
        except Exception as e:
            print("Failed update_stock")
            print(e)
    add_saved("si_detail")
    add("receipt")
    add("sale_transaction")
    if saved_id_sale_tuple:
        delete_saved_invoice("sale_invoice", saved_id_sale_tuple)
    else:
        print("There are no saved sale invoices")
    saved_id_purchase_tuple = add_saved("purchase_invoice")
    if saved_id_purchase_tuple:
        try:
            update_stock("purchase_invoice", saved_id_purchase_tuple)
        except Exception as e:
            print("Failed update_stock")
            print(e)
    add_saved("pi_detail")
    add("payment")
    add("purchase_transaction")
    if saved_id_purchase_tuple:
        delete_saved_invoice("purchase_invoice", saved_id_purchase_tuple)
    else:
        print("There are no saved purchase invoices")

def delete_public():
    delete_list = ["receipt", "sale_transaction", "payment", "purchase_transaction"]
    for a in delete_list:
        delete_all_records(a)

def delete_saved_invoice(table_, saved_id_tuple):
    with conn() as cursor:
        cursor.execute(sql.SQL("delete from {} where id in %s and gst_invoice_no is null").format(sql.Identifier(table_)), (saved_id_tuple,))

def delete_all_records(table_):
    with conn() as cursor:
        cursor.execute(sql.SQL("delete from {} where gst_invoice_no is null").format(sql.Identifier(table_)))

def add_saved(table_):
    master_table = sql.SQL("master.") + sql.Identifier(table_)
    public_table = sql.SQL("public.") + sql.Identifier(table_)
    if table_ in ["sale_invoice", "si_detail"]:
        transaction_table = "sale_transaction"
        if table_ == "sale_invoice":
            where_field = sql.Identifier("id")
        elif table_ == "si_detail":
            where_field = sql.Identifier("id_invoice")
    elif table_ in ["purchase_invoice", "pi_detail"]:
        transaction_table = "purchase_transaction"
        if table_ == "purchase_invoice":
            where_field = sql.Identifier("id")
        elif table_ == "pi_detail":
            where_field = sql.Identifier("id_invoice")
    result = cf.cursor_(sql.SQL("select distinct id_invoice from {} where gst_invoice_no is null").format(sql.Identifier(transaction_table)))
    saved_id_list = [element for tupl in result for element in tupl if element is not None]
    saved_id_tuple = tuple(saved_id_list)
    if saved_id_tuple:
        with conn() as cursor:
            # source: public.*
            # target: master.*
            # source names are not visible in the update part
            joined = sql.SQL(',').join(sql.SQL('excluded.')+sql.Identifier(n) for n in properties_dict[table_])
            sq = sql.SQL("insert into {} select * from {} where {} in %s returning id").format(master_table, public_table, where_field, sql.SQL(', ').join(sql.Identifier(n) for n in properties_dict[table_]), joined)
            cursor.execute(sq, (saved_id_tuple, ))
            result = cursor.fetchall()
    # print("\nAfter Update")
    # master_count, public_count=show_table_count(master_table, pt=public_table)
    return saved_id_tuple


def add(table_):
    if before_record_count[table_][1] == 0:
        print("There are no records in public.{}".format(table_))
        return
    master_table = sql.SQL("master.") + sql.Identifier(table_)
    public_table = sql.SQL("public.") + sql.Identifier(table_)
    with conn() as cursor:
        # source: public.*
        # target: master.*
        # source names are not visible in the update part
        joined = sql.SQL(',').join(sql.SQL('excluded.')+sql.Identifier(n) for n in properties_dict[table_])
        sq = sql.SQL("insert into {} select * from {} where gst_invoice_no is null returning id").format(master_table, public_table, sql.SQL(', ').join(sql.Identifier(n) for n in properties_dict[table_]), joined)
        cursor.execute(sq)

def add_and_modify_existing(table_):
    master_table = sql.SQL("master.") + sql.Identifier(table_)
    public_table = sql.SQL("public.") + sql.Identifier(table_)
    with conn() as cursor:
        # source: public.*
        # target: master.*
        # source names are not visible in the update part
        cu_joined = sql.SQL(',').join(sql.SQL('excluded.')+sql.Identifier(n) for n in properties_dict[table_])
        sqcu = sql.SQL("insert into {} select * from {} on conflict (id) do update set ({}) = ({}) returning id").format(master_table, public_table, sql.SQL(', ').join(sql.Identifier(n) for n in properties_dict[table_]), cu_joined)
        cursor.execute(sqcu)
    # delete master.customer records which are not in public.customer
    deletions = cf.cursor_(sql.SQL("delete from {} as m where not exists (select * from {} p where m.id = p.id) returning id").format(master_table, public_table))

def show_table_count(table_):
    master_table = sql.SQL("master.") + sql.Identifier(table_)
    public_table = sql.SQL("public.") + sql.Identifier(table_)
    count_master = cf.cursor_(sql.SQL("select count(id) from {}").format(master_table))
    count_public = cf.cursor_(sql.SQL("select count(id) from {}").format(public_table))
    count_master = count_master[0][0] if count_master else 0
    count_public = count_public[0][0] if count_public else 0
    return count_master, count_public

def get_before_record_count():
    global before_record_count
    for table_, value_ in properties_dict.items():
        before_record_count[table_] = show_table_count(table_)

def get_after_record_count():
    global after_record_count
    for table_,value_  in properties_dict.items():
        after_record_count[table_] = show_table_count(table_)

def show_summary():
    columns = ['Table','Before Master', 'After Master', 'Before Public', 'After Public']
    pt = PrettyTable(columns)
    for i in before_record_count:
        bm = before_record_count[i][0]
        am = after_record_count[i][0]
        bp = before_record_count[i][1]
        ap = after_record_count[i][1]
        am = am if am == bm else colored.stylize(am, colored.fg("green"))
        ap = ap if ap == bp else colored.stylize(ap, colored.fg("green"))
        pt.add_row([i, bm, am, bp, ap])
    print(pt)

def dropbox(master_backup_file):
    remote_folder = '/db'
    print('master_backup_file: {}'.format(master_backup_file))
    dropbox_backup = cf.prompt_("Do you want to backup to Dropbox? (y/n): ", ['y', 'n'], default_='y', unique_='existing')
    if dropbox_backup == 'n': return None
    compress_file_name = master_backup_file + ".7z"
    compress_ = "7z a " + compress_file_name + " " + master_backup_file +  " -p"
    print(compress_)
    confirm_ = cf.prompt_("Do you want to run the command? (y/n): ", ['y', 'n'], default_='y', unique_='existing')
    if confirm_ == 'n': return None
    os.system(compress_)
    dropbox_command = "cd ~/git_clones/Dropbox-Uploader/ && ./dropbox_uploader.sh upload " + compress_file_name + " " + remote_folder
    print(dropbox_command)
    confirm_ = cf.prompt_("Do you want to run the command? (y/n): ", ['y', 'n'], default_='y', unique_='existing')
    if confirm_ == 'n': return None
    os.system(dropbox_command)



if __name__ == "__main__":
    backup()
