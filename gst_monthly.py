''' print gst_monthly sale report '''
import os
import csv
import common_functions as cf
from database import Database, CursorFromConnectionFromPool

Database.initialise(database='chip', host='localhost', user='dba_tovak')


def get_starting_date():
    return cf.prompt_("Enter starting date (e.g. 2018-07-1): ",
                               [],
                               default_='2018-03-1')
    # starting_date = starting_date.split(".")
    # starting_date = starting_date[2] + "-" + starting_date[1] + "-" + starting_date[0]

def get_ending_date():
    return cf.prompt_("Enter ending date (e.g. 2018-07-31): ",
                             [], default_='2018-03-31')
    # ending_date = ending_date.split(".")
    # ending_date = ending_date[2] + "-" + ending_date[1] + "-" + ending_date[0]

def get_header():
    return ['GSTIN/UIN of Recipient', 'Invoice Number', 'Invoice date',
            'Invoice Value', 'Place Of Supply', 'Reverse Charge',
            'Invoice Type', 'E-Commerce GSTIN', 'Rate',
            'Taxable Value', 'Freight', 'Recipient Name']

def get_data(starting_date, ending_date):
    report_sq = "select " \
                     "customer.gst_number, " \
                     "sale_invoice.gst_invoice_no, " \
                     "to_char(sale_invoice.date_, 'DD/MM/YYYY'), " \
                     "sale_invoice.amount_after_gst, " \
                     "'27-Maharashtra', " \
                     "'N', " \
                     "'Regular', " \
                     "'', " \
                     "si_detail.product_gst_rate, " \
                     "Round(sum(si_detail.sub_total),2)," \
                     "sale_invoice.freight ," \
                     "sale_invoice.gst_owner_name " \
                     "from sale_invoice " \
                     "join si_detail on \
                     sale_invoice.id = si_detail.id_invoice " \
                     "inner join customer on \
                     sale_invoice.id_owner= customer.id " \
                     "where sale_invoice.date_ <= %s and" \
                     "sale_invoice.date_ >= %s and"  \
                     "gst_invoice_no > 0 " \
                     "group by " \
                     "customer.gst_number, " \
                     "sale_invoice.gst_invoice_no, " \
                     "sale_invoice.date_, " \
                     "sale_invoice.amount_after_gst, "\
                     "si_detail.product_gst_rate, " \
                     "sale_invoice.amount_after_freight, " \
                     "sale_invoice.freight, " \
                     "sale_invoice.gst_owner_name " \
                     "order by sale_invoice.gst_invoice_no"
    with CursorFromConnectionFromPool() as cursor:
        cursor.execute(report_sq, (ending_date, starting_date))
        return cursor.fetchall()

def print_data(report_headers, report_result):
    cf.pretty_(report_headers, report_result)

def write_data(starting_date, ending_date, report_headers, report_result):
    b2b_report_name = "b2b_" + starting_date + "_" + ending_date + ".csv"
    with open(b2b_report_name, 'wt') as f:
        try:
            writer = csv.writer(f)
            writer.writerow(report_headers)
            for i in report_result:
                writer.writerow(i)
            input(" will try to open ")
            os.system('xdg-open ' + b2b_report_name)
        except Exception as e:
            print(e)

def do_():
    starting_date = get_starting_date()
    ending_date = get_ending_date()
    report_headers = get_header()
    report_result = get_data(starting_date, ending_date)
    print_data(report_headers, report_result)
    write_data(starting_date, ending_date, report_headers, report_result)

do_()
