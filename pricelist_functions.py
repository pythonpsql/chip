from database import Database, CursorFromConnectionFromPool as conn
from psycopg2 import sql, errorcodes
import common_functions as cf
import product
import owner

def get_existing_id_pricelist(name):
    result = cf.cursor_(sql.SQL("select id from pricelist where lower(name) = %s"), arguments= (name.lower(), ))
    if result:
        return result[0][0]
    else:
        return None

def get_id_pricelist_by_name(name):
    result = get_existing_id_pricelist(name)
    if result:
        return result
    else:
        return create_pricelist(name)


def create_pricelist(name):
    result = cf.cursor_(sql.SQL("insert into pricelist (name) values (%s) returning id"), arguments=(name, ))
    return result[0]




def get_id_pricelist_from_id_product(id_product):
    result = cf.cursor_(sql.SQL("select id_pricelist from product_pricelist where id_product = %s"), arguments= (id_product, ))
    if result:
        return result[0][0]
    else:
        return None


def assign_pricelist_to_product():
    pl_last_name = ''
    while True:
        product_name = cf.prompt_("Enter product name: ", cf.get_completer_list("name", "product"), history_file="product_name.txt")
        if product_name == "quit": return "quit"
        if product_name == "back": return "back"
        id_product = product.get_product_details(product_name)[0]
        old_name = ''
        old_value = ''
        with conn() as cursor:
            cursor.execute("select name, value from pricelist as pl join product_pricelist ppl on pl.id=ppl.id_pricelist where ppl.id_product = %s", (id_product, ))
            old_name_result  = cursor.fetchone()
        if old_name_result:
            old_name = old_name_result[0]
            old_value = str(old_name_result[1])
            print("Price List Name is {}".format(old_name))
            print("You cannot edit name or value from here")
            return "back"
        pricelist_name = cf.prompt_("Enter pricelist name: ", cf.get_completer_list("name", "pricelist"), default_=pl_last_name)
        pl_last_name = pricelist_name
        if pricelist_name == "back": return "back"
        if pricelist_name == "quit": return "quit"
        pricelist_value = cf.prompt_("Enter pricelist value: ", [])
        if pricelist_value == "quit": return "quit"
        if pricelist_value == "back": return "back"
        id_pricelist = get_id_pricelist_by_name(pricelist_name)
        with conn() as cursor:
            cursor.execute("insert into product_pricelist (id_product, id_pricelist, value) values (%s, %s, %s) returning id", (id_product, id_pricelist, pricelist_value))


def get_old_pricelist_discount(owner_pricelist, id_owner, id_pricelist, **kwargs):
    gst_ = kwargs.get('gst_', '')
    if gst_:
        result = cf.cursor_(sql.SQL("select gst_discount from {} where id_owner = %s and id_pricelist = %s").format(sql.Identifier(owner_pricelist)), arguments= (id_owner, id_pricelist))
    else:
        result = cf.cursor_(sql.SQL("select discount from {} where id_owner = %s and id_pricelist = %s").format(sql.Identifier(owner_pricelist)), arguments= (id_owner, id_pricelist))
    if result:
        print("old pricelist discount is {}".format(result[0][0]))
        return result[0][0]

def get_old_pricelist_condition(owner_pricelist, id_owner, id_pricelist):
    cf.log_("inside get_old_pricelist_condition")
    reducing_pricelist_id = get_id_pricelist_by_name("GI Fitting Reducing")
    if id_pricelist == reducing_pricelist_id:
        result = cf.cursor_(sql.SQL("select condition from {} where id_owner = %s and id_pricelist = %s").format(sql.Identifier(owner_pricelist)), arguments= (id_owner, id_pricelist))
        if result:
            if result[0][0] in ['reducing', 'non_reducing']:
                return result[0][0]
        condition = cf.prompt_("Enter Condition: ", ['reducing', 'non_reducing'], unique_= "existing")
        if condition:
            set_pricelist_condition(owner_pricelist, id_owner, id_pricelist, condition)
        return condition
    return None

def get_id_pricelist(id_product):
    result = cf.cursor_(sql.SQL("select id_pricelist from product_pricelist where id_product = %s order by version desc limit 1"), arguments=(id_product, ))
    if result:
        return result[0]
    else:
        print("No Price List")
        return None

def set_pricelist_discount(owner_pricelist, id_owner, id_pricelist, discount, **kwargs):
    gst_ = kwargs.get('gst_', '')
    try:
        if gst_:
            cf.cursor_(sql.SQL("insert into {} (id_owner, id_pricelist, gst_discount) values (%s, %s, %s) returning discount").format(sql.Identifier(owner_pricelist)), arguments=(id_owner, id_pricelist, discount))
        else:
            cf.cursor_(sql.SQL("insert into {} (id_owner, id_pricelist, discount) values (%s, %s, %s) returning discount").format(sql.Identifier(owner_pricelist)), arguments=(id_owner, id_pricelist, discount))
    except Exception as e:
        if e.pgcode == '23505':
            print("Updating ...")
            if gst_:
                with conn() as cursor:
                    cursor.execute(sql.SQL("update {} set ( gst_discount ) = (%s) where id_owner = %s and id_pricelist = %s").format(sql.Identifier(owner_pricelist)), (discount,   id_owner, id_pricelist))
            else:
                with conn() as cursor:
                    cursor.execute(sql.SQL("update {} set ( discount ) = (%s) where id_owner = %s and id_pricelist = %s").format(sql.Identifier(owner_pricelist)), (discount,   id_owner, id_pricelist))
        else:
            print(e)

def set_pricelist_condition(owner_pricelist, id_owner, id_pricelist, condition):
    try:
        cf.cursor_(sql.SQL("insert into {} (id_owner, id_pricelist, condition) values (%s, %s, %s) returning condition").format(sql.Identifier(owner_pricelist)), arguments=(id_owner, id_pricelist, condition))
    except Exception as e:
        if e.pgcode == '23505':
            print("Updating ...")
            with conn() as cursor:
                cursor.execute(sql.SQL("update {} set ( condition ) = (%s) where id_owner = %s and id_pricelist = %s").format(sql.Identifier(owner_pricelist)), (condition,   id_owner, id_pricelist))
        else:
            print(e)

# called from start.py
def set_pricelist_discount_for_owner(owner_type, **kwargs):
    big_pricelist_id = get_id_pricelist_by_name("GI Fitting Big")
    reducing_pricelist_id = get_id_pricelist_by_name("GI Fitting Reducing")
    owner_pricelist = cf.owner_pricelist_from_owner_type_d[owner_type]
    id_owner = owner.get_id_from_nickname(owner_type, cf.prompt_("Enter {} Name: ".format(owner_type.title()), cf.get_completer_list("nickname", owner_type)))
    id_pricelist = get_id_pricelist_by_name(cf.prompt_("Enter Price List Name: ", cf.get_completer_list("name", "pricelist")))
    pricelist_discount = get_old_pricelist_discount(owner_pricelist, id_owner, id_pricelist, **kwargs)
    if id_pricelist == reducing_pricelist_id:
        condition = get_old_pricelist_condition(owner_pricelist, id_owner, id_pricelist)
        set_pricelist_condition(owner_pricelist, id_owner, id_pricelist, condition)
    pricelist_discount = cf.prompt_("Enter Discount: ", [], empty="y", default_=str(pricelist_discount))
    set_pricelist_discount(owner_pricelist, id_owner, id_pricelist, pricelist_discount, **kwargs)

def get_pricelist_value(id_product):
    result = cf.cursor_(sql.SQL("select value from product_pricelist where id_product = %s order by version desc limit 1"), arguments=(id_product, ))
    print("pricelist value is {}".format(result[0][0]))
    return result[0][0]

def get_pricelist_discount(invoice_, id_pricelist, id_product, **kwargs):
    big_pricelist_id = get_id_pricelist_by_name("GI Fitting Big")
    reducing_pricelist_id = get_id_pricelist_by_name("GI Fitting Reducing")
    elbow_id = get_id_pricelist_by_name("GI Fitting Elbow")
    id_owner = invoice_.owner.id
    invoice_type = invoice_.invoice_type
    invoice_detail_type = cf.invoice_detail_type_d[invoice_type]
    owner_pricelist = cf.owner_pricelist_from_invoice_type_d[invoice_type]
    condition = get_old_pricelist_condition(owner_pricelist, id_owner, id_pricelist)
    cf.log_("finished get_old_pricelist_condition.\nCondition is {}".format(condition))
    pricelist_discount = get_old_pricelist_discount(owner_pricelist, id_owner, id_pricelist, **kwargs)
    if not pricelist_discount:
        pricelist_discount = cf.prompt_("Enter Discount: ", [])
        set_pricelist_discount(owner_pricelist, id_owner, id_pricelist, pricelist_discount, **kwargs)
        if id_pricelist == reducing_pricelist_id:
            print("Also updating discount of GI Fitting Big pricelist...")
            set_pricelist_discount(owner_pricelist, id_owner, big_pricelist_id,pricelist_discount, **kwargs)
        if id_pricelist == big_pricelist_id:
            print("Also updating discount of GI Fitting Reducing pricelist...")
            condition = get_old_pricelist_condition(owner_pricelist, id_owner, reducing_pricelist_id, **kwargs)
            set_pricelist_condition(owner_pricelist, id_owner, id_pricelist, condition)
            set_pricelist_discount(owner_pricelist, id_owner, reducing_pricelist_id, pricelist_discount, **kwargs)
    if condition:
        if condition == "non_reducing":
            product_name = product.get_product_name_from_id(id_product)
            product_name_for_condition = (product_name.split("Red. ")[1]).split(" X ")[0]
            id_product = product.get_product_details(product_name_for_condition)[0]
            print("Product Name For Condition is {} and its id is {}".format(product_name_for_condition, id_product))
    pricelist_value = get_pricelist_value(id_product)
    if id_pricelist == elbow_id and pricelist_discount < 15:
        pricelist_value = pricelist_discount
        pricelist_discount = 0
    return pricelist_value, pricelist_discount




