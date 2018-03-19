import common_functions as cf
from psycopg2 import sql
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit import prompt
from database import CursorFromConnectionFromPool as conn

# Altering columns in psql shall require alterations in sq_properties and set_properties()

owner_commands_dict = {
        "ai": "All Invoices",
        "oli": "Open Last Invoice",
        "i": "Info",
        "ni": "New Invoice",
        "q": "Quit"
        }

#owner_commands_completer = WordCompleter(commands_list, meta_dict=owner_commands_dict)

sq_properties = ['id', 'name', 'place', 'email_address', 'preferred_transport', 'note', 'address_line_one', 'address_line_two', 'address_line_three', 'contact_one', 'contact_two', 'contact_three', 'gst_number',  'gst_name', 'nickname']

def get_new_owner(owner_type, **kwargs):
    owner_ = Owner(owner_type)
    owner_.nickname = kwargs.get('nickname', '')
    if not owner_.nickname:
        owner_.nickname = cf.prompt_("Enter {} Nickname: ".format(owner_type), cf.get_completer_list("nickname", owner_type), unique_="yes")
    owner_.name = cf.prompt_("Enter {} Name: ".format(owner_type), cf.get_completer_list("name", owner_type), default_=owner_.nickname.title())
    owner_.place = cf.prompt_("Enter {} Place: ".format(owner_type), cf.get_completer_list("place", owner_type))
    owner_.gst_name= cf.prompt_("Enter {} GST Name: ".format(owner_type),[], default_=owner_.name)
    owner_.id = create_new_owner_in_db(owner_)
    return owner_

def create_new_owner_in_db(owner_):
    cf.log_("db: create_new_owner_in_db")
    sq = "insert into {} (name, place, nickname, opening_balance) values (%s, %s, %s, %s) returning id"
    return cf.execute_(sq, [owner_.owner_type], arg_=[owner_.name, owner_.place, owner_.nickname, 0], fetch_="yes")

def get_existing_owner_by_nickname(owner_type, nickname):
    owner_ = Owner(owner_type)
    owner_.nickname = nickname
    owner_properties = get_properties_by_nickname(owner_type, nickname)
    if not owner_properties: return None
    owner_.id, owner_.name, owner_.place, owner_.email_address, owner_.preferred_transport, owner_.note, owner_.address_line_one, owner_.address_line_two, owner_.address_line_three, owner_.contact_one, owner_.contact_two, owner_.contact_three, owner_.gst_number, owner_.gst_name = owner_properties
    return owner_

def get_existing_owner_by_id(owner_type, id_):
    owner_ = Owner(owner_type)
    owner_.id = id_
    owner_properties = get_properties_by_id(owner_type, id_)
    owner_.name, owner_.place, owner_.email_address, owner_.preferred_transport, owner_.note, owner_.address_line_one, owner_.address_line_two, owner_.address_line_three, owner_.contact_one, owner_.contact_two, owner_.contact_three, owner_.gst_number, owner_.nickname, owner_.gst_name = owner_properties
    return owner_

def get_properties_by_nickname(owner_type, nickname):
    return cf.execute_("select {} from {} where {} = %s", sq_properties[:-1], table_=owner_type, where_="nickname", arg_=(nickname, ), fetch_="y")

def get_properties_by_id(owner_type, id_):
    return cf.execute_("select {} from {} where {} = %s", sq_properties[1:], table_=owner_type, where_="id", arg_=(id_, ), fetch_="y")


class Owner():

    def __init__(self, owner_type):
        assert owner_type in ["customer", "vendor"]
        self.owner_type = owner_type

    def display_basic_info(self):
        values_ = [self.id, self.name, self.place, self.contact_one, self.nickname]
        columns_ = ["id", "name", "place", "contact_one", "nickname"]
        cf.pretty_table_print(columns_, values_)

    def set_gst_number(self):
        self.gst_number = cf.prompt_("Enter GST Number for {}: ".format(self.nickname), [], default_="27")
        cf.psql_("update {} set gst_number = %s where id = %s".format(self.owner_type), arg_=(self.gst_number, self.id))

    def set_gst_name(self):
        self.gst_name= cf.prompt_("Enter GST Owner Name for {}: ".format(self.nickname), [], default_=self.name, empty_="yes")
        cf.psql_("update {} set gst_name = %s where id = %s".format(self.owner_type), arg_=(self.gst_name, self.id))
        return self.gst_name

    def edit_properties(self):
        property_ = cf.prompt_("Choose property to edit: ", sq_properties)
        if property_ == "id": return None
        old_value = getattr(self, property_)
        new_value = cf.prompt_("Enter new {} : ".format(property_), [], default_= old_value)
        if old_value == new_value: return None
        if new_value == "quit": return "quit"
        if new_value == "back": return "back"
        if new_value:
            setattr(self, property_, new_value)
            result = cf.cursor_(sql.SQL("update {} set {} = %s where id = %s returning {}").format(sql.Identifier(self.owner_type), sql.Identifier(property_), sql.Identifier(property_)), arguments=(new_value, self.id))

    def set_properties(self):
        self.name, self.place, self.email_address, self.preferred_transport, self.note, self.address_line_one, self.address_line_two, self.address_line_three, self.contact_one, self.contact_two, self.contact_three, self.gst_number, self.nickname, self.gst_name = cf.execute_("select {} from {} where {} = %s", sq_properties, table_=self.owner_type, where_="id", arg_=(self.id, ), fetch_="y")

    def get_owner_invoice(self, invoice_type, **kwargs):
        fetch_ = kwargs.get('fetch_', '') # if empty, fetchall()
        if fetch_:
            result = cf.execute_("select {} from {} where {} = %s order by id desc", ["id"], table_=invoice_type, where_="id_owner", arg_=(self.id, ), fetch_= fetch_)
            if result:
                cf.log_("result is {}".format(result))
                return result[0]
        else:
            filter_type= "All Owner Invoices"
            filter_result = get_filter_result(filter_type, invoice_type, nickname=self.nickname)
            selected_invoice = get_selected_invoice(filter_result, invoice_type)
            if selected_invoice in ["back"]: return "back"
            return selected_invoice

    # used in start.py
def view(invoice_type,  **kwargs):
    filter_type = kwargs.get('filter_type', '')
    owner_type = cf.owner_type_d[invoice_type]
    if not filter_type:
        filter_type = get_invoice_filter_type()
    filter_result = get_filter_result(filter_type,invoice_type)
    cf.log_(filter_result)
    selected_invoice = get_selected_invoice(filter_result, invoice_type)
    if selected_invoice in ["back"]: return "back"
    return selected_invoice

# def get_filter_sql(filter_type, invoice_type):
def get_all_gst_invoices(invoice_type):
    owner_type = cf.owner_type_d[invoice_type]
    transaction_type = cf.transaction_type_d[invoice_type]
    return cf.psql_("select s.gst_invoice_no, s.date_, o.nickname, s.amount_before_freight, s.id from {} as s join {} as o on o.id = s.id_owner where s.gst_invoice_no is not null and gst_invoice_no not in (select gst_invoice_no from {} where gst_invoice_no is not null) order by s.gst_invoice_no desc nulls last".format(invoice_type, owner_type, transaction_type))

def select_gst_invoice_id(result):
    # result requirement:
        # each tuple within result tuple must contain five elements
        # first element must be id
    # return id of invoice
    if len(result) == 1:
        return str(result[0][4])
    for a in result:
        invoice_dict[str(a[0])] = "{}, {}, {}, {}".format(str(a[1]), str(a[2]), str(a[3]), str(a[4]))
    completer = WordCompleter([*invoice_dict], meta_dict = invoice_dict)
    selected_invoice = prompt("Select invoice: ", completer=completer)
    if selected_invoice in ["q", "b"]: return "back"
    return invoice_dict[selected_invoice].split(",")[3].strip()

def get_all_unsaved_invoices(invoice_type):
    owner_type = cf.owner_type_d[invoice_type]
    if invoice_type == "sale_invoice":
        return cf.psql_("select s.date_, o.nickname, s.amount_before_freight, s.id from {} as s join {} as o on o.id = s.id_owner where s.gst_invoice_no is null  and s.id not in (select id_invoice from sale_transaction where id_invoice is not null) order by s.id desc".format(invoice_type, owner_type))
    elif invoice_type == "purchase_invoice":
        return cf.psql_("select s.date_, o.nickname, s.amount_before_freight, s.id from {} as s join {} as o on o.id = s.id_owner where s.gst_invoice_no is null  and s.id not in (select id_invoice from purchase_transaction where id_invoice is not null) order by s.id desc".format(invoice_type, owner_type))

def get_filter_result(filter_type, invoice_type, **kwargs):
    id_ = kwargs.get('id_', '')
    owner_type = cf.owner_type_d[invoice_type]
    owner_nickname = kwargs.get('nickname', '')
    if filter_type == "All Invoices":
        result = cf.cursor_(sql.SQL("select s.invoice_no, s.date_, o.nickname, s.amount_before_freight, s.id from {} as s join {} as o on o.id = s.id_owner where s.gst_invoice_no is not null order by s.id desc").format(sql.Identifier(invoice_type), sql.Identifier(owner_type)))
    elif filter_type == "Unsaved Invoices":
        sq = 'select invoice_no, date_,  owner_name, owner_place, amount_after_freight, id from {} where id not in (select id_invoice from sale_transaction where id_invoice is not null)'.format(invoice_type)
        with conn() as cursor:
            cursor.execute(sq)
            result = cursor.fetchall()
    elif filter_type == "Search By Nickname":
        if not owner_nickname:
            with conn() as cursor:
                cursor.execute("select distinct id_owner from {}".format(invoice_type))
                id_list = cursor.fetchall()
            nickname_list = []
            for a in id_list:
                nickname_list.append(get_nickname_from_id(owner_type,a))
            owner_nickname = cf.prompt_("Enter {} Name: ".format(owner_type), nickname_list, unique_ = "existing")
            # owner_nickname = cf.prompt_("Enter {} Name: ".format(owner_type), cf.get_completer_list("nickname", owner_type))
        if invoice_type in ["receipt", "payment"]:
            result = cf.cursor_(sql.SQL("select r.id, r.date_, c.name, r.amount from {} as r join {} as c on c.id = r.id_owner where c.nickname = %s").format(sql.Identifier(invoice_type), sql.Identifier(owner_type)), arguments=(owner_nickname,))
        else:
            result = cf.cursor_(sql.SQL("select s.invoice_no, s.date_, o.nickname, s.amount_before_freight, s.id from {} as s join {} as o on o.id = s.id_owner where o.nickname = %s order by s.id desc").format(sql.Identifier(invoice_type), sql.Identifier(owner_type)), arguments=(owner_nickname, ))
    elif filter_type == "All Estimates":
        result = cf.cursor_(sql.SQL("select s.invoice_no, s.date_, o.nickname, s.amount_before_freight, s.id from {} as s join {} as o on o.id = s.id_owner where s.gst_invoice_no is null order by s.id desc limit 10").format(sql.Identifier(invoice_type), sql.Identifier(owner_type)))
    elif filter_type == "Last 10 Invoices":
        result = cf.cursor_(sql.SQL("select s.invoice_no, s.date_, o.nickname, s.amount_before_freight, s.id from {} as s join {} as o on o.id = s.id_owner order by s.id desc limit 10").format(sql.Identifier(invoice_type), sql.Identifier(owner_type)))
    elif filter_type == "All Owner Invoices":
        result = cf.cursor_(sql.SQL("select s.invoice_no, s.date_, o.nickname, s.amount_before_freight, s.id from {} as s join {} as o on o.id = s.id_owner where o.nickname = %s order by s.id desc").format(sql.Identifier(invoice_type), sql.Identifier(owner_type)), arguments= (owner_nickname, ))
    return result

# functions to be accessed from outside of class
def get_id_from_nickname(owner_type, nickname, **kwargs):
    no_create = kwargs.get('no_create','')
    sq = "select {} from {} where {} = %s"
    result = cf.execute_(sq, ["id"], table_=owner_type, where_="nickname", arg_=[nickname,], fetch_="y")
    if result: return result[0]
    if no_create: return None
    owner_ = get_new_owner(owner_type, nickname=nickname)
    #result = Owner.create_owner(owner_type, nickname=nickname)
    if owner_: return owner_.id

def get_nickname_from_id(owner_type, id_):
    with conn() as cursor:
        cursor.execute("select nickname from {} where id = %s".format(owner_type), (id_, ))
        return cursor.fetchone()[0]

def get_invoice_filter_type():
    invoice_filter_list = ['Search By Nickname', 'Last 10 Invoices', "All Invoices", "All Estimates"]
    return cf.prompt_("Invoices to show: ", invoice_filter_list)

def get_last_invoice_id(invoice_type):
    with conn() as cursor:
        cursor.execute(sql.SQL("select max(id) from {}").format(sql.Identifier(invoice_type)), ())
        last_invoice_id = cursor.fetchone()[0]
    cf.log_("last invoice id is {}".format(last_invoice_id))
    return last_invoice_id

def get_owner_last_invoice_id(invoice_type, id_owner, **kwargs):
    master_ = kwargs.get('master_','')
    if master_:
        invoice_type = sql.SQL("master.")+sql.Identifier(invoice_type)
    else:
        invoice_type = sql.Identifier(invoice_type)
    with conn() as cursor:
        cursor.execute(sql.SQL("select max(id) from {} where id_owner = %s").format(invoice_type), (id_owner, ))
        last_invoice_id = cursor.fetchone()[0]
    cf.log_("owner last invoice id is {}".format(last_invoice_id))
    return last_invoice_id

def get_selected_invoice(result, invoice_type):
    invoice_dict = {}
    if invoice_type in ["receipt", "payment"]:
        for a in result:
            invoice_dict[str(a[0])] = "{}, {}, {}".format(str(a[1]), str(a[2]), str(a[3]), )
        completer = WordCompleter([*invoice_dict], meta_dict = invoice_dict)
        selected_invoice = prompt("Select invoice: ", completer=completer)
        if selected_invoice in ["q", "b"]: return "back"
        return selected_invoice
    else:
        if len(result) == 1:
            return str(result[0][4])
        for a in result:
            invoice_dict[str(a[0])] = "{}, {}, {}, {}".format(str(a[1]), str(a[2]), str(a[3]), str(a[4]))
        completer = WordCompleter([*invoice_dict], meta_dict = invoice_dict)
        selected_invoice = prompt("Select invoice: ", completer=completer)
        if selected_invoice in ["q", "b"]: return "back"
        return invoice_dict[selected_invoice].split(",")[3].strip()


if __name__ == "__main__":
    from database import Database, CursorFromConnectionFromPool as conn
    Database.initialise(database='chip', host='localhost', user='dba_tovak')
    try:
        o = get_existing_owner_by_nickname("customer", "Kishor Light House")
        o.display_basic_info()
        n = get_new_owner("customer")
        n.display_basic_info()
    except Exception as e:
        print(e)
