import common_functions as cf
from decimal import Decimal
from database import CursorFromConnectionFromPool as conn
from psycopg2 import sql
from psycopg2.extras import execute_values
import datetime
import product

name_dict = {"15": "1/2", "20": "3/4", "25": "1", "32": "1 1/4", "40": "1 1/2", "50": "2", "65": "2 1/2", "80": "3", "100": "4", "125": "5", "150": "6"}

detail_properties = ["id_invoice", "id_product",  "product_name", "product_qty", "product_unit", "product_rate", "product_hsn", "product_gst_rate", "sub_total", "product_print_name"]

class BarrelNipple():
    def __init__(self, input_, invoice_, **kwargs): # input_ = "bn 15 12:48-10 7-5"
        self.invoice_ = invoice_
        self.invoice_type = invoice_.invoice_type
        self.invoice_detail_type = cf.invoice_detail_type_d[self.invoice_type]
        self.owner_product = cf.owner_product_from_invoice_type_d[self.invoice_.invoice_type]
        input_ = input_.split("bn ")[1]
        self.input = input_
        self.main_size = self.get_main_size()
        # print("main size is {}".format(self.main_size))
        self.id_owner = self.invoice_.owner.id
        self.product_name = "Barrel Nipple " + self.main_size
        self.product_= product.Product.init_by_name(self.product_name)
        self.id_product = self.product_.id
        self.rate = self.get_previous_rate(**kwargs)
        if not self.rate:
            self.rate = cf.input_float("Enter Product Rate: ")
            if self.rate != "quit" and self.rate != "back":
                self.insert_owner_product(**kwargs)
        else:
            self.update_timestamp_()
            # self.update_owner_product(**kwargs)
        pq_list = self.parse_input()
            # pq_list = tuple(pq_list)
            # print(pq_list)
        self.insert_records(pq_list)

    def update_timestamp_non_gst_rate(self):
        rate_date = str(datetime.datetime.today())
        with conn() as cursor:
            cursor.execute(sql.SQL("update {} set (timestamp_, rate) = (%s, %s) where id_owner = %s and id_product = %s returning id").format(sql.Identifier(self.owner_product)), ( rate_date, self.rate, self.id_owner, self.id_product))
            result = cursor.fetchall()
            if len(result) == 0:
                return 'fail'
        cf.print_('Updated owner_product non_gst_rate and timestamp_ ')

    def update_timestamp_gst_rate(self):
        rate_date = str(datetime.datetime.today())
        with conn() as cursor:
            cursor.execute(sql.SQL("update {} set (timestamp_, gst_rate) = (%s, %s) where id_owner = %s and id_product = %s").format(sql.Identifier(self.owner_product)), ( rate_date, self.rate, self.id_owner, self.id_product))
        cf.print_('Updated owner_product gst_rate and timestamp_ ')

    def update_timestamp_(self):
        rate_date = str(datetime.datetime.today())
        with conn() as cursor:
            cursor.execute(sql.SQL("update {} set (timestamp_) = (%s) where id_owner = %s and id_product = %s and rate = %s").format(sql.Identifier(self.owner_product)), ( rate_date, self.id_owner, self.id_product, self.rate))
        cf.print_('Updated owner_product timestamp_')

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
        # print(self.input.split(" "))
        return self.input.split(" ")[1:]

    def get_main_size(self):
        return self.input.split(" ")[0]

    def parse_input(self):
        product_qty_list = [] # format: pn-q
        for a in self.input_split_by_spaces():
            if ":" in a:
                product_qty_list = product_qty_list + self.parse_adjacent(a)
            elif "-" in a:
                size = a.split("-")[0]
                qty = a.split("-")[1]
                name = "Barrel Nipple " + self.main_size + " x " + size
                unit = "Nos"
                id_ = self.get_product_id(name, unit)
                print_name = "Barrel Nipple " + name_dict[self.main_size] + " x " + size
                gst_name = print_name
                rate = self.get_product_rate(size)
                sub_total = (Decimal(qty)*Decimal(rate)).quantize(Decimal("1.00"))
                gst_amount = (Decimal(sub_total) * Decimal(0.18) ).quantize(Decimal("1.00"))
                if self.invoice_type == "sale_invoice":
                    cost = product.get_product_cost(id_)
                    if cost:
                        cost_sub_total = Decimal(Decimal(qty)*Decimal(cost)).quantize(Decimal("1.00"))
                    else:
                        cost_sub_total = 0
                    t = (self.invoice_.id, id_, name,  qty, unit, rate, 7307, 18, sub_total, print_name, gst_name, gst_amount, cost, cost_sub_total)
                else:
                    t = (self.invoice_.id, id_, name,  qty, unit, rate, 7307, 18, sub_total, print_name, gst_name, gst_amount)

                product_qty_list.append(t)
            else:
                print("Invalid input: {}".format(a))
        return product_qty_list


    def parse_adjacent(self, data):
        starting_size = data.split(":")[0]
        rest =  data.split(":")[1]
        ending_size = rest.split("-")[0]
        qty = rest.split("-")[1]
        # print("ss is {} and es is {} and qty is {}".format(starting_size, ending_size, qty))
        return self.get_adjacent_data(starting_size, ending_size, qty)

    def get_adjacent_data(self, ss, es, qty):
        adjacent_product_qty = []
        allowed_sizes = [2,3,4,5,6,7,8,9,10,15,18,24,30,36]
        ss = int(ss)
        max_ = int(es)+1
        for i in range(ss, max_):
            remainder = i%12
            if remainder == 0 or i in allowed_sizes:
                name = "Barrel Nipple " + self.main_size + " x " + str(i)
                unit = "Nos"
                id_ = self.get_product_id(name, unit)
                print_name = "Barrel Nipple " + name_dict[self.main_size] + " x " + str(i)
                rate = self.get_product_rate(i)
                sub_total = (Decimal(qty)*Decimal(rate)).quantize(Decimal("1.00"))
                t = (self.invoice_.id, id_, name,  qty, unit, rate, 7307, 18, sub_total, print_name, cost)
                adjacent_product_qty.append(t)
        return adjacent_product_qty

    def insert_owner_product(self, **kwargs):
        gst_ = kwargs.get('gst_', '')
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

    def insert_records(self, t):
        if self.owner_product == "customer_product":
            with conn() as cursor:
                execute_values(cursor, "insert into si_detail (id_invoice, id_product, product_name, product_qty, product_unit, product_rate, product_hsn, product_gst_rate, sub_total, product_print_name, product_gst_name, gst_amount, product_cost, cost_sub_total) values %s", t)
        if self.owner_product == "vendor_product":
            with conn() as cursor:
                execute_values(cursor, "insert into pi_detail (id_invoice, id_product, product_name, product_qty, product_unit, product_rate, product_hsn, product_gst_rate, sub_total, product_print_name, product_gst_name, gst_amount) values %s", t)
                # cursor.execute(sq, t)

    def get_product_id(self, name, unit):
        try:
            result = cf.execute_("insert into {}(name, unit) values (%s, %s) returning id", ["product"], arg_=(name, unit), fetch_="yes")
            return result[0]
        except:
            result = cf.execute_("select id from {} where name = %s", ["product"], arg_=(name,), fetch_="yes")
            return result[0]

    def get_product_rate(self, size):
        size = int(size)
        if size == 2:
            rate = (Decimal(self.rate)/Decimal(12)*Decimal(2.5)).quantize(Decimal("1.00"))
        else:
            rate = (Decimal(self.rate)/Decimal(12)*Decimal(size)).quantize(Decimal("1.00"))
        return rate


def set_owner_product_rate(owner_product, id_product, id_owner, rate, **kwargs):
    rate_date = str(datetime.datetime.today())
    gst_ = kwargs.get('gst_', '')
    if gst_:
        usq = "update {} set (gst_rate, timestamp_) = (%s, %s) where id_owner = %s and id_product = %s returning id".format(owner_product)

        sq = "insert into {} (id_owner, id_product, gst_rate, timestamp_) values (%s, %s, %s, %s) returning id".format(owner_product)
    else:
        usq = "update {} set (rate, timestamp_) = (%s, %s) where id_owner = %s and id_product = %s returning id".format(owner_product)
        sq = "insert into {} (id_owner, id_product, rate, timestamp_) values (%s, %s, %s, %s) returning id".format(owner_product)
    try:
        with conn() as cursor:
            cursor.execute(usq, (rate, rate_date, id_owner, id_product))
            result = cursor.fetchall()
            print(result)
        if len(result) == 0:
            print("Update failed, so inserting...")
            with conn() as cursor:
                cursor.execute(sq, (id_owner, id_product, rate, rate_date))
    except Exception as e:
        print(e)


if __name__ == "__main__":
    input_ = "bn 15 7-5 12-10 15-5"
    print("input_ is {}".format(input_))
    bn =  BarrelNipple(input_)
