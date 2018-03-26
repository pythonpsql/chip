from database import Database, CursorFromConnectionFromPool as conn
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit import prompt
from psycopg2 import sql
from decimal import Decimal, ROUND_HALF_UP
import common_functions as cf
import owner

transaction_type = {"receipt": "sale_transaction", "payment": "purchase_transaction"}

sq_properties = ['id_owner', 'date_', 'amount', 'type', 'recipient', 'medium', 'detail', 'place', 'invoice_no', 'id_transaction', 'gst_invoice_no']


class Money():

    def __init__(self, invoice_type,  **kwargs):
        assert invoice_type in ["receipt", "payment"]
        self.invoice_type = invoice_type # receipt | payment
        self.owner_type = cf.owner_type_d[self.invoice_type] # customer | vendor
        self.id = kwargs.get('id_', '')
        if self.id:
            self.get_invoice_properties(**kwargs)
            print("Invoice exists and id is {}".format(self.id))
        else:
            self.gst_invoice_no = None
            owner_nickname = kwargs.get('nickname', '')
            if not owner_nickname:
                owner_nickname = self.ask_owner_nickname()
            if owner_nickname:
                id_ = owner.get_id_from_nickname(self.owner_type, owner_nickname)
            self.owner = owner.get_existing_owner_by_id(self.owner_type, id_)
            if self.owner:
                self.id_owner = self.owner.id
                self.amount = self.ask_amount()
                if self.amount:
                    self.date_ = get_date()
                    self.recipient, self.medium, self.detail = self.get_detail()
                    if self.recipient:
                        self.id = self.create_new_invoice()
                    make_gst_confirm = cf.prompt_("Make: ", ['y','n'], unique_="existing", empty_="yes")
                    if make_gst_confirm == "y":
                        self.makegst()
                        # self.save()
        cf.log_("Finished Money __init__")

    @classmethod
    def invoice_by_id(cls, invoice_type, id_):
        return cls(invoice_type, id_=id_)

    @classmethod
    def invoice_by_nickname(cls, invoice_type, nickname):
        return cls(invoice_type, nickname=nickname)

    def ask_amount(self):
        amount = cf.prompt_("Enter amount: ", [])
        if amount == "quit": return None
        if amount == "back": return None
        if amount:
            try:
                return int(amount)
            except Exception as e:
                print(e)
                return None

    def get_detail(self):
        if self.owner_type == "customer": temp_ = "vendor"
        if self.owner_type == "vendor": temp_ = "customer"
        vendor_names = cf.get_completer_list("nickname", temp_)
        recipient = cf.prompt_("Enter recipient/payer: ", vendor_names, default_ = "self")
        if recipient in ["quit", "back"]: return None, None, None
        medium = cf.prompt_("Enter medium: ", ['Transfer', 'Cash', 'Cheque', 'Bank Cash', 'Bank Cheque', 'Invoice', 'Adjustment'], empty_="yes", default_="Cash")
        if medium in ["quit", "back"]: return None, None, None
        detail = cf.prompt_("Enter detail: ", [], empty_="yes")
        if detail in ["quit", "back"]: return None, None, None
        return recipient, medium, detail

    # no use in this file, check in others
    def get_id_owner_from_id(self, id_): # id is invoice table id
        result = cf.cursor_(sql.SQL("select id_owner from {} where id = %s").format(sql.Identifier(self.invoice_type)), arguments=(id_, ))
        return result[0][0]

    def ask_owner_nickname(self):
        owner_nickname = cf.prompt_("Enter {} nickname: ".format(self.owner_type), cf.get_completer_list("nickname", self.owner_type))
        if owner_nickname == cf.quit_: return None
        return owner_nickname

    def create_new_invoice(self):
        ''' insert a new record in invoice table and return id '''
        sq = "insert into {} (date_, id_owner, amount, recipient, detail, medium, gst_invoice_no) values (%s,%s, %s, %s, %s, %s, %s) returning id"
        return cf.execute_(sq, [self.invoice_type], arg_=(self.date_, self.id_owner, self.amount, self.recipient, self.detail, self.medium, self.gst_invoice_no), fetch_="y")[0]

    # def get_invoice_no(self):
    #     last_invoice_no = cf.execute_("select max({}) from {}", ["invoice_no"], table_= self.invoice_type, fetch_="y")
    #     # even with fetch_, result is a tuple (None, )
    #     print("last_invoice_no is {}".format(last_invoice_no))
    #     # print below returns (None,) which holds True for
    #     # the statement 'if last_invoice_no'
    #     # print("last_invoice_no is {}.".format(last_invoice_no))
    #     if last_invoice_no[0]:
    #         return int((last_invoice_no[0]) + 1)
    #     else:
    #         invoice_no = int(1)
    #             # for gst
    #             # TODO: update with input_float with int compulsory, also defend for quit and back return values
    #             # invoice_no = input("There are no invoices. Enter starting invoice number: ").strip()
    #     return invoice_no

    def fetch_invoice_details(self, **kwargs):
        master_ = kwargs.get("master_", '')
        if master_:
            cf.log_("reached master_")
            invoice_type = sql.SQL("master.") + sql.Identifier(self.invoice_type)
        else:
            invoice_type = sql.Identifier(self.invoice_type)
        with conn() as cursor:
            cursor.execute(sql.SQL("select r.date_, c.name, r.amount, r.medium, r.recipient, r.detail from {} as r join {} as c on c.id = r.id_owner where r.id = %s").format(invoice_type, sql.Identifier(self.owner_type)), (self.id, ))
            result = cursor.fetchall()
        return result

    def display_header(self):
        print("{}: {}".format(self.invoice_type, self.owner.name))
        cf.pretty_table_print(['Invoice No'], [str(self.invoice_no)])

    def view_invoice_details(self, result):
        if result:
            cf.pretty_table_multiple_rows(["date", "name", "amount", "medium", "recipient", "detail"], result)
        else:
            print("There are no details entered for this invoice")

    def edit_property(self, property_):
        if property_ == "id":
            print("You cannot change 'id' value")
            return None
        old_value = getattr(self, property_)
        new_value = cf.prompt_("Enter new {} [{}]: ".format(property_, old_value ),[], default_=str(old_value))
        if new_value == "q": return "quit"
        setattr(self, property_, new_value)
        cf.cursor_(sql.SQL("update {} set {} = %s where id = %s returning id").format(sql.Identifier(self.invoice_type), sql.Identifier(property_)), arguments=(new_value, self.id))

    def get_invoice_properties(self, **kwargs):
        master_ = kwargs.get("master_", '')
        invoice_type = sql.Identifier(self.invoice_type)
        if master_:
            cf.log_("reached master_")
            if self.invoice_type == "receipt":
                invoice_type = sql.SQL("master.")+sql.Identifier("receipt")
            if self.invoice_type == "payment":
                invoice_type = sql.SQL("master.")+sql.Identifier("payment")
        with conn() as cursor:
            cursor.execute(sql.SQL("select {} from {} where id = %s").format(sql.SQL(', ').join(map(sql.Identifier, sq_properties)), invoice_type), (self.id, ))
            self.invoice_properties = cursor.fetchone()
        # self.invoice_properties = cf.execute_("select {} from {} where {} = %s", sq_properties, table_=invoice_type, where_="id", arg_=(self.id, ), fetch_="y")
        #print("invoice_properties: {}".format(self.invoice_properties))
        self.id_owner = self.invoice_properties[0]
        self.date_ = self.invoice_properties[1]
        self.amount = self.invoice_properties[2]
        self.type = self.invoice_properties[3]
        self.recipient = self.invoice_properties[4]
        self.detail = self.invoice_properties[5]
        self.place = self.invoice_properties[6]
        self.invoice_no = self.invoice_properties[7]
        self.id_transaction = self.invoice_properties[8]
        self.gst_invoice_no = self.invoice_properties[9]
        self.owner = owner.get_existing_owner_by_id(self.owner_type, self.id_owner)
        cf.log_("Finished Money.get_invoice_properties()")

    def delete_(self):
        with conn() as cursor:
            sq = sql.SQL("with deleted as (delete from {} where id = %s returning *) select count(*) from deleted").format(sql.Identifier(self.invoice_type))
            cursor.execute(sq, (self.id ,))
            result = cursor.fetchone()
            print("No of deletions: {}".format(result[0]))

    def save(self):
        # called from master.save_all_money() which ensures that gst invoices are not saved
        with conn() as cursor:
            # excl_amount not required now since this method is only called before export. It was required earlier because it was called during receipt/payment creation
            excl_amount = sql.Composed([sql.SQL('excluded.'), sql.Identifier('amount')])
            sq = sql.SQL("insert into {} (type, id_voucher,id_owner, date_, amount) values (%s, %s, %s, %s, %s) on conflict (id_voucher) do update set amount = {} returning id").format(sql.Identifier(transaction_type[self.invoice_type]), excl_amount)
            cursor.execute(sq, (self.invoice_type, self.id,self.id_owner, self.date_, self.amount))
            result = cursor.fetchone()
        cf.log_("Money Transaction saved")

    def gst_save(self):
        with conn() as cursor:
            # excl_amount not required now since this method is only called before export. It was required earlier because it was called during receipt/payment creation
            excl_amount = sql.Composed([sql.SQL('excluded.'), sql.Identifier('amount')])
            sq = sql.SQL("insert into {} (type, id_voucher,id_owner, date_, amount, gst_invoice_no) values (%s, %s, %s, %s, %s, %s) on conflict (id_voucher) do update set amount = {} returning id").format(sql.Identifier(transaction_type[self.invoice_type]), excl_amount)
            cursor.execute(sq, (self.invoice_type, self.id,self.id_owner, self.date_, self.amount, self.gst_invoice_no))
            result = cursor.fetchone()
        cf.log_("Money Transaction saved")

    def makegst(self):
        if self.gst_invoice_no is not None:
            print('This is already a GST Invoice')
            return
        try:
            self.gst_invoice_no = get_invoice_no(self.invoice_type, gst_=True)
            cf.psql_("update {} set gst_invoice_no = %s where id = %s returning id".format(self.invoice_type), arg_=(self.gst_invoice_no, self.id))
            self.gst_save()
            # gst_invoice = sql.SQL("gst.") + sql.Identifier(self.invoice_type)
            # public_invoice = sql.SQL("public.") + sql.Identifier(self.invoice_type)
            # joined = sql.SQL(', ').join(sql.Identifier(n) for n in sq_properties)
            # excl_joined = sql.SQL(',').join(sql.SQL('excluded.')+sql.Identifier(n) for n in sq_properties)
            # sq = sql.SQL("insert into {} select * from {} where id = %s on conflict(id) do update set ({}) = ({})").format(gst_invoice, public_invoice, joined, excl_joined)
            # cf.psql_(sq, arg_=(self.id, ))
        except Exception as e:
            print(e)

def get_date():
    date_ = cf.prompt_date("Enter Date: ", default_=cf.get_current_date_two())
    if date_ in ["quit", "back"]:
        print("Current date has been set as invoice date")
        return cf.get_current_date_two()
    return date_

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
