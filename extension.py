import common_functions as cf
from decimal import Decimal, ROUND_HALF_UP
from database import Database, CursorFromConnectionFromPool as conn
from psycopg2 import sql
from psycopg2.extras import execute_values
import datetime
import product

name_dict = {"25": "1",  "40": "1 1/2", "50": "2", "65": "2 1/2", "80": "3", "100": "4", "125": "5", "150": "6"}
name_rate_dict = {"25": 1,  "40": 1.5, "50": 2, "65": 2.5, "80": 3, "100": 4, "125": 5, "150": 6}

packing_dict = {"25": 48,  "40": 24, "50": 24, "65": 12, "80": 12, "100": 12, "125": 12, "150": 12}
additional_name_dict = {"regular": "", "h": "Heavy"}

detail_properties = ["id_invoice", "id_product",  "product_name", "product_qty", "product_unit", "product_rate", "product_hsn", "product_gst_rate", "sub_total", "product_print_name"]

class Extension():

    def __init__(self, input_, invoice_): # input_ = "ex [h] 25-4 40-5"
        self.invoice_ = invoice_
        self.invoice_type = invoice_.invoice_type
        self.invoice_detail_type = cf.invoice_detail_type_d[self.invoice_type]
        self.owner_product = cf.owner_product_from_invoice_type_d[self.invoice_type]
        self.input_ = input_.split("ex ")[1]
        self.ext_type= self.get_ext_type()
        self.additional_name = additional_name_dict[self.ext_type]
        # print("main size is {}".format(self.main_size))
        self.id_owner = self.invoice_.owner.id
        self.product_name = "Extension"
        if self.additional_name:
            self.product_name = self.product_name + " " + self.additional_name
        self.product_= product.Product.init_by_name(self.product_name)
        self.id_product = self.product_.id
        self.rate = self.get_previous_rate(**kwargs)
        if not self.rate:
            self.rate = cf.input_float("Enter Product Rate: ")
            if self.rate != "quit" and self.rate != "back":
                self.insert_owner_product(**kwargs)
        else:
            self.update_timestamp_()
        pq_list = self.parse_input()
            # pq_list = tuple(pq_list)
            # print(pq_list)
        self.invoice_detail_id_list = self.insert_records(pq_list)
        print("Extension class finished")

    def update_timestamp_(self):
        now = datetime.datetime.now()
        rate_date = str(datetime.datetime.today())
        with conn() as cursor:
            cursor.execute(sql.SQL("update {} set (timestamp_) = (%s) where id_owner = %s and id_product = %s and rate = %s").format(sql.Identifier(self.owner_product)), ( rate_date, self.id_owner, self.id_product, self.rate))
        cf.print_('Updated owner_product timestamp_')

    def insert_owner_product(self, **kwargs):
        gst_ = kwargs.get('gst_', '')
        now = datetime.datetime.now()
        rate_date = str(datetime.datetime.today())
        if gst_:
            update_fail_pass = self.update_timestamp_gst_rate()
            if update_fail_pass == 'fail':
                with conn() as cursor:
                    cursor.execute("insert into {} (id_owner, id_product, gst_rate, timestamp_) values (%s, %s, %s, %s) returning id".format(self.owner_product), (self.id_owner, self.id_product, self.rate, rate_date))
        else:
            update_fail_pass = self.update_timestamp_non_gst_rate()
            if update_fail_pass == 'fail':
                with conn() as cursor:
                    cursor.execute("insert into {} (id_owner, id_product, rate, timestamp_) values (%s, %s, %s, %s) returning id".format(self.owner_product), (self.id_owner, self.id_product, self.rate, rate_date))

    def get_previous_rate(self, **kwargs):
        gst_ = kwargs.get('gst_')
        gst_result = cf.execute_("select gst_rate from {} where id_product = %s and id_owner = %s order by timestamp_ desc", [self.owner_product], arg_= (self.id_product, self.id_owner), fetch_= "yes")
        print('gst_rate: {}'.format(gst_result))
        non_gst_result = cf.execute_("select rate from {} where id_product = %s and id_owner = %s order by timestamp_ desc", [self.owner_product], arg_= (self.id_product, self.id_owner), fetch_= "yes")
        print('non-gst_rate: {}'.format(non_gst_result))
        if gst_:
            if gst_result:
                return gst_result[0]
        else:
            if non_gst_result:
                return non_gst_result[0]

    def input_split_by_spaces(self):
        if self.additional_name:
        # print(self.input.split(" "))
            return self.input_.split(" ")[1:]
        else:
            return self.input_.split(" ")

    def get_ext_type(self):
        type = self.input_.split(" ")[0] # None | h
        if "-" in type:
            return "regular"
        else:
            return type

    def parse_input(self):
        product_qty_list = [] # format: pn-q
        for a in self.input_split_by_spaces():
            if "-" in a:
                size = a.split("-")[0]
                qty = a.split("-")[1]
                name = self.product_name + " " +  size
                unit = "Nos"
                id_ = self.get_product_id(name, unit)
                print_name = self.product_name + " " + name_dict[size]
                gst_name = print_name
                rate = self.get_product_rate(name_rate_dict[size])
                sub_total = (Decimal(qty)*Decimal(rate)).quantize(Decimal("1.00"))
                gst_amount = (Decimal(sub_total) * Decimal(0.18) ).quantize(Decimal("1.00"))
                t = (self.invoice_.id, id_, name,  qty, unit, rate, 8481, 18, sub_total, print_name, gst_name, gst_amount)
                product_qty_list.append(t)
            else:
                print("Invalid input: {}".format(a))
        return product_qty_list

    def update_owner_product(self):
        now = datetime.datetime.now()
        rate_date = str(datetime.datetime.today())
        properties = ['id_owner', 'id_product', 'rate', 'timestamp_']
        if self.owner_product == "customer_product":
            result = cf.execute_("insert into customer_product ({}) values (%s, %s, %s, %s) returning id", properties, arg_=(self.id_owner, self.id_product, self.rate,rate_date))
        elif self.owner_product == "vendor_product":
            print("Updating vendor_product...")
            result = cf.execute_("insert into vendor_product ({}) values (%s, %s, %s, %s) returning id", properties, arg_=(self.id_owner, self.id_product, self.rate,rate_date))

    def insert_records(self, t):
        if self.owner_product == "customer_product":
            with conn() as cursor:
                execute_values(cursor, "insert into si_detail (id_invoice, id_product, product_name, product_qty, product_unit, product_rate, product_hsn, product_gst_rate, sub_total, product_print_name, product_gst_name, gst_amount) values %s returning id", t)
                result = cursor.fetchall()
        if self.owner_product == "vendor_product":
            print("Inserting pi_detail records...")
            with conn() as cursor:
                execute_values(cursor, "insert into pi_detail (id_invoice, id_product, product_name, product_qty, product_unit, product_rate, product_hsn, product_gst_rate, sub_total, product_print_name, product_gst_name, gst_amount) values %s returning id", t)
                result = cursor.fetchall()
        return result
                # cursor.execute(sq, t)

    def get_product_id(self, name, unit):
        try:
            result = cf.execute_("insert into {}(name, unit) values (%s, %s) returning id", ["product"], arg_=(name, unit), fetch_="yes")
            return result[0]
        except:
            result = cf.execute_("select id from {} where name = %s", ["product"], arg_=(name,), fetch_="yes")
            return result[0]

    def get_product_rate(self, size):
        rate = (Decimal(self.rate)*Decimal(size)).quantize(Decimal("1.00"))
        return rate
def set_owner_product_rate(owner_product, id_product, id_owner, rate, **kwargs):
    now = datetime.datetime.now()
    rate_date = str(datetime.datetime.today())
    properties = ['id_owner', 'id_product', 'rate', 'timestamp_']
    gst_ = kwargs.get('gst_', '')
    if gst_:
        usq = "update {} set (gst_rate, timestamp_) = (%s, %s) where id_owner = %s and id_product = %s returning id".format(owner_product)

        sq = "insert into {} (id_owner, id_product, gst_rate, timestamp_) values (%s, %s, %s, %s) returning id".format(owner_product)
    else:
        usq = "update {} set (rate, timestamp_) = (%s, %s) where id_owner = %s and id_product = %s returning id".format(owner_product)
        sq = "insert into {} (id_owner, id_product, rate, timestamp_) values (%s, %s, %s, %s) returning id".format(owner_product)
    try:
        with conn() as cursor:
            print("rechaeasf")
            cursor.execute(usq, (rate, rate_date, id_owner, id_product))
            result = cursor.fetchall()
            print(result)
        if len(result) == 0:
            print("Update failed, so inserting...")
            with conn() as cursor:
                cursor.execute(sq, (id_owner, id_product, rate, rate_date))
    except Exception as e:
        print(e)
