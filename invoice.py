from database import CursorFromConnectionFromPool as conn
from prettytable import PrettyTable
from psycopg2 import sql
from decimal import Decimal, ROUND_HALF_UP
import colored
import common_functions as cf
import invoice_detail
import owner

# TODO: Make invoice_no field unique in sale_invoice table

sq_properties = ['id', 'invoice_no', 'date_', 'freight', 'amount_before_freight', 'transport_name', 'transport_lr_no', 'transport_lr_date', 'transport_lr_bags', 'site', 'note', 'memo_type', 'gst_5', 'gst_12', 'gst_18', 'gst_28', 'id_owner', 'amount_after_freight', 'owner_name', 'owner_place', 'amount_after_gst', 'gst_invoice_no', 'gst_owner_name', 'creation_date']

def get_new_invoice(invoice_type, **kwargs):
    invoice_ = Invoice(invoice_type)
    invoice_.owner_type = cf.owner_type_d[invoice_type]
    invoice_.date_ = get_date(invoice_type)
    invoice_.owner = get_invoice_owner(invoice_, nickname=kwargs.get('nickname', ''))
    invoice_.owner_name = invoice_.owner.name
    invoice_.gst_owner_name = invoice_.owner.gst_name
    if invoice_.gst_owner_name is None:
        temp_name = invoice_.owner.set_gst_name()
        invoice_.gst_owner_name = temp_name
    print(invoice_.gst_owner_name)
    invoice_.owner_place = invoice_.owner.place
    invoice_.no_ = get_invoice_no(invoice_type)
    invoice_.freight = 0
    invoice_.gst_invoice_no = None
    invoice_.gst_5 = 0
    invoice_.gst_12 = 0
    invoice_.gst_18 = 0
    invoice_.gst_28 = 0
    invoice_.amount_before_freight = 0
    invoice_.amount_after_freight = 0
    invoice_.amount_after_gst = 0
    invoice_.transport_lr_no = None
    invoice_.memo_type = "credit"
    invoice_.site = None
    invoice_.id = create_new_invoice_in_db(invoice_)
    invoice_.detail_table = cf.invoice_detail_type_d[invoice_type]
    return invoice_

def get_existing_invoice(invoice_type, id_, **kwargs):
    invoice_ = Invoice(invoice_type)
    invoice_.id = id_
    invoice_properties = get_invoice_properties(invoice_type,id_, **kwargs)
    id_owner = invoice_properties[15]
    invoice_.owner_type = cf.owner_type_d[invoice_type]
    invoice_.date_ = invoice_properties[1]
    invoice_.owner = owner.get_existing_owner_by_id(invoice_.owner_type, id_owner)
    invoice_.no_ = invoice_properties[0]
    invoice_.gst_invoice_no = invoice_properties[20]
    invoice_.gst_owner_name = invoice_properties[21]
    print('gst invoice no: {}'.format(invoice_.gst_invoice_no))
    invoice_.freight = invoice_properties[2]
    invoice_.amount_before_freight = invoice_properties[3]
    invoice_.transport_name = invoice_properties[4]
    invoice_.transport_lr_no = invoice_properties[5]
    invoice_.transport_lr_date = invoice_properties[6]
    invoice_.transport_lr_bags = invoice_properties[7]
    invoice_.site = invoice_properties[8]
    invoice_.note = invoice_properties[9]
    invoice_.memo_type= invoice_properties[10]
    invoice_.gst_5 = invoice_properties[11]
    invoice_.gst_12 = invoice_properties[12]
    invoice_.gst_18 = invoice_properties[13]
    invoice_.gst_28 = invoice_properties[14]
    invoice_.amount_after_freight= invoice_properties[16]
    invoice_.owner_name = invoice_properties[17]
    invoice_.owner_place = invoice_properties[18]
    invoice_.amount_after_gst= invoice_properties[19]
    invoice_.detail_table = cf.invoice_detail_type_d[invoice_type]
    return invoice_

def get_invoice_properties(invoice_type, id_, **kwargs):
    cf.log_('get_invoice_properties')
    master_ = kwargs.get('master_', '')
    if master_:
        invoice_table = sql.SQL("master.")+sql.Identifier(invoice_type)
    else:
        invoice_table = sql.Identifier(invoice_type)
    return get_invoice_properties_from_db(invoice_table, id_)

def get_invoice_properties_from_db(invoice_table, id_):
    cf.log_('get_invoice_properties_from_db')
    sq = "select {} from {} where {} = %s"
    csq = sql.SQL(sq).format(sql.SQL(', ').join(map(sql.Identifier, sq_properties[1:][:-1])), invoice_table, sql.Identifier("id"))
    cf.log_("db: get_invoice_properties_from_db")
    with conn() as cursor:
        cursor.execute(csq, (id_, ))
        return cursor.fetchone()

class Invoice():

    def __init__(self, invoice_type,  **kwargs):
        assert invoice_type in ["sale_invoice", "purchase_invoice"]
        master_ = kwargs.get('master_', '')
        self.invoice_type = invoice_type

    def set_freight(self, freight):
        self.freight = freight
        self.set_amount_after_freight()
        cf.cursor_(sql.SQL("update {} set (freight, amount_after_freight) = (%s, %s) where id = %s returning id").format(sql.Identifier(self.invoice_type)), arguments=(self.freight, self.amount_after_freight, self.id))

    def set_amount_after_freight(self):
        # converting None to 0 for calculation
        if not self.freight: self.freight = 0
        if not self.amount_before_freight: self.amount_before_freight= 0
        # called by set_freight, not called directly
        self.amount_after_freight = Decimal(self.amount_before_freight) + Decimal(self.freight)
        self.amount_after_freight = Decimal(self.amount_after_freight.quantize(Decimal("1")))
        cf.cursor_(sql.SQL("update {} set (amount_after_freight) = (%s) where id = %s returning id").format(sql.Identifier(self.invoice_type)), arguments=(self.amount_after_freight, self.id))

    def set_amount_after_gst(self):
        self.gst_5 =  self.get_gst_amount(5)
        self.gst_12 =  self.get_gst_amount(12)
        self.gst_18 =  self.get_gst_amount(18)
        self.gst_28 =  self.get_gst_amount(28)
        freight_gst = (Decimal(self.freight) * Decimal(0.18)).quantize(Decimal("1.00"))
        print('freight_gst: {}'.format(freight_gst))
        total_gst = Decimal(self.gst_5 + self.gst_12 + self.gst_18 + self.gst_28 + freight_gst).quantize(Decimal("1.00"))
        self.amount_after_gst = (self.amount_after_freight + total_gst).quantize(Decimal("1"))
        print('amount_after_gst: {}'.format(self.amount_after_gst))
        cf.cursor_(sql.SQL("update {} set (gst_5, gst_12, gst_18, gst_28, amount_after_gst) = (%s, %s, %s, %s, %s) where id = %s returning id").format(sql.Identifier(self.invoice_type)), arguments=(self.gst_5, self.gst_12, self.gst_18, self.gst_28, self.amount_after_gst, self.id))

    def update_invoice_with_sub_total(self):
        self.set_amount_before_freight()
        self.set_amount_after_freight()
        self.set_amount_after_gst()

    def set_gst_invoice_number(self):
        self.gst_invoice_no= cf.prompt_("Enter GST Invoice No: ", [])
        cf.psql_("update {} set gst_invoice_no = %s where id = %s returning id".format(self.invoice_type), arg_=(self.gst_invoice_no, self.id))

    def set_memo_type(self, type_):
        assert type_ in ["cash", "credit"]
        self.memo_type = type_
        cf.psql_("update {} set memo_type = %s where id = %s".format(self.invoice_type), arg_=(self.memo_type, self.id))

    def makegst(self):
        if self.gst_invoice_no is not None:
            print('This is already a GST Invoice')
            return
        try:
            if self.invoice_type == "sale_invoice":
                self.gst_invoice_no = get_invoice_no(self.invoice_type, gst_=True)
            elif self.invoice_type == "purchase_invoice":
                self.gst_invoice_no = cf.prompt_("Enter GST Invoice No: ", [])
            cf.psql_("update {} set gst_invoice_no = %s where id = %s returning id".format(self.invoice_type), arg_=(self.gst_invoice_no, self.id))
            # gst_invoice = sql.SQL("gst.") + sql.Identifier(self.invoice_type)
            # public_invoice = sql.SQL("public.") + sql.Identifier(self.invoice_type)
            # joined = sql.SQL(', ').join(sql.Identifier(n) for n in sq_properties)
            # excl_joined = sql.SQL(',').join(sql.SQL('excluded.')+sql.Identifier(n) for n in sq_properties)
            # sq = sql.SQL("insert into {} select * from {} where id = %s on conflict(id) do update set ({}) = ({})").format(gst_invoice, public_invoice, joined, excl_joined)
            # cf.psql_(sq, arg_=(self.id, ))
        except Exception as e:
            print(e)


    def fetch_invoice_details_gst(self, **kwargs):
        master_ = kwargs.get("master_", "")
        if master_:
            cf.log_("reached master_")
            if self.invoice_type == "sale_invoice":
                detail_table = sql.SQL("master.")+sql.Identifier("si_detail")
            elif self.invoice_type == "purchase_invoice":
                detail_table = sql.SQL("master.")+sql.Identifier("pi_detail")
        else:
            # self.set_amount_before_freight()
            # self.set_amount_after_freight()
            detail_table = sql.Identifier(self.detail_table)
        with conn() as cursor:
            cursor.execute(sql.SQL("select product_name, product_qty, product_unit, product_rate, product_discount, sub_total, product_print_name, packed, product_hsn, product_gst_rate, gst_amount, product_gst_name from {} where id_invoice = %s order by id").format(detail_table), (self.id, ))
            result = cursor.fetchall()
            cf.log_("fetch_invoice_details completed")
            return result

    def fetch_invoice_details(self, **kwargs):
        master_ = kwargs.get("master_", '')
        gst_ = kwargs.get("gst_", '')
        if master_:
            cf.log_("reached master_")
            if self.invoice_type == "sale_invoice":
                detail_table = sql.SQL("master.")+sql.Identifier("si_detail")
            elif self.invoice_type == "purchase_invoice":
                detail_table = sql.SQL("master.")+sql.Identifier("pi_detail")
        elif gst_:
            cf.log_("reached gst")
            if self.invoice_type == "sale_invoice":
                detail_table = sql.SQL("gst.")+sql.Identifier("si_detail")
            if self.invoice_type == "purchase_invoice":
                detail_table = sql.SQL("gst.")+sql.Identifier("pi_detail")
        else:
            # self.set_amount_before_freight()
            # self.set_amount_after_freight()
            detail_table = sql.Identifier(self.detail_table)
        with conn() as cursor:
            cursor.execute(sql.SQL("select product_name, product_qty, product_unit, product_rate, product_discount, sub_total, product_print_name, packed from {} where id_invoice = %s order by id").format(detail_table), (self.id, ))
            result = cursor.fetchall()
            cf.log_("fetch_invoice_details completed")
            return result

    def fetch_old_value(self,  property_, product_name):
        sq = sql.SQL("select id, {}, qty from {} where product_name = %s and id_invoice = %s").format(sql.Identifier(property_), sql.Identifier(self.detail_table))
        with conn() as cursor:
            cursor.execute(sq, (product_name, self.id))
            result = cursor.fetchall()
            if len(result) > 1:
                cf.log_("There are multiple entries of {} in the current invoice".format(product_name))
            else:
                return result[0][0], result[0][1]

    def get_gst_amount(self, gst_rate):
        with conn() as cursor:
            cursor.execute(sql.SQL("select sum(gst_amount) from {} where id_invoice = %s and product_gst_rate = %s").format(sql.Identifier(self.detail_table)), (self.id, gst_rate ))

            result = cursor.fetchone()

        if not result[0]:
            # print('there is no result')
            cf.log_('get_gst_amount_result is {}'.format(result))
            return 0
        return result[0]

    def get_amount_before_freight(self):
        with conn() as cursor:
            cursor.execute(sql.SQL("select sum(sub_total) from {} where id_invoice = %s").format(sql.Identifier(self.detail_table)), (self.id, ))
            result = cursor.fetchone()
        cf.log_(result)
        if not result:
            return 0
        return result[0]

    def set_amount_before_freight(self):
        self.amount_before_freight = self.get_amount_before_freight()
        try:
            with conn() as cursor:
                cursor.execute(sql.SQL("update {} set (amount_before_freight) = (%s) where id = %s").format(sql.Identifier(self.invoice_type)), (self.amount_before_freight, self.id))
        except Exception as e:
            cf.log_(e)

    def display_header(self):
        print("{}".format(self.invoice_type))
        cf.pretty_table_print(['Date', 'No', 'Name'], [cf.reverse_date(str(self.date_)),str(self.no_), self.owner.name+" ("+self.owner.place+")"])

    def view_invoice_details(self, result, **kwargs):
        all_ = kwargs.get('all_','')
        self.display_header()
        if all_:
            if result:
                view_print(result)
                print("Count: {}".format(len(result)))
        elif len(result) > 5:
            view_print(result[-5:])
            print("Last 5 items have been shown")
        else:
            view_print(result)
        self.display_footer()

    def display_footer(self):
        if not self.freight:
            print("Total: {}".format(self.amount_before_freight))
        else:
            print("Freight: {}".format(self.freight))
            print( "Total: {}".format(self.amount_after_freight))


    def update_invoice_detail(self, edit_id, property_, new_value):
        with conn() as cursor:
            cursor.execute(sql.SQL("update {} set {} = %s where id = %s").format(sql.Identifier(self.detail_table), sql.Identifier(property_)),(new_value, edit_id))


    def delete_(self):
        with conn() as cursor:
            sq = sql.SQL("with deleted as (delete from {} where id = %s returning *) select count(*) from deleted").format(sql.Identifier(self.invoice_type))
            cursor.execute(sq, (self.id ,))
            result = cursor.fetchone()
            cf.log_("No of deletions: {}".format(result[0]))

    def get_detail_table_id(self, product_name, **kwargs):
        packed = kwargs.get('packed', '')
        unpacked = kwargs.get('unpacked', '')
        if packed:
            with conn() as cursor:
                cursor.execute(sql.SQL("select id, product_qty from {} where product_name = %s and id_invoice = %s and packed is null").format(sql.Identifier(self.detail_table)), (product_name, self.id))
        elif unpacked:
            with conn() as cursor:
                cursor.execute(sql.SQL("select id, product_qty from {} where product_name = %s and id_invoice = %s and packed is not null").format(sql.Identifier(self.detail_table)), (product_name, self.id))
        else:
            with conn() as cursor:
                cursor.execute(sql.SQL("select id, product_qty from {} where product_name = %s and id_invoice = %s").format(sql.Identifier(self.detail_table)), (product_name, self.id))
        result = cursor.fetchall()
        if len(result) > 1:
            cf.log_("There are multiple entries of {} in this invoice".format(product_name))
            qty_list = [str(tupl[1]) for tupl in result]
            cf.log_(qty_list)
            # cf.log_(str([tupl[1]) for tupl in result])
            selected_qty = cf.prompt_("Edit {} By Qty: ".format(product_name), qty_list )
            selected_id =([tupl[0] for tupl in result if str(tupl[1]) == selected_qty])
            return selected_id[0]
        else:
            return result[0][0]

    def edit_property(self, property_):
        if property_ == "id":
            cf.log_("You cannot change 'id' value")
            return None
        old_value = getattr(self, property_)
        new_value = cf.prompt_("Enter new {} [{}] : ".format(property_, old_value ),[],default_=str(old_value) )
        setattr(self, property_, new_value)
        cf.cursor_(sql.SQL("update {} set {} = %s where id = %s returning id").format(sql.Identifier(self.invoice_type), sql.Identifier(property_)), arguments=(new_value, self.id))

    def save(self):
        self.validate_before_save()
        transaction_type = {"sale_invoice": "sale_transaction", "purchase_invoice": "purchase_transaction"}
        with conn() as cursor:
            joined = sql.Composed([sql.SQL('excluded.'), sql.Identifier('amount')])
            sq = sql.SQL("insert into {} (type, id_invoice,id_owner, date_, amount) values (%s, %s, %s, %s, %s) on conflict (id_invoice) do update set amount = {} returning id").format(sql.Identifier(transaction_type[self.invoice_type]), joined)
            cursor.execute(sq, (self.invoice_type, self.id,self.owner.id, self.date_, self.amount_after_freight ))
            result = cursor.fetchone()
            cf.log_(result)

    def gst_save(self):
        self.validate_before_save()
        transaction_type = {"sale_invoice": "sale_transaction", "purchase_invoice": "purchase_transaction"}
        with conn() as cursor:
            joined = sql.Composed([sql.SQL('excluded.'), sql.Identifier('amount')])
            sq = sql.SQL("insert into {} (type, id_invoice,id_owner, date_, amount, gst_invoice_no) values (%s, %s, %s, %s, %s, %s) on conflict (id_invoice) do update set amount = {} returning id").format(sql.Identifier(transaction_type[self.invoice_type]), joined)
            cursor.execute(sq, (self.invoice_type, self.id,self.owner.id, self.date_, self.amount_after_freight, self.gst_invoice_no ))
            result = cursor.fetchone()
            cf.log_(result)

    def validate_before_save(self):
        pass

def view_print(result):
    left_align = ["name"]
    right_align = ["qty", "unit", "rate","discount", "sub_total", "product_print_name"]
    pt = PrettyTable(invoice_detail.detail_columns)
    for a in result:
        packed_ = a[-1]
        result = a[:-1]
        a0 = a[0] if not packed_ else colored.stylize(a[0], colored.fg("green"))
        a4 = '' if a [4] is None else a[4]
        pt.add_row([a0, a[1], a[2], a[3], a4, a[5], a[6]])
    if left_align:
        for a in left_align:
            pt.align[a] = "l"
    if right_align:
        for a in right_align:
            pt.align[a] = "r"
    print(pt)

def get_date(invoice_type):
    if invoice_type == "purchase_invoice":
        date_ = cf.prompt_date("Enter Date: ", default_=cf.get_current_date_two())
        if date_ in ["quit", "back"]:
            print("Current date has been set as invoice date")
            return cf.get_current_date_two()
        return date_
    elif invoice_type == "sale_invoice":
        cf.log_("Current date has been set as invoice date")
        return cf.get_current_date_two()


def get_invoice_owner(invoice_, **kwargs):
    owner_nickname = kwargs.get('nickname', '')
    if not owner_nickname:
        owner_nickname = cf.prompt_("Enter {} nickname: ".format(invoice_.owner_type), cf.get_completer_list("nickname", invoice_.owner_type))
    owner_ = owner.get_existing_owner_by_nickname(invoice_.owner_type, owner_nickname)
    # print(owner_.gst_name)

    if not owner_:
        owner_ = owner.get_new_owner(invoice_.owner_type, nickname=owner_nickname)
    return owner_

def get_invoice_no(invoice_type, **kwargs):
    last_invoice_no = get_last_invoice_no_from_db(invoice_type, **kwargs)
    print(last_invoice_no)
    if last_invoice_no:
        return int((last_invoice_no) + 1)
    else:
        return int(1)

def get_last_invoice_no_from_db(invoice_type, **kwargs):
    gst_ = kwargs.get('gst_','')
    if gst_:
        field_ = "gst_invoice_no"
    else:
        field_ = "invoice_no"
    #TODO: lock table here and unlock after inserting in db
    with conn() as cursor:
        cursor.execute("select max({}) from {}".format(field_, invoice_type))
        return cursor.fetchone()[0] # (None, ) is result when its null

def create_new_invoice_in_db(invoice_):
    cf.log_("db: create_new_invoice_in_db")
    sq = "insert into {} (invoice_no, id_owner, owner_name, owner_place, date_, gst_owner_name) values (%s, %s, %s, %s, %s, %s) returning id".format(invoice_.invoice_type)
    with conn() as cursor:
        cursor.execute(sq, (invoice_.no_, invoice_.owner.id, invoice_.owner.name, invoice_.owner.place, invoice_.date_, invoice_.gst_owner_name))
        return cursor.fetchone()[0]


if __name__ == "__main__":
    from database import Database, CursorFromConnectionFromPool as conn
    Database.initialise(database='chip', host='localhost', user='dba_tovak')
    try:
        n = get_new_invoice("sale_invoice")
        print(n.id)
        print(n.no_)
    except Exception as e:
        print(e)

