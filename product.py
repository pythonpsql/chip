import common_functions as cf
from psycopg2 import sql
from database import CursorFromConnectionFromPool as conn
import pricelist_functions as plf
from prettytable import PrettyTable
from decimal import Decimal

properties = ['id', 'name', 'unit', 'print_name', 'abbr_name', 'product_group', 'hsn', 'gst_rate', 'gst_name']
check_name = "select {} from product where lower(name) = %s"
check_abbr = "select {} from product where lower(abbr_name) = %s"
check_list = [check_name, check_abbr]

class Product():

    def __init__(self, name, unit):
        self.name = name
        self.unit = unit
        self.set_properties()

    @classmethod
    def init_by_name(cls, name):
        for check_ in check_list:
            result = cf.execute_(check_, properties, arg_= (name.lower(), ), fetch_='yes')
            if result:
                return cls(result[1], result[2])
        name, unit = create_product(name)
        if name == "quit": return "quit"
        return cls(name, unit)

    def set_properties(self):
        try:
            self.id, self.name, self.unit, self.print_name, self.abbr_name, self.product_group, self.hsn, self.gst_rate, self.gst_name = get_product_details(self.name)
        except TypeError:
            result = create_product(self.name)
            if result[0] == "quit":
                cf.log_("No new product was created")
                return
            self.id, self.name, self.unit, self.print_name, self.abbr_name, self.product_group, self.hsn, self.gst_rate, self.gst_name = get_product_details(name)

    def edit_product_property(self, property_):
        if property_ == "id":
            cf.log_("You cannot change 'id' of the product")
            return None
        old_value = getattr(self, property_)
        new_value = cf.prompt_("Enter new {} for {}: ".format(property_, self.name), cf.get_completer_list(property_, "product"), default_=old_value, empty_="yes")
        if old_value == new_value: return None
        setattr(self, property_, new_value)
        try:
            cf.execute_("update product set {} = %s where id = %s returning id", [property_], arg_=(new_value, self.id))
        except Exception as e:
            print(e)

def ask_cost():
    cost_before_discount = cf.prompt_("Enter cost: ", [], empty_='yes')
    discount = cf.prompt_("Enter discount: ", [], empty_='yes')
    transport_cost = cf.prompt_("Enter Transport Cost: ", [], empty_='yes')
    if discount:
        cost = (Decimal(cost_before_discount) * Decimal(1 - discount/100)).quantize(Decimal("1.00"))
    else:
        cost = cost_before_discount
    final_cost = cost + transport_cost
    print('finishing ask_cost...')
    return cost, final_cost

def get_previous_cost(id_product):
    return cf.psql_("select cost from product where id = %s", arg_= (id_product, ))

def update_cost_in_product(id_product, cost, final_cost):
    timestamp_ = cf.get_current_timestamp()
    cf.psql_("update product set (purchase_cost, cost, timestamp_) = (%s, %s,%s) where id = %s", arg_=(cost, final_cost, timestamp_, id_product))

def get_product_cost(id_product):
    previous_cost = get_previous_cost(id_product)
    if previous_cost[0][0]:
        return previous_cost[0][0]
    else:
        return None

def get_product_name_from_id(id_):
    with conn() as cursor:
        cursor.execute("select name from product where id = %s",(id_, ))
        return cursor.fetchone()[0]

def get_id_from_name(name):
    with conn() as cursor:
        cursor.execute("select id from product where name = %s",(name, ))
        return cursor.fetchone()[0]

def get_product_details(name):
    ''' return product details from name, if unsuccessful then try abbr, if still unsuccessful return None (default) '''
    for check_ in check_list:
        result = cf.execute_(check_, properties, arg_= (name.lower(), ), fetch_='yes')
        if result:
            return result

def create_product(name):
    unit = cf.prompt_("Enter {} Unit: ".format(name),cf.get_completer_list("unit", "product"), history_file=None, default_="Nos")
    if unit == "quit": return "quit", "quit"
    if unit == "back": return "back", "back"
    abbr_name = cf.prompt_("Enter {} abbr: ".format(name),cf.get_completer_list("abbr_name", "product"), history_file=None, unique_="y", empty_="y")
    if abbr_name == "quit": return "quit", "quit"
    if abbr_name == "back": return "back", "back"
    print_name = cf.prompt_("Enter {} print_name: ".format(name),cf.get_completer_list("print_name", "product"), history_file=None, unique_="y", empty_="y", default_=name)
    if print_name == "quit": return "quit", "quit"
    if print_name == "back": return "back", "back"
    result = cf.execute_("insert into {} (name, unit, abbr_name, print_name) values (%s, %s, %s, %s) returning name, unit, id", ["product"], arg_= (name, unit, abbr_name, print_name), fetch_="yes")
    id_ = result[2]
    cf.log_("New Product ({}) was created".format(result[0]))
    pricelist = cf.prompt_("Enter {} price_list: ".format(name),cf.get_completer_list("name", "pricelist"), empty_="y")
    if pricelist == "quit": return "quit", "quit"
    if pricelist == "back": return "back", "back"
    if pricelist:
        id_pricelist= plf.get_id_pricelist_by_name(pricelist)
        pricelist_value = cf.prompt_("Enter pricelist value: ", [])
        if pricelist_value == "quit": return "quit"
        if pricelist_value == "back": return "back"
        with conn() as cursor:
            cursor.execute("insert into product_pricelist (id_product, value, id_pricelist) values (%s, %s, %s)", (id_, pricelist_value, id_pricelist))
    return [result[0], result[1]]

def delete_product(name):
    with conn() as cursor:
        sq = "with deleted as (delete from product where lower(name) = %s returning *) select count(*) from deleted"
        cursor.execute(sq, (name.lower(), ))
        result = cursor.fetchone()
        cf.log_("No of products deleted: {}".format(result[0]))

def set_property(property_, by_name=False):
    if by_name:
        name = cf.prompt_("Enter product name: ", cf.get_completer_list("name", "product"), unique_="existing")
        if name in ["quit", "back"]: return "back"
        cf.log_(name)
        old_value = cf.execute_("select {} from {} where lower({})= %s", [property_], table_="product",  where_="name",  arg_=(name.lower(),), fetch_="yes")
        old_value = old_value[0]
        if old_value == None: old_value = ""
        new_value = cf.prompt_("{} for {}: ".format(property_, name), [], default_=old_value)
        if new_value == "quit": return "back"
        if new_value == "back": return "back"
        if new_value == "s": return "back" # only for consistency with bulk abbreviate
        if old_value == new_value: return "back"
        cf.log_(cf.execute_("update product set {} = %s where name = %s returning id", [property_],  arg_=(new_value, name)))
        return "back"
    result = cf.cursor_(sql.SQL("select name from product where {} is null order by id desc").format(sql.Identifier(property_)))
    name_list = [element for tupl in result for element in tupl]
    for name in name_list:
        new_value = cf.prompt_("{} for {}: ".format(property_, name), [])
        if new_value == "quit": return "quit"
        if new_value == "back": return "back"
        if new_value == "s": continue
        cf.log_(cf.cursor_(sql.SQL("update product set {} = %s where name = %s returning id").format(sql.Identifier(property_)), arguments=(new_value, name)))


def get_owner_product_dict(owner_product, id_owner):
    with conn() as cursor:
        sq = "select * from ( select  p.name, cast(o.rate as text), date(o.timestamp_) as tt from product as p  left outer join {} as o on p.id = o.id_product and o.id_owner = %s order by  o.timestamp_ desc nulls last) whatever order by whatever.tt desc nulls last ".format(owner_product)
        cursor.execute(sq, (id_owner, ))
        result = cursor.fetchall()
        # print(result)

    # result = cf.cursor_(sql.SQL("select p.name, cast(o.rate as text), date(timestamp_) from product as p inner join {} as o on p.id = o.id_product and o.id_owner = %s order by o.timestamp_ desc nulls last").format(sql.Identifier(owner_product)), arguments=(id_owner, ))
    if not result: return None
    result = [(v[0], '') if v[1] is None else (v[0],v[1]+" "+str( v[2])) for v in result]
    # cf.log_(result)
    # convert tuple to dictionary
    product_dict = dict(result)
    product_list_sorted = [v[0] for v in result]
    # product_list_sorted = sorted(product_list, key=product_list.get, reverse=True)
    return product_list_sorted, product_dict

def get_owner_product_abbr_dict(owner_product, id_owner):
    result = cf.cursor_(sql.SQL("select p.abbr_name, cast(o.rate as text), date(timestamp_), p.name from {} as o right outer join product as p on p.id = o.id_product and o.id_owner = %s where p.abbr_name is not null order by o.timestamp_ desc nulls last").format(sql.Identifier(owner_product)), arguments=(id_owner, ))
    if not result: return None
    result = [(v[0], v[3]) if v[1] is None else (v[0],v[1]+" ("+v[3]+") " +str( v[2])) for v in result]
    # cf.log_(result)
    # convert tuple to dictionary
    # cf.log_(result)
    product_dict = dict(result)
    product_list_sorted = [v[0] for v in result]
    # product_list_sorted = sorted(product_list, key=product_list.get, reverse=True)
    # cf.log_(product_list_sorted)
    # cf.log_(product_list)
    return product_list_sorted, product_dict

def get_buy_rate(product_name):
    with conn() as cursor:
        cursor.execute("select * from temp_vendor_product where lower(product_name) like %s order by timestamp_ desc", (product_name.lower(), ))
        r = cursor.fetchall()
        pt = PrettyTable(['name', 'owner', 'date', 'rate', 'discount'])
        for a in r:
            pt.add_row(a)
        print(pt)



if __name__ == "__main__":
    from database import Database
    Database.initialise(database='chips_stack', host='localhost', user='dba_tovak')
    name="Topman Tarrim Two Way Angle"
    unit="Nos"
    p = Product(name, unit)
    cf.log_(p.name)
    x = Product.init_by_name("Society Short Body")
    cf.log_(x.name)
    cf.log_(x.unit)
    x.edit_product_property("unit")
    cf.log_(x.unit)
