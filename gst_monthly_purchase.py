
''' print gst_monthly sale report '''
import os
import csv
import common_functions as cf
from database import Database, CursorFromConnectionFromPool

Database.initialise(database='chip', host='localhost', user='dba_tovak')


def get_starting_date():
    return cf.prompt_("Enter starting date (e.g. 2018-03-1): ",
                               [],
                               default_='2018-03-1')
    # starting_date = starting_date.split(".")
    # starting_date = starting_date[2] + "-" + starting_date[1] + "-" + starting_date[0]

def get_ending_date():
    return cf.prompt_("Enter ending date (e.g. 2018-03-31): ",
                             [], default_='2018-03-31')
    # ending_date = ending_date.split(".")
    # ending_date = ending_date[2] + "-" + ending_date[1] + "-" + ending_date[0]

def get_header():
    return ['GSTIN/UIN of Recipient', 'Invoice Number', 'Invoice date',
            'Invoice Value', 'Place Of Supply', 'Reverse Charge',
            'Invoice Type', 'E-Commerce GSTIN', 'Rate',
            'Taxable Value', 'Freight']

def get_data(starting_date, ending_date):
    report_sq = "select " \
                     "vendor.gst_number, " \
                     "purchase_invoice.gst_invoice_no, " \
                     "to_char(purchase_invoice.date_, 'DD/MM/YYYY'), " \
                     "purchase_invoice.amount_after_gst, " \
                     "'27-Maharashtra', " \
                     "'N', " \
                     "'Regular', " \
                     "'', " \
                     "pi_detail.product_gst_rate, " \
                     "Round(sum(pi_detail.sub_total),2)," \
                     "purchase_invoice.freight " \
                     "from purchase_invoice " \
                     "join pi_detail on \
                     purchase_invoice.id = pi_detail.id_invoice " \
                     "inner join vendor on \
                     purchase_invoice.id_owner= vendor.id " \
                     "where purchase_invoice.date_ <= %s and \
                     purchase_invoice.date_ >= %s " \
                     "group by " \
                     "vendor.gst_number, " \
                     "purchase_invoice.gst_invoice_no, " \
                     "purchase_invoice.date_, " \
                     "purchase_invoice.amount_after_gst, "\
                     "pi_detail.product_gst_rate, " \
                     "purchase_invoice.amount_after_freight, " \
                     "purchase_invoice.freight " \
                     "order by purchase_invoice.date_"
    with CursorFromConnectionFromPool() as cursor:
        cursor.execute(report_sq, (ending_date, starting_date))
        return cursor.fetchall()

def print_data(report_headers, report_result):
    cf.pretty_(report_headers, report_result)

def write_data(starting_date, ending_date, report_headers, report_result):
    b2b_report_name = "b2b_purchase_" + starting_date + "_" + ending_date + ".csv"
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
#         elif layout == "GST Report Purchase":
#             try:
#                 # starting_date = "2017-7-1"
#                 # ending_date = "2017-7-31"
#                 starting_date = input(colored.blue("Enter starting date (e.g. 1.7.2017): ")).strip()
#                 starting_date = starting_date.split(".")
#                 starting_date = starting_date[2] + "-" + starting_date[1] + "-" + starting_date[0]
#                 ending_date = input(colored.blue("Enter ending date (e.g. 31.7.2017): ")).strip()
#                 ending_date = ending_date.split(".")
#                 ending_date = ending_date[2] + "-" + ending_date[1] + "-" + ending_date[0]
#                 sq = "select " \
#                      "to_char(date, 'DD.MM.YY'), " \
#                      "invoice_no, " \
#                      "gst, " \
#                      "concat(purchase_invoice.name,  ' (', purchase_invoice.place,  ')') as name, " \
#                      "Round((amount_before_tax + coalesce(freight,0)),2), " \
#                      "cgst9_taxable_amount, " \
#                      "sgst9_taxable_amount, " \
#                      "igst9_taxable_amount, " \
#                      "cgst9_amount, " \
#                      "sgst9_amount, " \
#                      "Round((igst9_amount*2),2), " \
#                      "cgst14_taxable_amount," \
#                      "sgst14_taxable_amount, " \
#                      "igst14_taxable_amount, " \
#                      "cgst14_amount, " \
#                      "sgst14_amount, " \
#                      "Round((igst14_amount*2),2)," \
#                      "Round(total_amount_after_gst,2) " \
#                      "from purchase_invoice inner join vendor on vendor.name = purchase_invoice.name " \
#                      "where date <= %s and date >= %s " \
#                      "order by purchase_invoice.date"
#                 with CursorFromConnectionFromPool() as cursor:
#                     cursor.execute(sq, (ending_date, starting_date))
#                     transaction_report = cursor.fetchall()
#                 headers_list = ['Date', 'Invoice No', 'GST IN', 'Name', 'Amount Before Tax',
#                                 'CGST 9 Taxable Amount', 'SGST 9 Taxable Amount', 'IGST 18 Taxable Amount',
#                                 'CGST 9 Amount', 'SGST 9 Amount', 'IGST 18 Amount',
#                                 'CGST 14 Taxable Amount', 'SGST 14 Taxable Amount', 'IGST 28 Taxable Amount',
#                                 'CGST 14 Amount', 'SGST 14 Amount', 'IGST 28 Amount', 'Total Amount after GST']
#                 # print(tabulate(purchase_report,
#                 #                headers=headers_list,
#                 #                showindex=range(1, len(purchase_report) + 1),
#                 #                tablefmt="psql"))
#                 import csv
#                 import sys

#                 with open("purchase_report.csv", 'wt') as f:
#                     try:
#                         writer = csv.writer(f)
#                         writer.writerow(headers_list)
#                         for i in range(len(transaction_report)):
#                             writer.writerow((str(transaction_report[i][0]),
#                                              str(transaction_report[i][1]),
#                                              str(transaction_report[i][2]),
#                                              str(transaction_report[i][3]),
#                                              str(transaction_report[i][4]),
#                                              str(transaction_report[i][5]),
#                                              str(transaction_report[i][6]),
#                                              str(transaction_report[i][7]),
#                                              str(transaction_report[i][8]),
#                                              str(transaction_report[i][9]),
#                                              str(transaction_report[i][10]),
#                                              str(transaction_report[i][11]),
#                                              str(transaction_report[i][12]),
#                                              str(transaction_report[i][13]),
#                                              str(transaction_report[i][14]),
#                                              str(transaction_report[i][15]),
#                                              str(transaction_report[i][16]),
#                                              str(transaction_report[i][17])
#                                              ))
#                         import os

#                         if os.name == "nt":
#                             os.system('start ' + "purchase_report.csv")
#                         else:
#                             os.system('libreoffice ' + "purchase_report.csv")
#                     except Exception as e:
#                         print(e)
#                 sq = "select " \
#                      "Round(sum(amount_before_tax+ freight),2)," \
#                      "Round((sum(cgst9_amount)+sum(cgst14_amount)),2)," \
#                      "Round((sum(sgst9_amount)+sum(sgst14_amount)),2)," \
#                      "Round((sum(igst9_amount*2)+sum(igst14_amount*2)),2)," \
#                      "Round(sum(total_amount_after_gst),2) " \
#                      "from purchase_invoice where date <= %s and date >= %s"
#                 with CursorFromConnectionFromPool() as cursor:
#                     cursor.execute(sq, (ending_date, starting_date))
#                     summary_report = cursor.fetchall()
#                 headers_list = ['Amount Before GST', 'CGST', 'SGST', 'IGST', 'Amount After GST']
#                 import csv
#                 import sys

#                 with open("purchase_report_summary.csv", 'wt') as f:
#                     try:
#                         writer = csv.writer(f)
#                         writer.writerow(headers_list)
#                         for i in range(len(summary_report)):
#                             writer.writerow((str(summary_report[i][0]),
#                                              str(summary_report[i][1]),
#                                              str(summary_report[i][2]),
#                                              str(summary_report[i][3]),
#                                              str(summary_report[i][4])
#                                              ))
#                             import os

#                             if os.name == "nt":
#                                 os.system('start ' + "purchase_report_summary.csv")
#                             else:
#                                 os.system('libreoffice ' + "purchase_report_summary.csv")
#                     except Exception as e:
#                         print(e)
#                 get_response = input(colored.blue("Press b to go back: ")).strip()
#                 if get_response == "b":
#                     layout = get_layout()
#                     continue

#             except Exception as e:
#                 print(e)
#                 get_response = input(colored.blue("Press b to go back: ")).strip()
# ''' print gst_monthly sale report '''
# import os
# import csv
# import common_functions as cf
# from database import Database, CursorFromConnectionFromPool

# Database.initialise(database='chip', host='localhost', user='dba_tovak')


# def get_starting_date():
#     return cf.prompt_("Enter starting date (e.g. 2018-07-1): ",
#                                [],
#                                default_='2018-07-1')
#     # starting_date = starting_date.split(".")
#     # starting_date = starting_date[2] + "-" + starting_date[1] + "-" + starting_date[0]

# def get_ending_date():
#     return cf.prompt_("Enter ending date (e.g. 2018-07-31): ",
#                              [], default_='2018-07-12')
#     # ending_date = ending_date.split(".")
#     # ending_date = ending_date[2] + "-" + ending_date[1] + "-" + ending_date[0]

# def get_header():
#     return ['GSTIN/UIN of Recipient', 'Invoice Number', 'Invoice date',
#             'Invoice Value', 'Place Of Supply', 'Reverse Charge',
#             'Invoice Type', 'E-Commerce GSTIN', 'Rate',
#             'Taxable Value', 'Freight']

# def get_data(starting_date, ending_date):
#     report_sq = "select " \
#                      "vendor.gst_number, " \
#                      "purchase_invoice.gst_invoice_no, " \
#                      "to_char(purchase_invoice.date_, 'DD/MM/YYYY'), " \
#                      "purchase_invoice.amount_after_gst, " \
#                      "'27-Maharashtra', " \
#                      "'N', " \
#                      "'Regular', " \
#                      "'', " \
#                      "pi_detail.product_gst_rate, " \
#                      "Round(sum(pi_detail.sub_total),2)," \
#                      "purchase_invoice.freight " \
#                      "from purchase_invoice " \
#                      "join pi_detail on \
#                      purchase_invoice.id = pi_detail.id_invoice " \
#                      "inner join vendor on \
#                      purchase_invoice.id_owner= vendor.id " \
#                      "where purchase_invoice.date_ <= %s and \
#                      purchase_invoice.date_ >= %s " \
#                      "group by " \
#                      "vendor.gst_number, " \
#                      "purchase_invoice.gst_invoice_no, " \
#                      "purchase_invoice.date_, " \
#                      "purchase_invoice.amount_after_gst, "\
#                      "pi_detail.product_gst_rate, " \
#                      "purchase_invoice.amount_after_freight, " \
#                      "purchase_invoice.freight " \
#                      "order by purchase_invoice.gst_invoice_no"
#     with CursorFromConnectionFromPool() as cursor:
#         cursor.execute(report_sq, (ending_date, starting_date))
#         return cursor.fetchall()

# def print_data(report_headers, report_result):
#     cf.pretty_(report_headers, report_result)

# def write_data(starting_date, ending_date, report_headers, report_result):
#     b2b_report_name = "b2b_" + starting_date + "_" + ending_date + ".csv"
#     with open(b2b_report_name, 'wt') as f:
#         try:
#             writer = csv.writer(f)
#             writer.writerow(report_headers)
#             for i in report_result:
#                 writer.writerow(i)
#             input(" will try to open ")
#             os.system('xdg-open ' + b2b_report_name)
#         except Exception as e:
#             print(e)

# def do_():
#     starting_date = get_starting_date()
#     ending_date = get_ending_date()
#     report_headers = get_header()
#     report_result = get_data(starting_date, ending_date)
#     print_data(report_headers, report_result)
#     write_data(starting_date, ending_date, report_headers, report_result)

# do_()
