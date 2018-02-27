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
pdf_dir = os.path.join(project_dir, "invoices")
font_dir = os.path.join(project_dir, "fonts")
font_path = os.path.join(font_dir, "DroidSans.ttf")
# font_path = os.path.join(font_dir, "CarroisGothic-Regular.ttf")
font_path2 = os.path.join(font_dir, "LiberationMono-Bold.ttf")
font_path3 = os.path.join(font_dir, "larabiefont free.ttf")
image_path = os.path.join(project_dir,"some_pic.png")
# pdfmetrics.registerFont(TTFont("CarroisGothic-Regular", font_path))
pdfmetrics.registerFont(TTFont("DroidSans", font_path))
pdfmetrics.registerFont(TTFont("ClassCoder", font_path2))
pdfmetrics.registerFont(TTFont("larabie", font_path3))
margin = 0.5*units.cm
width = wid - margin
height = hei  -  margin
invoice_detail_font_size = 8

def sub_header_(c, invoice_, height):
    h= height - 30
    w = 10
    w_name = w + 20
    w_qty = w_name + 200
    w_unit= w_qty+ 30
    w_rate = w_unit + 45
    w_discount= w_rate+ 40
    w_sub_total= w_discount+ 45
    c.setFillColorRGB(128, 0,0)
    c.drawString(w, h, "Sr")
    c.drawString(w_name, h, "Product")
    c.drawRightString(w_qty, h, "Qty")
    c.drawRightString(w_unit, h, "Unit")
    c.drawRightString(w_rate, h, "Rate")
    c.drawRightString(w_discount, h, "Disc")
    c.drawRightString(w_sub_total, h, "Amount")
    c.setLineWidth(0.2)
    c.line(8, h-5, wid-25, h-5)
    return c

def header_(c, invoice_, height):
    # c.setFillColorRGB(0, 0, 102)
    c.setFillColor(navy)
    # c.setFillColorRGB(0,0,255)
    c.drawString(10, height, "Estimate")
    c.drawRightString(360, height, "No:")
    c.drawRightString(390, height, str(invoice_.no_))
    height = height - 15
    c.drawString(10, height, invoice_.owner_name + " (" + invoice_.owner_place + ")")
    c.drawRightString(390, height, cf.reverse_date(str(invoice_.date_)))
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


def create_(invoice_,**kwargs):
    master_= kwargs.get('master_', '')
    x_start_value = width
    y_start_value = height
    # invoice_.get_invoice_properties()
    dtd = invoice_.fetch_invoice_details(master_=master_)
    # print('dtd is {}'.format(dtd))
    x = x_start_value
    h = y_start_value
    pdf_file_name = os.path.join(pdf_dir, str(invoice_.id) + ".pdf")
    c = canvas.Canvas(pdf_file_name, pagesize=pagesizes.landscape(pagesizes.A6))
    c.setFont("DroidSans",invoice_detail_font_size,leading=None)
    page_count = 1
    row_height = 45
    item_count = 1
    page_item_count = 1
    for a in dtd:
        if h == y_start_value:
            c = header_(c, invoice_, height)
            c = sub_header_(c, invoice_, height)
        h = height-row_height
        w = 20
        w_name = w + 10
        w_qty = w_name + 200
        w_unit= w_qty+ 30
        w_rate = w_unit + 50
        w_discount= w_rate + 30
        w_sub_total= w_discount+ 50
        # c.setFillColorRGB(101,0,0)
        c.setFillColor(navy)
        c.drawRightString(w, h, str(item_count))
        c.drawString(w_name, h, str(a[6]))
        c.drawRightString(w_qty, h, str(a[1]))
        c.drawRightString(w_unit, h, str(a[2]))
        c.drawRightString(w_rate, h, str(round(a[3],2)))
        if a[4] == None or a[4] == 0:
            disc = ""
        else:
            disc = str(round(a[4]))
        c.drawRightString(w_discount, h, disc)
        c.drawRightString(w_sub_total, h, str(round(a[5],0)))
        row_height = row_height + 12
        item_count = item_count + 1
        page_item_count = page_item_count + 1
        if page_item_count == max_page_item_count:
            print("page_item_count is {}".format(max_page_item_count))
            page_item_count = 1
            c.drawRightString(w_sub_total, h-20, "Page: " + str(page_count))
            page_count = page_count + 1
            h = y_start_value
            row_height = 45
            c.showPage()
            c.setFont("DroidSans",invoice_detail_font_size,leading=None)
            c.setFillColor(navy)
            c = header_(c, invoice_, height)
    c.setFont("DroidSans",invoice_detail_font_size,leading=None)
    c.setFillColor(navy)
    if not invoice_.freight:
        if not h > 20:
            c.show_Page()
            c.setFont("DroidSans",invoice_detail_font_size,leading=None)
            c.setFillColorRGB(0,0,101)
            c = header_(c, invoice_, height)
        c.setFillColorRGB(128, 0,0)
        c.drawString(w_sub_total-80, h-20, "Total:    ")
        c.drawRightString(w_sub_total,h-20,str(round(invoice_.amount_before_freight, 0)))
    else:
        if not h > 40:
            c.show_Page()
            c.setFont("DroidSans",invoice_detail_font_size,leading=None)
            c.setFillColor(navy)
            c = header_(c, invoice_, height)
        c.setFillColorRGB(128, 0, 0)
        c.drawString(w_sub_total-80, h-20, "Freight:    ")
        c.drawRightString(w_sub_total, h-20,str(round(invoice_.freight, 0)))
        c.drawString(w_sub_total-80, h-30, "Total:    ")
        c.drawRightString(w_sub_total,h-30,str(round(invoice_.amount_after_freight, 0)))
    c.setFillColorRGB(0,0,101)
    if page_count != 1:
        c.drawRightString(w_sub_total, 15, "Page: " + str(page_count))
    c.save()
    if platform == "linux" or platform == "linux2":
        os.system('xdg-open ' + pdf_file_name)
        # os.system('xpdf ' + pdf_file_name)
    elif platform == "darwin":
        os.system('open ' + pdf_file_name)
