import pandas as pd
import streamlit as st
from fpdf import FPDF
import tempfile
import io
import uuid
import os
from io import BytesIO
import math
import datetime as dt




color_map = {
    "White": "White.jpg",
    "Navy Blue": "Navy Blue.jpg",
    "Indigo": "Indigo.jpg",
    "Aqua Blue": "Aqua Blue.jpg",
    "Polka Denim": "Polka Denim.jpg",
    "Beach Print": "Beach Print.jpg"
}


def mask_mobile_email(mobile_no, email):

    digits = list(mobile_no)

    for i in range(len(mobile_no)):
        if i % 2 == 1:
            digits[i]='*'

    masked_mobile_no = "".join(digits)

    email_chars = list(email)

    for i in range(len(email)):
        if i % 2 == 1:
            email_chars[i]='*'

    masked_email = "".join(email_chars)

    #st.write(masked_email, masked_mobile_no)

    return masked_mobile_no, masked_email



def display_labels(label, values):

    html_text = f"""
        <p><strong style='line-height: 50px;color:blue;vertical-align: middle;'>{label}:</strong> <span style='color:red;vertical-align: middle;'>{values}</span></p>
    """

    return html_text



def display_amount(amount, paisa='N'):

    if amount != amount:
        amount = 0

    if amount < 0:
        amt_str = '₹ -'
        amount = abs(amount)
    else:
        amt_str = '₹ '

    decimal_part_str = str(round(amount,2)).split(".")

    if len(decimal_part_str) > 1:
        decimal_part = decimal_part_str[1][:2]
        if len(decimal_part) == 1:
            decimal_part = decimal_part.ljust(2,'0')
        else:
            decimal_part = decimal_part.rjust(2,'0')
    else:
        decimal_part = '00'


    amount = round(amount,2)
    cr_amt = int(amount/10000000)
    cr_bal = int(amount - cr_amt * 10000000)

    lkh_amt = int (cr_bal/100000)
    lkh_bal = int(cr_bal - lkh_amt * 100000)

    th_amt  = int(lkh_bal/1000)
    th_bal  = int(lkh_bal - th_amt * 1000)


    if cr_amt > 0:
        if cr_bal > 0:
            amt_str = amt_str + str(cr_amt) + "," + str(lkh_amt).rjust(2,'0') + "," + str(th_amt).rjust(2,'0') + "," + str(th_bal).rjust(3,'0') + "." + decimal_part
        else:
            amt_str = amt_str + str(cr_amt) + ",00,00,000.00"
    elif lkh_amt > 0:
        if lkh_bal > 0:
            amt_str = amt_str + str(lkh_amt) + "," + str(th_amt).rjust(2,'0') + "," + str(th_bal).rjust(3,'0') + "." + decimal_part
        else:
            amt_str = amt_str + str(lkh_amt) + ",00,000.00"
    elif th_amt > 0:
        amt_str = amt_str + str(th_amt) + "," + str(th_bal).rjust(3,'0') + "." + decimal_part
    else:
        amt_str = amt_str + str(th_bal) + "." + decimal_part

    if paisa == 'N':
        amt_str = amt_str.split(".")[0]

    return amt_str

def get_markdown_table(data, header='Y', footer='Y'):


    if header == 'Y':

        cols = data.columns
        ncols = len(cols)
        if ncols < 5:
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f3f3f3;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:14px'>"
        elif ncols < 7:
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:12px'>"
        else:
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:10px'>"


        for i in cols:
            if 'Fund' in i or 'Name' in i:
                html_script = html_script + "<th style='text-align:left'>{}</th>".format(i)
            else:
                html_script = html_script + "<th style='text-align:center''>{}</th>".format(i)

    html_script = html_script + "</tr></thead><tbody>"
    for j in data.index:
        if ncols < 5:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:12px;padding:1px;';>"
        elif ncols < 7:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:11px;padding:1px;';>"
        else:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:9px;padding:1px;';>"

        a = data.loc[j]
        for k in cols:
            if 'Fund' in k or 'Name' in k:
                html_script = html_script + "<td style='padding:2px;text-align:left' rowspan='1'>{}</td>".format(a[k])
            else:
                html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(a[k])

    html_script = html_script + '</tbody></table>'

    return html_script


def get_markdown_col_fields(field_label, field_value, format_amt = 'N'):
    markdown_txt = '<p><span style="font-family: Verdana, Geneva, sans-serif; font-size: 12px;">'
    markdown_txt = markdown_txt + '<span style="color: rgb(20,20,255);"><strong>{}: </strong></span>'.format(field_label)
    if format_amt == 'Y':
        markdown_txt = markdown_txt + '<span style="color: rgb(0,0,0);">{}</span>'.format(display_amount(field_value))
    else:
        markdown_txt = markdown_txt + '<span style="color: rgb(0,0,0);">{}</span>'.format(field_value)

    return markdown_txt


def get_markdown_dict(dict, font_size = 10, format_amt = 'N'):


    html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:15px'>"

    #html_script = html_script +  "<table><style> th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:15px'>"

    for j in dict.keys():

        if dict[j] == dict[j]:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:{}px;padding:1px;';>".format(font_size)
            html_script = html_script + "<td style='border:none;padding:2px;font-family:Courier; color:Blue; font-size:{}px;text-align:left' rowspan='1'>{}</td>".format(font_size,j)
            if format_amt == 'N':
                html_script = html_script + "<td style='border:none;padding:4px;font-family:Courier; color:Black; font-size:{}px;text-align:left' rowspan='1'>{}</td>".format(font_size -1,dict[j])
            else:
                html_script = html_script + "<td style='border:none;padding:4px;font-family:Courier; color:Black; font-size:{}px;text-align:right' rowspan='1'>{}</td>".format(font_size -1,display_amount(dict[j]))



    html_script = html_script + '</tbody></table>'

    return html_script



def calculate_bmi(height, weight):
    height_in_metres = height * 0.0254
    bmi = weight / (height_in_metres ** 2)

    return bmi

def nearest_point_5(value):
    return round(value * 2,0)/2

def calculate_across_shoulder(chest):
    return nearest_point_5(8 + chest * 0.25)

def calculate_shirt_length(chest, height, bmi):
    #shirt_length = nearest_point_5(18 + chest * 0.25)

    if height >= 72:
        shirt_length = 30
    elif height >= 69:
        shirt_length = 29.5
    elif height >= 66:
        shirt_length = 28.5
    elif height < 65:
        shirt_length = shirt_length - 0.5

    if bmi >= 30:
        shirt_length = shirt_length + 0.5
    elif bmi <=22:
        shirt_length = shirt_length - 0.5


    return shirt_length

def calculate_waist_length(chest, shirt_fit, bmi):

    if bmi > 30:
        waist_length = chest
    elif bmi > 27 and bmi <= 30:
        waist_length = chest - 0.5
    elif bmi > 22 and bmi <= 27:
        waist_length = chest -1
    elif bmi > 18 and bmi <= 22:
        waist_length = chest -1.5
    else:
        waist_length = chest - 2

    if shirt_fit == 'Slim':
        waist_length = waist_length - 0.5
    elif shirt_fit == 'Loose':
        waist_length = waist_length + 0.5


    return waist_length


def calculate_sleeve_length(shirt_length, half_sleeve=True):


    if shirt_length <= 28:
        sleeve_length = 9

        if not half_sleeve:
            sleeve_length = 24

    elif shirt_length <= 30:
        sleeve_length = 9.5

        if not half_sleeve:
            sleeve_length = 25
    else:
        sleeve_length = 10
        if not half_sleeve:
            sleeve_length = 26

    #st.write(half_sleeve, sleeve_length)
    return sleeve_length


def calculate_collar_length(chest):

    if chest < 38:
        collar_length = 15.5
    elif chest in [38, 39]:
        collar_length = 16
    elif chest in [40, 41]:
        collar_length = 16.5
    elif chest in [42, 43]:
        collar_length = 17
    elif chest in [44, 45]:
        collar_length = 17.5
    else:
        collar_length = 18

    return collar_length



def calculate_recommended_dimensions(shirt_fit,height, bmi, chest, half_sleeve='Y'):
    # Filter the dataframe for the selected brand and size

    #bmi = calculate_bmi(height, weight)

    across_shoulder_adj = calculate_across_shoulder(chest)

    shirt_length = calculate_shirt_length(chest, height, bmi)

    waist_length = calculate_waist_length(chest,shirt_fit, bmi)

    sleeve_length = calculate_sleeve_length(shirt_length, half_sleeve)

    collar_length = calculate_collar_length(chest)

    dims = {
        'Chest': chest,
        'ShirtLength': shirt_length,
        'AcrossShoulder': across_shoulder_adj,
        'Waist': waist_length,
        'SleeveLength': sleeve_length,
        'Collar': collar_length

    }

    #st.write(dims)
    return dims



def hex_to_rgb(hex_code: str):
    """
    Convert a hex color code (e.g., "#FF5733" or "FF5733")
    to an (R, G, B) tuple of integers (0-255).
    """
    # Strip leading "#" if present
    hex_code = hex_code.lstrip('#')

    # Optionally expand shorthand (e.g., "FFF" -> "FFFFFF")
    if len(hex_code) == 3:
        hex_code = ''.join([2 * c for c in hex_code])

    # Parse the three pairs (R, G, B)
    r = int(hex_code[0:2], 16)
    g = int(hex_code[2:4], 16)
    b = int(hex_code[4:6], 16)

    return r, g, b



def show_logo():

    # Display the logo at the top of every page
    c1,c2,c3 = st.columns((8,8,3))
    c3.image(LOGO_PATH, width=75)  # Adjust width as needed


@st.cache_data()
def generate_pdf_report(order_no, curr_submission, shirt_dims, additional_notes, curr_status,price_flag="Y"):


    #st.write(curr_submission)
    WIDTH = 297
    HEIGHT = 210
    session_id = str(uuid.uuid4())
    #st.write(session_id)
    temp_filename = f"file_{session_id}.png"
    report_filenm = f"report_{session_id}.png"

    logo_path = "AC_Logo.png"
    size_guide_path = "SizeGuide.PNG"


    if curr_submission["half_sleeve"]:
        shirt_type = "Half Sleeve"
    else:
        shirt_type = "Full Sleeve"


    name = curr_submission["name"]
    mobile = curr_submission["mobile_number"]
    emailid = curr_submission["email"]
    order_price = curr_submission["shirt_price"]

    masked_mobile, masked_email = mask_mobile_email(mobile, emailid)

    delivery_address = curr_submission["delivery_addr"]

    color = curr_submission["color_option"]
    #fc_red, fc_green, fc_blue = hex_to_rgb(color_map[color])

    #curr_submission["chest_size"],
    height = curr_submission["how_tall"]

    if height == "Short":
        height_desc = "Less than 5 Feet 5 Inch"
        height_image = "Tall_Category_1.png"
    elif height == "Average":
        height_desc = "5 Feet 5 Inch - 5 Feet 8 Inch"
        height_image = "Tall_Category_2.png"
    elif height == "Tall":
        height_desc = "5 Feet 9 Inch - 6 Feet"
        height_image = "Tall_Category_3.png"
    elif height == "Very Tall":
        height_desc = "More than 6 Feet"
        height_image = "Tall_Category_4.png"



    body_type = curr_submission["body_type"]

    if body_type == "Skinny":
        body_type_image = "Skinny_bodytype.png"
    elif body_type == "Slim":
        body_type_image = "Slim_bodytype.png"
    elif body_type == "Regular":
        body_type_image = "Regular_bodytype.png"
    elif body_type == "Overweight":
        body_type_image = "Overweight_bodytype.png"
    else:
        body_type_image = "Obese_bodytype.png"



    pocket_desc = curr_submission["pockets"]
    shirt_fit = curr_submission["shirt_fit"]

    chest_size = shirt_dims["Chest"]
    shirt_length = shirt_dims["ShirtLength"]
    across_shoulder = shirt_dims["AcrossShoulder"]
    waist_length = shirt_dims["Waist"]
    sleeve_length = shirt_dims["SleeveLength"]
    collar_size = shirt_dims["Collar"]


    try:

        # Create a new PDF instance in Landscape mode (A4)
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()

        # Optionally, set auto page breaks
        pdf.set_auto_page_break(auto=True, margin=15)

        # Store page dimensions
        page_width = pdf.w
        page_height = pdf.h

        # -------------------------------------------------------------------------
        # 1. Add the top-centered logo
        # -------------------------------------------------------------------------
        # Choose a desired logo width (in mm). Adjust as necessary.
        logo_width = 30

        # Calculate X-position to center the logo
        x_logo = (page_width - logo_width -10)
        y_logo = 10  # vertical positioning for the logo

        pdf.image(logo_path, x=x_logo, y=y_logo, w=logo_width)

        # -------------------------------------------------------------------------
        # 2. Add the title "Order Summary" below the logo
        # -------------------------------------------------------------------------
        # Move down below the logo
        pdf.set_y(y_logo  + 5)

        pdf.set_font("Arial", "BU", 16)
        pdf.cell(0, 10, "Order Summary", border=0, ln=1, align='C')

        pdf.set_font("Arial", size=13)

        pdf.set_y(y_logo  + 12)
        pdf.cell(0, 10, "Affordable Classics", border=0, ln=1, align='C')

        pdf.set_y(y_logo  + 19)
        pdf.cell(0, 10, "Mobile:9836064237", border=0, ln=1, align='C')



        # -------------------------------------------------------------------------
        # 3. Position for Left & Right columns
        # -------------------------------------------------------------------------
        # We'll place the left column at x=10 mm, the right column at x ~ 150 mm.
        # Adjust as needed based on your preferred layout.
        left_x = 12
        left_x2 = 30
        right_x = 130
        right_x2 = 150
        top_y = 50  # where the columns start
        line_gap = 7


        # -------------------------------------------------------------------------
        # 4. Left Column - Basic Customer Information
        # -------------------------------------------------------------------------
        top_y = 50
        pdf.set_xy(left_x, top_y)
        column_width = 20  # width for the left column text

        pdf.set_font("Arial", "B", 12)
        pdf.cell(column_width, 10, f"Order No:", align="R")

        pdf.set_xy(left_x2, top_y)
        pdf.set_font("Arial", size=12)
        pdf.cell(column_width, 10, f"{order_no}", align="L")

        top_y += line_gap
        pdf.set_xy(left_x, top_y)
        column_width = 20  # width for the left column text

        pdf.set_font("Arial", "B", 12)
        pdf.cell(column_width, 10, f"Order Amount:", align="R")

        pdf.set_xy(left_x2, top_y)
        pdf.set_font("Arial", size=12)
        pdf.cell(column_width, 10, f" Rs. {order_price}", align="L")

        top_y += line_gap
        pdf.set_xy(left_x, top_y)
        column_width = 20  # width for the left column text

        pdf.set_font("Arial", "B", 12)
        pdf.cell(column_width, 10, f"Name:", align="R")

        pdf.set_xy(left_x2, top_y)
        pdf.set_font("Arial", size=12)
        pdf.cell(column_width, 10, f"{name}", align="L")


        top_y += line_gap
        pdf.set_xy(left_x, top_y)
        column_width = 20  # width for the left column text

        pdf.set_font("Arial", "B", 12)
        pdf.cell(column_width, 10, f"Mobile:", align="R")

        pdf.set_xy(left_x2, top_y)
        pdf.set_font("Arial", size=12)
        pdf.cell(column_width, 10, f"{masked_mobile}", align="L")

        top_y += line_gap
        pdf.set_xy(left_x, top_y)
        column_width = 20  # width for the left column text

        pdf.set_font("Arial", "B", 12)
        pdf.cell(column_width, 10, f"Email:", align="R")

        pdf.set_xy(left_x2, top_y)
        pdf.set_font("Arial", size=12)
        pdf.cell(column_width, 10, f"{masked_email}", align="L")


        top_y += 2*line_gap
        pdf.set_xy(left_x, top_y)
        column_width = 20  # width for the left column text

        pdf.set_font("Arial", "B", 12)
        pdf.cell(column_width, 10, f"Shipping Address:", align="L")

        top_y += line_gap
        pdf.set_xy(left_x, top_y)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(80, 10, f"{curr_submission['delivery_addr']}", align="L")






        # -------------------------------------------------------------------------
        # 5. Right Column - Order Details
        # -------------------------------------------------------------------------

        top_y = 50
        pdf.set_xy(right_x, top_y)
        column_width = 20  # width for the left column text

        pdf.set_font("Arial", "B", 12)
        pdf.cell(column_width, 10, f"Shirt Type:", align="R")

        pdf.set_xy(right_x2, top_y)
        pdf.set_font("Arial", size=12)
        pdf.cell(column_width, 10, f"{shirt_type}", align="L")

        top_y += line_gap
        pdf.set_xy(right_x, top_y)
        column_width = 20  # width for the left column text

        pdf.set_font("Arial", "B", 12)
        pdf.cell(column_width, 10, f"Shirt Colour:", align="R")

        pdf.set_xy(right_x2, top_y)
        pdf.set_font("Arial", size=12)
        #pdf.cell(column_width, 10, f"{color}", align="L")
        #pdf.set_fill_color(fc_red, fc_green, fc_blue)

        #pdf.rect(right_x2+3, top_y+2, 10, 5, style='DF')

        pdf.image(color_map[color], x=right_x2+3, y=top_y+2, w=13)


        top_y += 2*line_gap
        pdf.set_xy(right_x, top_y)
        column_width = 20  # width for the left column text

        pdf.set_font("Arial", "B", 12)
        pdf.cell(column_width, 10, f"Shirt Pocket:", align="R")

        pdf.set_xy(right_x2, top_y)
        pdf.set_font("Arial", size=12)
        pdf.cell(column_width, 10, f"{curr_submission['pockets']}", align="L")


        top_y += line_gap
        pdf.set_xy(right_x, top_y)
        column_width = 20  # width for the left column text

        pdf.set_font("Arial", "B", 12)
        pdf.cell(column_width, 10, f"Hemline:", align="R")

        pdf.set_xy(right_x2, top_y)
        pdf.set_font("Arial", size=12)
        pdf.cell(column_width, 10, f"{curr_submission['hemline']}", align="L")

        top_y += line_gap
        pdf.set_xy(right_x, top_y)
        column_width = 20  # width for the left column text

        pdf.set_font("Arial", "B", 12)
        #pdf.cell(column_width, 10, f"Embroidered Initials:", align="R")

        pdf.set_xy(right_x2, top_y)
        pdf.set_font("Arial", size=12)
        #pdf.cell(column_width, 10, f"{curr_submission['personalise_letter']}", align="L")


        if additional_notes.strip():

            top_y += 2*line_gap
            pdf.set_xy(right_x, top_y)
            column_width = 20  # width for the left column text

            pdf.set_font("Arial", "B", 12)
            pdf.cell(column_width, 10, f"Additional Notes:", align="L")

            pdf.set_xy(right_x, top_y+10)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(80, 10, f"{additional_notes}", align="L")



        top_y = 50
        pdf.set_xy(200, top_y)

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Height: {height_desc}", align="C")
        pdf.image(height_image, x=205 , y=60, w=75)


        top_y = 100
        pdf.set_xy(200, top_y)

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Body Type: {body_type}", align="C")
        pdf.image(body_type_image, x=210 , y=110, w=60)



        # -------------------------------------------------------------------------
        # 6. Save the generated PDF
        # -------------------------------------------------------------------------

        pdf.set_xy(105, 125)
        pdf.set_font("Arial", "BU", 14)
        pdf.cell(40, 10, "Recommended Measurements", border=0, ln=1, align='C')

        pdf.image("SizeGuide.PNG", x=60 , y=135, w=60)


        top_y = 140
        top_x = 220
        right_x = right_x + 10
        right_x2 = right_x2 + 10

        pdf.set_xy(right_x, top_y)
        column_width = 20  # width for the left column text

        pdf.set_font("Arial", "B", 12)
        pdf.cell(column_width, 10, f"Shirt Fit:", align="R")

        pdf.set_xy(right_x2, top_y)
        pdf.set_font("Arial", size=12)
        pdf.cell(column_width, 10, f"{shirt_fit}", align="L")

        top_y += line_gap
        pdf.set_xy(right_x, top_y)
        column_width = 20  # width for the left column text

        pdf.set_font("Arial", "B", 12)
        pdf.cell(column_width, 10, f"Chest Size:", align="R")

        pdf.set_xy(right_x2, top_y)
        pdf.set_font("Arial", size=12)
        pdf.cell(column_width, 10, f"{chest_size}", align="L")


        top_y += line_gap
        pdf.set_xy(right_x, top_y)
        column_width = 20  # width for the left column text

        pdf.set_font("Arial", "B", 12)
        pdf.cell(column_width, 10, f"Shirt Length:", align="R")

        pdf.set_xy(right_x2, top_y)
        pdf.set_font("Arial", size=12)
        pdf.cell(column_width, 10, f"{shirt_length}", align="L")



        top_y += line_gap
        pdf.set_xy(right_x, top_y)
        column_width = 20  # width for the left column text

        pdf.set_font("Arial", "B", 12)
        pdf.cell(column_width, 10, f"Across Shoulder:", align="R")

        pdf.set_xy(right_x2, top_y)
        pdf.set_font("Arial", size=12)
        pdf.cell(column_width, 10, f"{across_shoulder}", align="L")


        top_y += line_gap
        pdf.set_xy(right_x, top_y)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(column_width, 10, f"Waist:", align="R")

        pdf.set_xy(right_x2, top_y)
        pdf.set_font("Arial", size=12)
        pdf.cell(column_width, 10, f"{waist_length}", align="L")

        top_y += line_gap
        pdf.set_xy(right_x, top_y)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(column_width, 10, f"Sleeve Length:", align="R")

        pdf.set_xy(right_x2, top_y)
        pdf.set_font("Arial", size=12)
        pdf.cell(column_width, 10, f"{sleeve_length}", align="L")

        top_y += line_gap
        pdf.set_xy(right_x, top_y)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(column_width, 10, f"Collar:", align="R")

        pdf.set_xy(right_x2, top_y)
        pdf.set_font("Arial", size=12)
        pdf.cell(column_width, 10, f"{collar_size}", align="L")


    except Exception as e:
        st.write(e)

        #if os.path.exists(report_filenm):
        #    os.remove(report_filenm)




    # Save the PDF to a temporary file
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_pdf.name)

    pdf_bytes = open(temp_pdf.name, 'rb').read()


    return pdf_bytes
