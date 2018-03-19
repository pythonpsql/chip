from database import Database, CursorFromConnectionFromPool as conn
# from prompt_toolkit.contrib.completers import WordCompleter
from fuzzy_word_completer import WordCompleter
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.completion import generate_completions, display_completions_like_readline
import colored

# from prompt_toolkit.styles import style_from_dict
from psycopg2 import sql
from prettytable import from_db_cursor, PrettyTable
from decimal import Decimal, ROUND_HALF_UP
import datetime
import logging
import os

DETAIL_VIEW = True
project_dir = os.path.dirname(os.path.abspath(__file__))
temp_dir = os.path.join(project_dir, "temp_")
temp_file= os.path.join(temp_dir, "temp.txt")
log_file= os.path.join(temp_dir, "chip.log")
last_history_value = True

quit_ = "quit"
back_ = "back"
# invoice_dict = {"sale": ["customer", "sale_invoice", "si_detail"], "purchase": ["vendor", "purchase_invoice", "pi_detail"]}
# style = style_from_dict({ Token.Toolbar: '#ffffff bg:#333333', })
logging.basicConfig(filename=log_file, format="%(message)s", level = logging.DEBUG)

color_one = colored.fg("green")

style = Style.from_dict({
    '': '#7CFC00',
    # 'title': '#00aa00'
    # 'title': '#FF4500'
    'title': '#808000'
    })

prompt_fragments = [
        ('class:title', 'Enter input: ')
        ]
def log_(text_, **kwargs):
    logging.debug(text_)

def get_current_date():
    # 2017/12/23
    return datetime.datetime.now().strftime('%Y/%m/%d')

def get_current_date_two():
    # 2017-12-23
    return datetime.datetime.now().strftime('%Y-%m-%d')
def get_current_timestamp():
    # 2017-12-23 08:53:09
    return datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

def execute_(sq, identifier_list,  **kwargs):
    arg_ = kwargs.get('arg_', '')
    table_ = kwargs.get('table_', '')
    where_ = kwargs.get('where_', '')
    csq = sql.SQL(sq).format(sql.SQL(', ').join(map(sql.Identifier, identifier_list)), sql.Identifier(table_), sql.Identifier(where_))
    with conn() as cursor:
#        cf.log_(csq.as_string(cursor))
        cursor.execute(csq, (arg_))
        fetch_ = kwargs.get('fetch_', '')
        if fetch_:
            return cursor.fetchone()
        else:
            return cursor.fetchall()

def cursor_(sq, **kwargs):
    arguments = kwargs.get('arguments', '')
    with conn() as cursor:
        cursor.execute(sq.as_string(cursor), arguments)
        return cursor.fetchall()


def get_completer_list(property_, table_):
    ''' returns a list of distinct, non-None values of property_ from table_ '''
    result = cursor_(sql.SQL("select distinct {} from {}").format(sql.Identifier(property_), sql.Identifier(table_)))
    return [str(element) for tupl in result for element in tupl if element is not None]

def get_filtered_completer(property_, table_, where_property, where_value):
    ''' returns a list of non-distinct, non-None values of property_ from table_ subject to a where clause'''
    result = cursor_(sql.SQL("select {} from {} where {} = %s").format(sql.Identifier(property_), sql.Identifier(table_), sql.Identifier(where_property)), (where_value,))
    return [str(element) for tupl in result for element in tupl if element is not None]

def prompt_dict(display_text, dict_, **kwargs):
    list_ = kwargs.get('list_','')
    # invoice_list = kwargs.get('invoice_list','')
    # meta_dict_two=kwargs.get('meta_dict_two','')
    if not list_:
        list_ = [*dict_]
    history_file = (temp_file)
    completer = WordCompleter(list_, ignore_case=True, sentence=True, match_middle=True, meta_dict=dict_, **kwargs )
    prompt_fragments = [
            ('class:title', display_text)
            ]
    while True:
        result = prompt(prompt_fragments, completer=completer, history=FileHistory(history_file), vi_mode=True, style=style, extra_key_bindings=bindings).strip()
        if result == "b":
            raise BackException
        if result:
            break
    return result

class BackException(Exception):
    def __init__(self):
        Exception.__init__(self, "BackException")

bindings = KeyBindings()

@bindings.add("'")
def _(event):
    event.current_buffer.validate_and_handle()

@bindings.add(';')
def _(event):
    generate_completions(event)

@bindings.add(':')
def _(event):
    event.current_buffer.complete_previous()

def prompt_(display_text, completer_list, **kwargs):
    ''' returns non-null [unique] user input.
        User input ':q' returns "quit" '''
    empty_ = kwargs.get('empty_', '')
    history_file = kwargs.get('history', temp_file)
    unique_ = kwargs.get('unique_', 'n')
    default_ = kwargs.get('default_', '')
    completer = WordCompleter(completer_list, ignore_case=True, sentence=True, match_middle=True)
    prompt_fragments = [
            ('class:title', display_text)
            ]
    while True:
        result = prompt(prompt_fragments, completer=completer, history=FileHistory(history_file),  vi_mode=True, default=default_, style=style, extra_key_bindings=bindings).strip()
        if result == "b":
            raise BackException
        if result:
            if unique_ == "existing" and result.lower() not in [x.lower() for x in  completer_list]:
                print("Input must be an existing item")
                continue
            if unique_ == "existing" and result.lower() in [x.lower() for x in  completer_list]:
                break
            elif result.lower() not in [x.lower() for x in completer_list] and unique_ == "y":
                break
            if result not in completer_list or unique_ == "n":
                break
            continue
        elif empty_:
            print("An empty value was entered and allowed")
            break
    return result

def psql_(query, **kwargs):
    arg_ = kwargs.get('arg_', '')
    with conn() as cursor:
        cursor.execute(query, arg_)
        try:
            return cursor.fetchall()
        except Exception as e:
            print(e)
            print('Nothing was returned from psql_ function')

def print_(text):
    print(text)

def input_float(text_, **kwargs):
    empty = kwargs.get('empty', '')
    while True:
        result = input(text_).strip()
        try:
            if result == "q":
                return "quit"
            if result == "b":
                return "back"
            if not result and empty:
                return None
            if not float(result).is_integer:
                result = float(result)
            return result
            break
        except Exception as e:
            print(e)

def prompt_date(text_, **kwargs):
    default_ = kwargs.get('default_', '')
    empty = kwargs.get('empty', '')
    while True:
        result = prompt(text_, default=default_, vi_mode=True).strip()
        try:
            if result == "q":
                return "quit"
            if result == "b":
                return "back"
            if not result and empty:
                return None
            try:
                datetime.datetime.strptime(result, '%Y-%m-%d')
            except Exception as e:
                print(e)
                continue

            return result
            break
        except Exception as e:
            print(e)

def pretty_table_multiple_rows(column_list, result, **kwargs):
    left_align = kwargs.get("left","")
    right_align = kwargs.get("right","")
    pt = PrettyTable(column_list)
    for a in result:
        pt.add_row(a)
    if left_align:
        for a in left_align:
            pt.align[a] = "l"
    if right_align:
        for a in right_align:
            pt.align[a] = "r"
    print(pt)

def pretty_table_print(column_list, result, **kwargs):
    result_t = [str(element) for element in result]
    pt = PrettyTable(column_list, print_empty=False)
    pt.add_row(result_t)
    print(pt)

invoice_detail_type_d = {
        "sale_invoice": "si_detail",
        "purchase_invoice": "pi_detail"
    }

owner_type_d = {
        "sale_invoice": "customer",
        "purchase_invoice": "vendor",
        "receipt": "customer",
        "payment": "vendor"
        }

transaction_type_d = {
        "sale_invoice": "sale_transaction",
        "purchase_invoice": "purchase_transaction",
        }

owner_product_from_invoice_type_d = {
        "sale_invoice": "customer_product",
        "purchase_invoice": "vendor_product"
        }

owner_pricelist_from_invoice_type_d = {
        "sale_invoice": "customer_pricelist",
        "purchase_invoice": "vendor_pricelist"
        }

owner_pricelist_from_owner_type_d = {
        "customer": "customer_pricelist",
        "vendor": "vendor_pricelist"
        }

def reverse_date(i):
    i = i.split("-")
    return i[2] + "-" + i[1] + "-" + i[0]

def clear_screen(**kwargs):
    return
    from os import system
    msg = kwargs.get('msg', '')
    system('clear && printf "\e[3J"')  # on linux
    system('printf "\033c"')  # on linux
    if msg:
        print(msg)

if __name__ == "__main__":
    Database.initialise(database='chips_stack', host='localhost', user='dba_tovak')
