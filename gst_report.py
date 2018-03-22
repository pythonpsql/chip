from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from num2words import num2words
import os
import required.custom_data as custom_data
from decimal import Decimal
pagesize = A4
width, height = pagesize
project_dir = os.path.dirname(os.path.abspath(__file__))
pdf_dir = os.path.join(project_dir, "temp_")
pdf_dir = os.path.join(pdf_dir, "gst_invoices")
font_dir = os.path.join(project_dir, "required")
font_dir = os.path.join(font_dir, "fonts")
font_path = os.path.join(font_dir, "CarroisGothic-Regular.ttf")
font_path2 = os.path.join(font_dir, "LiberationMono-Bold.ttf")
font_path3 = os.path.join(font_dir, "larabiefont free.ttf")
# pdf_file_name = os.path.join(project_dir, "temp.pdf")
# pdf_file_name = "/Users/python/
#
# /stack/project/temp.pdf"
image_path = os.path.join(font_dir,"some_pic.png")

def reverse_date(i):
    i = i.split("-")
    i = i[2] + "-" + i[1] + "-" + i[0]
    return i


def setup_page(invoice_detail_info_p, invoice_info_p, transactor_name_p, transactor_place_p, customer_details_p,c, memo_type_p):
    freight_p = invoice_info_p.freight
    if freight_p is None: freight_p = 0
    customer_gst_p = str(customer_details_p.gst_number)
    address_first_line = "" if customer_details_p.address_line_one is None else str(customer_details_p.address_line_one)
    address_second_line = "" if customer_details_p.address_line_two is None else str(customer_details_p.address_line_two)
    address_third_line = "" if customer_details_p.address_line_three is None else str(customer_details_p.address_line_three)
    contact_no_first = "" if customer_details_p.contact_one is None else str(customer_details_p.contact_one)
    state_name = custom_data.custom_state
    state_code = custom_data.custom_state_code
    invoice_date = str(invoice_info_p.date_)
    # transport_name = invoice_info_p[0][1]
    # transport_lr_no = invoice_info_p[0][2]
    # transport_lr_no_of_bags = invoice_info_p[0][3]
    invoice_no = str(invoice_info_p.gst_invoice_no)
    amount_before_tax = invoice_info_p.amount_before_freight
    # print(amount_before_tax)
    if amount_before_tax is None: amount_before_tax = 0
    amount_before_tax = (amount_before_tax).quantize(Decimal("1"))
    # print(freight_p)
    if invoice_info_p.gst_18 is None: invoice_info_p.gst_18= 0
    cgst9_amount = (Decimal(invoice_info_p.gst_18)/Decimal(2) + Decimal(freight_p) * Decimal(0.09)).quantize(Decimal("1.00"))
    # if cgst9_amount is None: cgst9_amount = 0
    # cgst9_amount = cgst9_amount.quantize(Decimal("1.00"))
    sgst9_amount = cgst9_amount
    if invoice_info_p.gst_28 is None: invoice_info_p.gst_28= 0
    cgst14_amount = (Decimal(invoice_info_p.gst_28)/Decimal(2)).quantize(Decimal("1.00"))
    sgst14_amount = cgst9_amount
    # sgst9_amount = sgst9_amount.quantize(Decimal("1.00"))
    # cgst14_amount = invoice_info_p[0][8]
    if invoice_info_p.gst_5 is None: invoice_info_p.gst_5= 0
    cgst2_5_amount = (Decimal(invoice_info_p.gst_5)/Decimal(2)).quantize(Decimal("1.00"))
    if cgst2_5_amount is None: cgst2_5_amount = 0
    sgst2_5_amount = cgst2_5_amount
    if invoice_info_p.gst_12 is None: invoice_info_p.gst_12= 0
    cgst6_amount = (Decimal(invoice_info_p.gst_12)/Decimal(2)).quantize(Decimal("1.00"))

    sgst6_amount = cgst6_amount
    # cgst6_amount = invoice_info_p[0][15]
    # if cgst6_amount is None: cgst6_amount = 0
    cgst14_amount = cgst14_amount.quantize(Decimal("1.00"))

    cgst9_taxable_amount = (Decimal(cgst9_amount)/ Decimal(9) * Decimal(100)).quantize(Decimal("1.00"))
    cgst14_taxable_amount = (Decimal(cgst14_amount)/ Decimal(14) * Decimal(100)).quantize(Decimal("1.00"))
    cgst2_5_taxable_amount = (Decimal(cgst2_5_amount)/ Decimal(2.5) * Decimal(100)).quantize(Decimal("1.00"))
    cgst6_taxable_amount = (Decimal(cgst6_amount)/ Decimal(6) * Decimal(100)).quantize(Decimal("1.00"))
    # cgst14_taxable_amount = cgst14_taxable_amount.quantize(Decimal("1.00"))
    if invoice_info_p.amount_after_gst is None: invoice_info_p.amount_after_gst = 0
    total_amount_after_gst = invoice_info_p.amount_after_gst
    # amount_after_gst = amount_after_gst.quantize(Decimal("1.00"))
    site = invoice_info_p.site
    # barcode_font = r"/carrois-gothic/CarroisGothic-Regular.ttf"
    # print(font_path)

    pdfmetrics.registerFont(TTFont("CarroisGothic-Regular", font_path))
    pdfmetrics.registerFont(TTFont("ClassCoder", font_path2))
    pdfmetrics.registerFont(TTFont("larabie", font_path3))
    c.setFillColorRGB(0, 0, 102)
    c.setFont("CarroisGothic-Regular",14,leading=None)
    page_header = "Tax Invoice"

    y1 = 820

    c.setFont("larabie",14,leading=None)
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
    # print(memo_type_p)
    c.drawString(470, y1+48, "Original / Duplicate")
    if memo_type_p is None or memo_type_p  == "credit":
        c.drawString(480, y1, "Credit Memo")
    elif memo_type_p == "cash":
        c.drawString(480, y1, "Cash Memo")
    y1 = y1 - 1
    c.rect(25, 625, 550, 125, fill=0)      # buyer rectangle
    c.line(337, 625,337, 750) # vertical line in buyer rectangle
    c.line(0, height/2, 10, height/2)
    c.setFont("CarroisGothic-Regular", 10, leading=None)
    c.drawString(35, 730, "Buyer:")
    c.drawRightString(330, 730,transactor_name_p + " (" + transactor_place_p + ")")
    c.drawString(35, 710, "Address:")
    c.drawString(35, 660, "Contact No:")
    c.drawRightString(330, 710, address_first_line)
    c.drawRightString(330, 695, address_second_line)
    c.drawRightString(330, 680, address_third_line)
    c.drawRightString(330, 660, contact_no_first)
    c.drawString(35, 640, "GST IN:")
    c.drawRightString(330, 640, customer_gst_p)
    # c.setFont("CarroisGothic-Regular", 10, leading=None)
    c.drawString(360, 730, "Invoice No:")
    c.drawRightString(550, 730,invoice_no)
    c.drawString(360, 710, "Date:")
    c.drawRightString(550, 710,reverse_date(invoice_date))
    c.drawString(360, 690, "State:")
    c.drawRightString(550, 690, state_name)
    c.drawString(360, 670, "State Code:")
    c.drawString(360, 650, "Place of Supply:")
    c.drawRightString(550, 650, transactor_place_p)
    c.drawRightString(550, 670, state_code)
    c.rect(25, 242, 550, 575, fill=0)  # main rectangle
    # table_heading = "Sr"+ t+"Name" + 7*t +"  HSN"+t+ "Qty" + t + "Unit" + t + "Rate" +\
    #                 t + "Disc"+t+"SGST" + " " +"CGST" + t + "      Amount"
    # c.setFont("Courier",10,leading=None)
    # c.drawString(30, 600, table_heading)
    c.setFont("CarroisGothic-Regular", 10, leading=None)
    c.line(25, 610, 575, 610)  # horizontal line in product table
    table_title_y = 613
    c.drawString(30, table_title_y, "Sr")
    x1,y1,x2,y2 = 45, 625, 45,242
    c.line(x1 + 2, y1, x2 + 2, y2)  # sr line
    c.drawString(x1 + 5, table_title_y, "Product")
    c.line(x1+170, y1, x1+170, y2)    # name
    c.drawRightString(x1 + 205+ 1, table_title_y, "HSN")
    c.line(x1 + 210, y1, x1 + 210, y2)  #hsn
    c.drawRightString(x1 + 255, table_title_y, "Qty")
    c.line(x1 + 260+2, y1, x1 + 260+2, y2) # qty
    c.drawRightString(x1 + 290, table_title_y, "Unit")
    c.line(x1 + 290+2, y1, x1 + 290+2, y2) # unit
    c.drawRightString(x1 + 335, table_title_y, "Rate")
    c.line(x1 + 340+2, y1, x1 + 340+2, y2) #rate
    c.drawRightString(x1 + 375, table_title_y, "Disc")
    c.line(x1 + 380 + 2, y1, x1 + 380 + 2, y2)# discount
    c.drawRightString(x1 + 410, table_title_y, "CGST")
    c.line(x1 + 410 + 2, y1, x1 + 410 + 2, y2) # cgst
    c.drawRightString(x1 + 440, table_title_y, "SGST")
    c.line(x1 + 440 + 2, y1, x1 + 440 + 2, y2)  # sgst
    c.drawRightString(x1 + 465, table_title_y, "IGST")
    c.line(x1 + 465+2, y1, x1 + 465+2, y2) #cgst
    c.drawRightString(x1 + 520, table_title_y, "Amount")
    c.rect(25,222,550,20) #total amt rect
    c.rect(25,122,550,100)# tax calculation
    c.line(387,122,387,102)#grand total vertical
    c.line(387,222,387,122)#tax calculation vertical
    c.setFont("CarroisGothic-Regular", 12, leading=None)
    c.drawString(390, 228, "Sub Total:")  # sub-total
    c.drawRightString(550, 228, str(amount_before_tax)) # sub-total
    c.drawString(30, 205, "GST @ 5%")
    if not cgst2_5_taxable_amount == 0:
        c.drawRightString(190, 205, str(cgst2_5_taxable_amount))
        c.drawRightString(310,205,str(cgst2_5_amount * 2))
    c.drawString(390,205,"Transport:")#transport
    if not freight_p == 0:
        c.drawRightString(550, 205, str(freight_p))
    c.line(25,198,575,198)#transport horizontal
    c.drawString(30, 180, "GST @ 12%")
    if not cgst6_taxable_amount == 0:
        c.drawRightString(190, 180, str(cgst6_taxable_amount))
        c.drawRightString(310, 180, str(cgst6_amount * 2))
    cgst = (cgst9_amount + cgst14_amount + cgst2_5_amount + cgst6_amount).quantize(Decimal("1"))
    c.drawRightString(550, 180, str(cgst))
    c.drawString(390,180,"CGST:")#cgst
    c.line(25,173,575,173)#cgst horizontal
    c.drawString(30, 155, "GST @ 18%")
    if not cgst9_taxable_amount == 0:
        c.drawRightString(190, 155, str(cgst9_taxable_amount))
        c.drawRightString(310,155,str(cgst9_amount*2))
    c.drawString(390, 155,"SGST:")  # sgst
    c.drawRightString(550, 155, str(cgst))
    c.line(25,148,575,148)#sgst horizontal
    c.drawString(30, 130, "GST @ 28%")
    # print(cgst14_taxable_amount)
    if not cgst14_taxable_amount == 0:
        c.drawRightString(190, 130, str(cgst14_taxable_amount))
        c.drawRightString(310, 130, str(cgst14_amount*2))  # transport
    c.drawString(390, 130, "IGST: ")  # igst
    c.drawString(390, 107, "Grand Total (Rs):")
    # grand_total = amount_before_tax + (cgst * 2)
    # grand_total = round(grand_total)
    c.drawString(30, 88, "Rs. " + num2words(total_amount_after_gst).title())
    c.drawRightString(550, 107,str(total_amount_after_gst))
    c.drawString(30, 227, "Tax Account")
    c.drawString(130, 227, "Taxable Amount")
    c.drawString(250, 227, "Tax Amount")
    c.line(387,242,387,222)#sub total
    c.rect(25, 102, 550, 20) #grand total
    c.rect(25, 82, 550, 20) #in words amt
    c.rect(25, 20, 550, 62)#sign
    c.line(387,82,387,20)
    c.line(25,50,387,50)
    c.drawString(30, 38, custom_data.custom_bank_line_one)
    c.drawString(30, 24, custom_data.custom_bank_line_two)
    c.drawString(30, 70, "Certified that the particulars given above are true and correct")
    c.drawString(30, 55, "Amount of tax subject to reverse charge:")
    c.drawString(400, 70, custom_data.custom_signatory)
    c.drawString(420, 25, "Authorised Signatory")
    # c.drawInlineImage(image_path, 425,35,70,30)
    # mask = [254, 255, 254, 255, 254, 255]
    c.drawImage(image_path, 425,35,70,30,mask='auto')
    c.setFont("CarroisGothic-Regular", 10, leading=None)
    c.drawString(30, 10, "Subject to " + custom_data.custom_city + " Jurisdiction")
    c.setFont("CarroisGothic-Regular", 12, leading=None)
    return c

def create_(invoice_, page_size, **kwargs):
    master_= kwargs.get('master_', '')
    invoice_detail_info_p = invoice_.fetch_invoice_details_gst(master_=master_)
    invoice_info_p = invoice_
    transactor_name_p = invoice_.gst_owner_name
    if not transactor_name_p:
        temp_name = invoice_.owner.set_gst_name()
        transactor_name_p = temp_name
        invoice_.gst_owner_name = temp_name
    transactor_place_p = invoice_.owner_place
    customer_details_p = invoice_.owner
    memo_type_p = invoice_.memo_type
    # print("1. {} 2. {} 3. {} 4. {} 5. {} 6 {}".format(invoice_detail_info_p, invoice_info_p, transactor_name_p, transactor_place_p, customer_details_p, memo_type_p))
    invoice_no = str(invoice_.gst_invoice_no)
    # invoice_no = str(invoice_info_p[0][4])
    import os
    pdf_file_name = os.path.join(pdf_dir, invoice_no + ".pdf")
    c = canvas.Canvas(pdf_file_name, pagesize=A4)
    setup_page(invoice_detail_info_p, invoice_info_p, transactor_name_p, transactor_place_p, customer_details_p,c, memo_type_p)
    i_co = 1
    x_co = 45
    y_co = 595

    for a in invoice_detail_info_p:
        c.setFont("CarroisGothic-Regular", 10, leading=None)
        # print(a)
        c.drawRightString(45, y_co, str(i_co))                  # sr
        # c.drawString(x + 15, y, str(a[0]))
        c.drawString(x_co+5, y_co, str(a[11]))          # name
        if str(a[8]) == "None":
            c.drawRightString(x_co + 205, y_co, "")  # hsn
        else:
            c.drawRightString(x_co + 205, y_co, str(a[8]))            # hsn
        c.drawRightString(x_co + 260, y_co, str(a[1])) # qty
        c.drawRightString(x_co + 290, y_co, str(a[2]))    # unit
        c.drawRightString(x_co + 340, y_co, str(a[3]))    # rate

        if a[4] in [None, 0.00]:
            temp = ""
        else:
            temp = str(a[4])
        c.drawRightString(x_co + 380, y_co, str(temp))    # disc
        c.drawRightString(x_co + 410, y_co, str(a[9]/2))    # cgst
        c.drawRightString(x_co + 440, y_co, str(a[9]/2))  # sgst
        c.drawRightString(x_co + 465, y_co, "")  # igst
        c.drawRightString(x_co + 525, y_co, str(a[5]))    # amount
        i_co += 1
        y_co -= 15
        if y_co < 250:
            c.showPage()
            y_co = 595
            c = setup_page(invoice_detail_info_p, invoice_info_p, transactor_name_p, transactor_place_p, customer_details_p, c, memo_type_p)
    c.showPage()
    c.save()
    try:
        from sys import platform
        import os
        if platform == "linux" or platform == "linux2":
            os.system('xdg-open ' + pdf_file_name)
        elif platform == "darwin":
            os.system('open ' + pdf_file_name)
        elif platform == "win32":
            os.system('start ' + pdf_file_name)
        # subprocess.Popen(pdf_file_name)
    except Exception as e:
        print(e)
