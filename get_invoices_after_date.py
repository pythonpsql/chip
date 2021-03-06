
from database import Database, CursorFromConnectionFromPool as conn
import common_functions as cf
import os
import sale_report, gst_report
import invoice

def get_invoices(place, date_):
    with conn() as cursor:
        cursor.execute("select id, owner_name,amount_after_freight from master.sale_invoice where lower(owner_place) = %s and date_ > %s", (place, date_))
        result = cursor.fetchall()
        # print(result)
        return result

def get_gst_invoices(place, date_):
    with conn() as cursor:
        cursor.execute("select id, owner_name,amount_after_gst from sale_invoice where lower(owner_place) = %s and date_ > %s and gst_invoice_no is not null", (place, date_))
        result = cursor.fetchall()
        # print(result)
        return result

def create_pdf(result, **kwargs):
    gst_print = kwargs.get('gst_print','')
    if gst_print:
        for a in result:
            invoice_ = invoice.get_existing_invoice("sale_invoice", a[0], **kwargs)
            gst_report.create_(invoice_, 'A5', **kwargs, do_not_open_preview=True)
    else:
        for a in result:
            invoice_ = invoice.get_existing_invoice("sale_invoice", a[0], **kwargs)
            sale_report.create_(invoice_, 'A6', **kwargs, do_not_open_preview=True)

def move_invoices(result):
    import glob
    for name in glob.glob("temp_/invoices/*"):
        # invoice_id = name.split("temp_/invoices/")[1]
        try:
            invoice_id = name.split("temp_/invoices/")[1]
            invoice_id = invoice_id.split(".pdf")[0]
            print('see')
            print(invoice_id)
            for a in result:
                a = str(a[1]) + str(a[0]) + "(" + str(a[2]) + ")" + "__"
                # print(a)
                if str(invoice_id) == str(a):
                    os.system('mv ' + '\"'+ name + '\"' + ' ' + "temp_/invoices/" + place)
                    print('print start')
                    print(name)
        except Exception as e:
            pass


if __name__ == "__main__":
    Database.initialise(database='chip', host='localhost', user='dba_tovak')
    place = cf.prompt_("Enter place: ", cf.get_completer_list("place", "customer"), unique_="existing")
    place = place.lower()
    date_ = cf.prompt_("Enter starting date: ", [], default_="2018-")
    result = get_invoices(place, date_)
    gst_result = get_gst_invoices(place, date_)
    if result is not None:
        create_pdf(result, master_=True, place_=place)
    else:
        print("No invoices were found for {} after {}".format(place, date_))
    if gst_result  is not None:
        create_pdf(gst_result, place_=place, gst_print=True)
