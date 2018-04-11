from database import CursorFromConnectionFromPool as conn
from psycopg2 import sql
import common_functions as cf
import pricelist_functions as plf
import datetime
from decimal import Decimal
import product

properties = ["id_invoice", "id_product",  "product_name", "product_qty", "product_unit", "product_rate", "product_discount", "product_hsn", "product_gst_rate", "sub_total", "product_print_name", "gst_amount", "product_gst_name", "packed"]

properties_for_update = properties[:-1] + ['date_', 'creation_date']

detail_columns = ["name",  "qty", "unit",  "rate", "discount", "sub_total", "product_print_name"]

def get_new_invoice_detail_by_product(invoice_, product_name, product_qty):
    if len(product_name) == 0: return
    invoice_detail_ = InvoiceDetail(invoice_)
    invoice_detail_.product_qty= product_qty
    product_= product.Product.init_by_name(product_name)
    invoice_detail_.product_id = product_.id
    invoice_detail_.product_name = product_.name
    invoice_detail_.product_unit = product_.unit
    if not product_.hsn:
        product_.edit_product_property("hsn")
    invoice_detail_.product_hsn= product_.hsn
    if product_.gst_rate is None:
        product_.edit_product_property("gst_rate")
    invoice_detail_.product_gst_rate= product_.gst_rate
    invoice_detail_.product_print_name = product_.print_name
    print('product_.gst_name: {}'.format(product_.gst_name))
    if not product_.gst_name:
        print('product_.gst_name: {}'.format(product_.gst_name))
        product_.edit_product_property("gst_name")
    else:
        print('product_.gst_name is not None')
    invoice_detail_.product_gst_name = product_.gst_name
    id_pricelist = plf.get_id_pricelist_from_id_product(invoice_detail_.product_id)
    if id_pricelist:
        if invoice_.gst_invoice_no is None:
            product_rate, product_discount = plf.get_pricelist_discount(invoice_, id_pricelist, product_.id)
        else:
            product_rate, product_discount = plf.get_pricelist_discount(invoice_, id_pricelist, product_.id, gst_=True)
    else:
        owner_product = cf.owner_product_from_invoice_type_d[invoice_detail_.invoice_.invoice_type]
        id_owner = invoice_detail_.invoice_.owner.id
        if product_name in ["gst"]:
            product_rate = None
        else:
            if invoice_.gst_invoice_no is None:
                product_rate = get_previous_rate(id_owner, owner_product, invoice_detail_.product_id)
            else:
                product_rate = get_previous_rate(id_owner, owner_product, invoice_detail_.product_id, gst_=True)
        print(id_owner, invoice_detail_.product_id)
        if not product_rate:
            product.get_buy_rate(invoice_detail_.product_name)
            product_rate = cf.prompt_("Enter Product Rate: ", [])
        if invoice_.gst_invoice_no is None:
            invoice_detail_.update_owner_product(owner_product, product_rate)
        else:
            invoice_detail_.update_owner_product(owner_product, product_rate, gst_=True)
        product_discount = None
    invoice_detail_.product_rate = product_rate
    invoice_detail_.product_discount = product_discount
    invoice_detail_.sub_total = invoice_detail_.get_sub_total()
    invoice_detail_.packed = None
    invoice_detail_.id = create_new_invoice_detail_in_db(invoice_detail_)
    if invoice_.invoice_type == "sale_invoice":
        # pass
        set_product_cost(invoice_detail_)
    return invoice_detail_

def update_cost_in_si_detail(invoice_detail_, product_cost):
    cost_sub_total = (Decimal(product_cost) * Decimal(invoice_detail_.product_qty)).quantize(Decimal("1.00"))
    print('cost_sub_total: {}'.format(cost_sub_total))
    cf.psql_("update si_detail set (product_cost, cost_sub_total) = (%s, %s) where id = %s", arg_=(product_cost, cost_sub_total, invoice_detail_.id))

def set_product_cost(invoice_detail_):
    product_cost = product.get_product_cost(invoice_detail_.product_id)
    if not product_cost:
        product.get_buy_rate(invoice_detail_.product_name)
        product_cost = product.ask_cost()
        if not product_cost:
            return
        product.update_cost_in_product(invoice_detail_.product_id, product_cost)
    print("polynomial is {}".format(product_cost))
    update_cost_in_si_detail(invoice_detail_, product_cost)

def get_existing_invoice_detail_by_id(invoice_, id_):
    invoice_detail_ = InvoiceDetail(invoice_)
    invoice_detail_.id = id_
    invoice_detail_properties = get_invoice_detail_properties_from_db(invoice_detail_)
    invoice_detail_.product_id = invoice_detail_properties[1]
    invoice_detail_.product_name = invoice_detail_properties[2]
    invoice_detail_.product_qty = invoice_detail_properties[3]
    invoice_detail_.product_unit = invoice_detail_properties[4]
    invoice_detail_.product_rate = invoice_detail_properties[5]
    invoice_detail_.product_discount = invoice_detail_properties[6]
    invoice_detail_.product_hsn = invoice_detail_properties[7]
    invoice_detail_.product_gst_rate = invoice_detail_properties[8]
    invoice_detail_.sub_total = invoice_detail_properties[9]
    invoice_detail_.product_print_name = invoice_detail_properties[10]
    invoice_detail_.gst_amount = invoice_detail_properties[11]
    invoice_detail_.product_gst_name = invoice_detail_properties[12]
    invoice_detail_.packed = invoice_detail_properties[13]
    return invoice_detail_

def get_invoice_detail_properties_from_db(invoice_detail_):
    cf.log_("db: get_invoice_detail_properties_from_db")
    with conn() as cursor:
        cursor.execute(sql.SQL("select {} from {} where id = %s").format(sql.SQL(', ').join(map(sql.Identifier, properties)), sql.Identifier(invoice_detail_.invoice_detail_type)), (invoice_detail_.id, ))
        return cursor.fetchone()

def create_new_invoice_detail_in_db(invoice_detail_):
    invoice_detail_.gst_amount = (Decimal(invoice_detail_.sub_total) * Decimal( invoice_detail_.product_gst_rate) * Decimal(0.01)).quantize(Decimal("1.00"))
    cf.log_("db: create_new_invoice_detail_in_db")
    sq = "insert into {} (id_invoice, id_product, product_name, product_qty, product_unit, product_rate, product_discount, product_hsn, product_gst_rate, sub_total, product_print_name, packed, gst_amount, product_gst_name) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) returning id".format(invoice_detail_.invoice_detail_type)
    # sq = sql.SQL("insert into {} ({}) values ({}) returning id").format(sql.Identifier(invoice_detail_.invoice_detail_type), sql.SQL(', ').join(map(sql.Identifier, properties)), sql.SQL(', ').join(sql.Placeholder() * len(properties)))
    with conn() as cursor:
        cursor.execute(sq, (
            invoice_detail_.invoice_.id, # 0
                invoice_detail_.product_id, # 1
                invoice_detail_.product_name, # 2
                invoice_detail_.product_qty, # 3
                invoice_detail_.product_unit, # 4
                invoice_detail_.product_rate, # 5
                invoice_detail_.product_discount, # 6
                invoice_detail_.product_hsn, # 7
                invoice_detail_.product_gst_rate, #8
                invoice_detail_.sub_total, # 9
                invoice_detail_.product_print_name, # 10
                invoice_detail_.packed, # 11
                invoice_detail_.gst_amount,
                invoice_detail_.product_gst_name
                )
                )
        return cursor.fetchall()[0]

class InvoiceDetail():

    def __init__(self, invoice_, **kwargs):
        # Access to old invoice_detail can only be had through id since there is no other unique property
        self.invoice_ = invoice_ # invoice object
        self.invoice_detail_type = cf.invoice_detail_type_d[self.invoice_.invoice_type] # si_detail | pi_detail | ...

    def delete_(self):
        with conn() as cursor:
            sq = sql.SQL("with deleted as (delete from {} where id = %s returning *) select count(*) from deleted").format(sql.Identifier(self.invoice_detail_type))
            cursor.execute(sq, (self.id ,))
            result = cursor.fetchone()
            cf.log_("No of deletions: {}".format(result[0]))

    def view_(self):
        if cf.DETAIL_VIEW:
            cf.pretty_table_print(
                    detail_columns,
                    [
                        self.product_name,
                        self.product_qty,
                        self.product_unit,
                        self.product_rate,
                        '' if self.product_discount is None else str(self.product_discount),
                        self.sub_total,
                        self.product_print_name
                    ]
                )

    def update_owner_product(self, owner_product, rate, **kwargs):
        gst_ = kwargs.get('gst_', '')
        previous_rate =get_previous_rate(self.invoice_.owner.id, owner_product, self.product_id, **kwargs)
        rate_date = str(datetime.datetime.today())
        if previous_rate == rate:
            with conn() as cursor:
                cursor.execute(sql.SQL("update {} set (timestamp_) = (%s) where id_owner = %s and id_product = %s and rate = %s").format(sql.Identifier(owner_product)), ( rate_date, self.invoice_.owner.id, self.product_id, rate))
            cf.log_("Updated customer product timestamp_")
        else:
            if gst_:
                with conn() as cursor:
                    cursor.execute(sql.SQL("insert into {} (gst_rate, timestamp_, id_owner, id_product) values (%s, %s, %s, %s)").format(sql.Identifier(owner_product)), (rate, rate_date, self.invoice_.owner.id, self.product_id ))
            else:
                with conn() as cursor:
                    cursor.execute(sql.SQL("insert into {} (rate, timestamp_, id_owner, id_product) values (%s, %s, %s, %s)").format(sql.Identifier(owner_product)), (rate, rate_date, self.invoice_.owner.id, self.product_id ))
            cf.log_("Inserted customer product rate and timestamp_")

    def get_sub_total(self, **kwargs):
        property_ = kwargs.get('property_', '')
        property_value = kwargs.get('property_value', '')
        d_ = {
                "product_rate": self.product_rate,
                "product_qty": self.product_qty,
                "product_discount": self.product_discount
                }
        for a in [*d_]:
            if a == property_:
                d_[a] = property_value
        if d_['product_discount'] not in [None, 0]:
            rate_after_discount = Decimal(d_['product_rate'])*Decimal((1-(Decimal(d_['product_discount'])/100)))
        else:
            rate_after_discount = Decimal(d_['product_rate'])
        return (Decimal(d_['product_qty'])*Decimal(rate_after_discount)).quantize(Decimal("1.00"))

    # not used in this file
    def fetch_old_value(self, property_):
        sq = sql.SQL("select {} from {} where id = %s").format(sql.Identifier(property_), sql.Identifier(self.invoice_detail_type))
        with conn() as cursor:
            cursor.execute(sq, (self.id, ))
            result = cursor.fetchall()
            if len(result) > 1:
                return None
            else:
                return result[0][0]

    def edit_property(self, property_, **kwargs ):
        if property_ in ["packed", "unpack"]:
            old_value = getattr(self, property_)
            if old_value:
                new_value = None
                setattr(self, property_, new_value)
            else:
                new_value = "yes"
                setattr(self, property_, new_value)
            cf.cursor_(sql.SQL("update {} set {} = %s where id = %s returning id").format(sql.Identifier(self.invoice_detail_type), sql.Identifier(property_)), arguments=(new_value, self.id))
            return
        if property_ in ["id", "product_gst_rate"]:
            cf.log_("You cannot change 'id' value")
            return None
        old_value = getattr(self, property_)
        new_value = cf.prompt_("Enter new {} [{}] for {}: ".format(property_, old_value, self.product_name), cf.get_completer_list(property_, self.invoice_detail_type))
        if new_value == "quit": return "quit"
        setattr(self, property_, new_value)
        cf.cursor_(sql.SQL("update {} set {} = %s where id = %s returning id").format(sql.Identifier(self.invoice_detail_type), sql.Identifier(property_)), arguments=(new_value, self.id))
        if property_ in ['product_gst_name']:
            confirm_ = cf.prompt_("Do you want to update the name in Product table?: ", ['y', 'n'], default_ = 'y', unique_='existing')
            if confirm_ == 'y':
                with conn() as cursor:
                    cursor.execute("update product set gst_name = %s where id = %s", (new_value, self.product_id))
        if property_ in ["product_rate", "product_qty", "product_discount"]:
            sub_total = self.get_sub_total(property_=property_, property_value = Decimal(new_value))
            gst_amount = (Decimal(sub_total) * Decimal( self.product_gst_rate) * Decimal(0.01)).quantize(Decimal("1.00"))
            with conn() as cursor:
                cursor.execute(sql.SQL("update {} set ({}, sub_total, gst_amount) = (%s, %s, %s) where id = %s").format(sql.Identifier(self.invoice_detail_type), sql.Identifier(property_)), (new_value, sub_total, gst_amount, self.id))
            setattr(self, "sub_total", sub_total)
            owner_product = cf.owner_product_from_invoice_type_d[self.invoice_.invoice_type]
            self.invoice_.update_invoice_with_sub_total()
            self.update_owner_product(owner_product,self.product_rate, **kwargs)
            self.view_()


def get_previous_rate(id_owner, owner_product, product_id, **kwargs):
    gst_ = kwargs.get('gst_', '')
    if gst_:
        with conn() as cursor:
            cursor.execute(sql.SQL("select rate from {} where id_product = %s and id_owner = %s and rate is not null order by timestamp_ desc ").format(sql.Identifier(owner_product)), (product_id, id_owner))
            result = cursor.fetchone()
        print('non-gst is {}: '.format(result))
        with conn() as cursor:
            cursor.execute(sql.SQL("select gst_rate from {} where id_product = %s and id_owner = %s and gst_rate is not null order by timestamp_ desc ").format(sql.Identifier(owner_product)), (product_id, id_owner))
            result = cursor.fetchone()
    else:
        with conn() as cursor:
            cursor.execute(sql.SQL("select rate from {} where id_product = %s and id_owner = %s and rate is not null order by timestamp_ desc ").format(sql.Identifier(owner_product)), (product_id, id_owner))
            result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None
