import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt
from shared_functions import *
from db_functions import *
from login_functions import *
import re
import smtplib
import time
from email.mime.text import MIMEText


st.set_page_config(
    page_title="Affordable Classics",
    page_icon="AC_Logo.ico",
    layout="wide"
    )


# Hide Streamlit menu and footer
hide_streamlit_style = """
        <style>
        .stToolbarActions {display: none !important;}
        </style>
        """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def send_email(to_email, subject, body,
               from_email="sender@example.com",
               smtp_server="smtp.example.com",
               port=587,
               password="YOUR_EMAIL_PASSWORD"):
    """
    Sends an email using SMTP.
    Args:
        to_email (str): Recipient email address
        subject (str): Subject of the email
        body (str): Body text of the email
        from_email (str): Your sender email address
        smtp_server (str): SMTP server address
        port (int): SMTP port (usually 587 or 465)
        password (str): Password or app-specific password for your email
    """
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    # Connect and send the email
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())

LOGO_PATH = "AC_Logo.png"  # Replace with the actual path or URL

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.auth_name = None
    st.session_state.auth_email = None
    st.session_state.auth_mobile = None
    st.session_state.auth_address = None


# Function to generate the HTML table with delete buttons
def generate_html_table(df_table):

    table_html = """
    <style>
        table {width: 100%; border-collapse: collapse; margin-top: 10px;}
        th, td {border: 1px solid #ddd; padding: 8px; text-align: left;}
        th {background-color: #f2f2f2;}
        .delete-btn {cursor: pointer; color: red; font-weight: bold;}
    </style>
    <table>
        <tr>
    """
    for columns in df_table.columns:
        table_html += f"<th>{columns}</td>"

    table_html += "<th>Delete</th></tr>"



    for i in df_table.index:
        order_id = df_table.loc[i,"ORDER_NUMBER"]
        delete_button = f'<a href="?delete={order_id}" class="delete-btn">❌</a>'
        table_html += "<tr>"

        for j in df_table.columns:
            table_html += f"<td>{df_table.loc[i,j]}</td>"

        table_html += f"<td>{delete_button}</td></tr>"

    table_html += "</table>"


    return table_html



def render_order_attributes(data: dict, attrs_per_row: int = 3):
    """
    Render dictionary attributes as an HTML table in Streamlit.

    :param data: Dictionary of attributes {key: value}
    :param attrs_per_row: How many attributes to show per row (default = 3)
    """
    html = "<table style='border-collapse:collapse;border:0px;width:100%;font-family:sans-serif;font-size:14px;'>"

    items = list(data.items())
    for i in range(0, len(items), attrs_per_row):
        html += "<tr style='border-collapse:collapse;border:0px'>"
        for j in range(attrs_per_row):
            if i + j < len(items):
                key, value = items[i + j]
                html = html + f"<td style='padding:6px 12px;font-weight:600;color:#2C64F6;border:0px solid #ddd;'>{key}:</td>"
                html = html + f"<td style='padding:6px 12px;border:0px solid #ddd;'>{value}</td>"

        html += "</tr>"

    html += "</table>"
    return html








st.write("")
c1,c2,c3 = st.columns((2,12,2))
c3.image(LOGO_PATH, width=60)  # Adjust width as needed


c2.markdown('<p style="font-size:40px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Track Orders</p>', unsafe_allow_html=True)
styles = {
    "Field_Label": "font-size:16px;font-weight: bold;text-align:right;vertical-align:bottom;color:blue;margin:0px;padding:0px;line-height:32px",
    "Field_Label_Top": "font-size:14px;font-weight: bold;text-align:right;vertical-align:bottom;color:red;margin:0px;padding:0px;line-height:18px",
    "Display_Info": "font-size:15px:text-align:left;vertical-align:bottom;color:green;margin:4px;padding:0px;line-height:24px",
    "Display_Info_Center": "font-size:14px;font-weight: bold;text-align:center;vertical-align:bottom;color:blue;margin-right:30px;margin-top:0px;margin-bottom:0px;padding:4px;line-height:18px",
    "Scheme Level": "background-color: #ffffff; font-style: italic;",
    "Calligraphy_Font": "font-family:'Dancing Script', cursive; font-size: 18px; color: #6a1b9a;",
    "Error_Message": "background-color: #E1A2AA; font-style: italic;margin-top:14px;margin-bottom:0px",


}







st.markdown('<BR><BR>',unsafe_allow_html=True)

if not st.session_state.authenticated:
    user_login()
    st.stop()


else:
    #st.markdown('<BR>',unsafe_allow_html=True)

    left, right, extreme_right = st.columns([15,3,3])
    extreme_right.markdown('<p style="{}">{}</p>'.format(styles['Display_Info'], st.session_state.auth_name), unsafe_allow_html=True)
    st.markdown('<p>',unsafe_allow_html=True)

    if extreme_right.button('Sign-Off'):
        st.write(f"{st.session_state.auth_name} has been logged off")
        st.session_state.authenticated = False
        st.session_state.auth_name = None
        st.session_state.auth_email = None
        st.session_state.auth_mobile = None
        st.session_state.auth_address = None
        time.sleep(2)
        st.rerun()
    t_track_orders, t_update_orders = st.tabs(['Track Orders','Update Orders'])

    with t_track_orders:


        df = fetch_all_orders(st.session_state.auth_email)
        df['ORDER_PRICE']= df['ORDER_PRICE'].apply(lambda x: f"Rs. {x}" if pd.notna(x) else "NA")
        disp_columns_admin = ['ORDER_NUMBER','CUSTOMER_NAME','MOBILE_NO','EMAIL','SHIRT_COLOUR','CHEST_SIZE','ORDER_STATUS','ORDER_PRICE']
        disp_columns = ['ORDER_NUMBER','SHIRT_COLOUR','CHEST_SIZE','ORDER_STATUS','ORDER_PRICE']

        customer_list = [ cust for cust in df['CUSTOMER_NAME'].unique()]
        customer_list.insert(0,'ALL')

        st.markdown('<BR>', unsafe_allow_html=True)
        # Map the selected option to colors
        color_map = {
            "White": "#F8F6F8",
            "Navy Blue": "#000080",
            "Indigo": "#4B0082",
            "Aqua Blue": "#217FA2"
        }

        if st.session_state.auth_name == 'admin':
            # Get the selected color
            col1, col2, buf, col3, col4 = st.columns([6,10,6,6,10])

            col1.markdown('<p style="{}">Customer Name:</p><BR>'.format(styles['Field_Label']), unsafe_allow_html=True)

            sel_customer_name = col2.selectbox("Select Customer Name:",customer_list , 0,label_visibility="collapsed")

            col3.markdown('<p style="{}">Order Number:</p><BR>'.format(styles['Field_Label']), unsafe_allow_html=True)

            if sel_customer_name == "ALL":
                df_cust = df
            else:
                df_cust = df[df['CUSTOMER_NAME'] == sel_customer_name ]

            order_list = [order for order in df_cust['ORDER_NUMBER']]

            if len(order_list) > 1:
                order_list.insert(0,'ALL')


            sel_order_no = col4.selectbox("Select Order Name:",order_list,0,label_visibility="collapsed")

            if sel_order_no == "ALL":
                #st.dataframe(df_cust)
                st.markdown(get_markdown_table(df_cust[disp_columns_admin]),unsafe_allow_html=True)

            else:
                #st.dataframe(df_cust[df_cust['ORDER_NUMBER'] == sel_order_no])
                st.markdown(get_markdown_table(df_cust[df_cust['ORDER_NUMBER'] == sel_order_no][disp_columns_admin]),unsafe_allow_html=True)

        else:
            st.markdown(get_markdown_table(df[disp_columns]),unsafe_allow_html=True)

    with t_update_orders:

        order_status_options = ['Initiated','Payment Done','In Progress','Ready for Delivery','Delivered','Cancelled']

        # Get the selected color

        display_columns = [ 'CUSTOMER_NAME','MOBILE_NO','EMAIL','ORDER_NUMBER','ORDER_PRICE',
           'SHIRT_COLOUR', 'CHEST_SIZE', 'HOW_TALL', 'BODY_TYPE', 'SHIRT_FIT','POCKETS','HEMLINE',
           'HALF_SLEEVE', 'SHIRT_LENGTH', 'ACROSS_SHOULDER', 'WAIST','COLLAR', 'SLEEVE_LENGTH']

        if len(df) > 0:
            upd_order_number = st.selectbox(":blue[**Select Order Number:**]",[order for order in df['ORDER_NUMBER']],0)
            st.markdown('<BR>', unsafe_allow_html=True)

            order_dtls = df[df['ORDER_NUMBER'] == upd_order_number].iloc[0]
            order_no = order_dtls['ORDER_NUMBER']
            order_status = order_dtls['ORDER_STATUS']
            addl_notes = order_dtls['ADDITIONAL_NOTES']
            delivery_addr = order_dtls['DELIVERY_ADDR']

            #st.write(order_dtls[display_columns].to_dict())

            order_dtls_dict = order_dtls[display_columns].to_dict()

            html_text = render_order_attributes(order_dtls_dict)
            st.markdown(html_text, unsafe_allow_html=True)

            #st.write(order_dtls_dict)



            current_submission = {
                "name": order_dtls_dict['CUSTOMER_NAME'],
                "email": order_dtls_dict['EMAIL'],
                "mobile_number": order_dtls_dict['MOBILE_NO'],
                "delivery_addr": delivery_addr,
                "color_option": order_dtls_dict['SHIRT_COLOUR'],
                "how_tall": order_dtls_dict['HOW_TALL'],
                "body_type": order_dtls_dict['BODY_TYPE'],
                "chest_size": order_dtls_dict['CHEST_SIZE'],
                "pockets": order_dtls_dict['POCKETS'],
                "personalise_letter": "None",
                "hemline":order_dtls_dict['HEMLINE'],
                "half_sleeve": order_dtls_dict['HALF_SLEEVE'],
                "shirt_fit":order_dtls_dict['SHIRT_FIT'],
                "shirt_price": 799

                }

            dims = {
                "Chest":order_dtls_dict['CHEST_SIZE'],
                "ShirtLength":order_dtls_dict['SHIRT_LENGTH'],
                "AcrossShoulder":order_dtls_dict['ACROSS_SHOULDER'],
                "Waist":order_dtls_dict['WAIST'],
                "SleeveLength":order_dtls_dict['SLEEVE_LENGTH'],
                "Collar":order_dtls_dict['COLLAR']
                }

            pdf_bytes = generate_pdf_report(order_no, current_submission, dims, addl_notes, order_status)
            st.markdown('<BR>', unsafe_allow_html=True)

            # Create a download button for the PDF
            col1, col2, buf = st.columns((2,2,8))
            col1.download_button(
                label="Download Invoice",
                data=pdf_bytes,
                key='download_button_1',
                file_name="Order_Summary_{}.pdf".format(st.session_state.auth_name)
            )


            if st.session_state.auth_name == "admin" or order_status in ['Initiated','Payment Done']:

                st.markdown('<BR>', unsafe_allow_html=True)
                del_button = col2.button("Delete Order")

                if del_button:
                    delete_order(upd_order_number)
                    st.rerun()




                def_status_key = order_status_options.index(order_status)

                updated_order_status = st.selectbox(":blue[**Update Status**]",order_status_options,def_status_key)
                updated_delivery_addr = st.text_area(":blue[**Update Delievery Address**]", delivery_addr,height=150)
                updated_addl_notes = st.text_area(":blue[**Update Additional Notes**]", addl_notes, height=150)

                upd_button = st.button("Update Order")

                if upd_button:

                    if updated_order_status == order_status and updated_delivery_addr.strip() == delivery_addr.strip() and updated_addl_notes.strip() == addl_notes.strip():
                        st.warning("No Change Detected for update")
                    else:
                        update_order(upd_order_number, updated_order_status,updated_delivery_addr,updated_addl_notes)
