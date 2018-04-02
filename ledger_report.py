
from reportlab.pdfgen import canvas
from reportlab.lib import units
from reportlab.lib import pagesizes
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import lightcoral, black, grey, navy
from num2words import num2words
import common_functions as cf
import os
from sys import platform

project_dir = os.path.dirname(os.path.abspath(__file__))
pdf_dir = os.path.join(project_dir, "temp_")
pdf_dir = os.path.join(pdf_dir, "invoices")
font_dir = os.path.join(project_dir, "required")
font_dir = os.path.join(font_dir, "fonts")
font_path = os.path.join(font_dir, "DroidSans.ttf")
# font_path = os.path.join(font_dir, "CarroisGothic-Regular.ttf")
font_path2 = os.path.join(font_dir, "LiberationMono-Bold.ttf")
font_path3 = os.path.join(font_dir, "larabiefont free.ttf")
image_path = os.path.join(project_dir,"some_pic.png")
# pdfmetrics.registerFont(TTFont("CarroisGothic-Regular", font_path))
pdfmetrics.registerFont(TTFont("DroidSans", font_path))
pdfmetrics.registerFont(TTFont("ClassCoder", font_path2))
pdfmetrics.registerFont(TTFont("larabie", font_path3))
invoice_detail_font_size = 8

def sub_header_(c, height):
    h = height - 30
    w = 60
    w_date = w + 50
    w_invoice_amount = w_date + 50
    w_receipt_amount = w_invoice_amount + 50
    w_balance = w_receipt_amount + 50
    c.setFillColorRGB(128, 0,0)
    c.drawString(w-30, h, "Date")
    c.drawRightString(w_date, h, "Invoice")
    c.drawRightString(w_invoice_amount, h, "Receipt")
    c.drawRightString(w_receipt_amount, h, "Balance")
    c.setLineWidth(0.2)
    c.line(8, h-5, 395, h-5)
    return c

def header_(c, owner_, height):
    # c.setFillColorRGB(0, 0, 102)
    c.setFillColor(navy)
    # c.setFillColorRGB(0,0,255)
    c.drawString(10, height, "Sale Ledger")
    height = height - 15
    c.drawString(10, height, owner_.name + " (" + owner_.place + ")")
    return c

    '''
    y1 = 595


    c.drawCentredString(300, y1, page_header)
    c.setFont("CarroisGothic-Regular",14,leading=None)
    c.setFillColorRGB(0, 0, 0)
    y1 = y1-15
    x = 30
    c.drawString(x, y1, custom_data.custom_name)
    c.setFont("CarroisGothic-Regular", 10, leading=None)
    y1 = y1 - 12
    c.drawString(x, y1, custom_data.custom_address_line_one)
    y1 = y1 - 12
    c.drawString(x, y1, custom_data.custom_address_line_two)
    y1 = y1 - 12
    c.drawString(x, y1, custom_data.custom_contact_no)
    y1 = y1 - 12
    c.setFont("ClassCoder", 10, leading=None)
    c.drawString(x,y1,custom_data.custom_gst_no)
    c.setFont("CarroisGothic-Regular", 12, leading=None)
    '''


def create_(dtd, page_size, owner_, opening_,  **kwargs):
    # if opening_ is None: # taking care of zero
    #     opening_ = dtd[0][5]
    master_= kwargs.get('master_', '')
    # dtd = invoice_.fetch_invoice_details(master_=master_)
    pdf_file_name = os.path.join(pdf_dir, str(1) + ".pdf")
    # print('dtd is {}'.format(dtd))
    margin = 0.5*units.cm
    if page_size == 'A5':
        c = canvas.Canvas(pdf_file_name, pagesize=pagesizes.A5)
        wid, hei = pagesizes.portrait(pagesizes.A5) # 420, 595 for A5 portrait
        max_page_item_count = 44
    elif page_size == 'A6':
        c = canvas.Canvas(pdf_file_name, pagesize=pagesizes.landscape(pagesizes.A6))
        wid, hei = pagesizes.landscape(pagesizes.A6) # 420, 297 for A6 landscape
        max_page_item_count = 19
    width = wid - margin
    height = hei  -  margin - 5
    y_start_value = height
    h = y_start_value
    c.setFont("DroidSans",invoice_detail_font_size,leading=None)
    page_count = 1
    row_height = 45
    item_count = 1
    page_item_count = 1
    flag_first = False
    last_item = len(dtd)
    for a in dtd:
        if h == y_start_value:
            c = header_(c, owner_,  height)
            c = sub_header_(c,  height)
        h = height-row_height
        if not flag_first:
            c.setFillColor(navy)
            # print('first height is {}'.format(h))
            c.drawRightString(60, h, 'Opening')
            c.drawRightString(210, h, str(opening_))
            page_item_count = page_item_count + 1
            h = h-12
            row_height = row_height + 12
            flag_first = True
        # w = 20
        # print(item_count, h)
        w = 60
        w_date = w + 50
        w_invoice_amount = w_date + 50
        w_receipt_amount = w_invoice_amount + 50
        w_balance = w_receipt_amount + 50
        # c.setFillColorRGB(101,0,0)
        c.setFillColor(navy)
        date_ = cf.reverse_date(str(a[0]))
        if a[2] in [0, None]:
            invoice_amount = ''
        else:
            invoice_amount = str(a[2])
        if a[3] in [0, None]:
            receipt_amount = ''
        else:
            receipt_amount = str(a[3])
        # invoice_amount = '' if a[2] == 0 else str(a[2])
        # receipt_amount = '' if a[3] == 0 else str(a[3])
        c.drawRightString(w, h, date_)
        c.drawRightString(w_date, h, invoice_amount)
        c.drawRightString(w_invoice_amount, h, receipt_amount)
        if item_count == last_item:
            c.setFillColorRGB(128, 0,0)
            c.setLineWidth(0.25)
            c.line(w_receipt_amount-25, h-3, w_receipt_amount, h-3)
            c.line(w_receipt_amount-25, h-5, w_receipt_amount, h-5)
            # c.setFillColor(lightcoral)
            c.drawRightString(w_receipt_amount, h, str(a[4]))
        else:
            c.drawRightString(w_receipt_amount, h, str(a[4]))
        row_height = row_height + 12
        item_count = item_count + 1
        page_item_count = page_item_count + 1
        if page_item_count == max_page_item_count:
            print("page_item_count is {}".format(page_item_count))
            page_item_count = 1
            c.drawRightString(40, h-20, "Page: " + str(page_count))
            page_count = page_count + 1
            h = y_start_value
            row_height = 45
            c.showPage()
            c.setFont("DroidSans",invoice_detail_font_size,leading=None)
            c.setFillColor(navy)
            c = sub_header_(c,  height)
            c = header_(c, owner_, height)
    c.showPage()
    c.save()
    os.system('xdg-open ' + pdf_file_name)
        # c.drawRightString(w_discount, h, disc)
        # c.drawRightString(w_sub_total, h, str(round(a[5],0)))
