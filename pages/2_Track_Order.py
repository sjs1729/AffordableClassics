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












st.write("")
c1,c2,c3 = st.columns((2,12,2))
c3.image(LOGO_PATH, width=60)  # Adjust width as needed


c2.markdown('<p style="font-size:40px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Track Orders</p>', unsafe_allow_html=True)
styles = {
    "Field_Label": "font-size:16px;font-weight: bold;text-align:right;vertical-align:bottom;color:blue;margin:0px;padding:0px;line-height:32px",
    "Field_Label_Top": "font-size:14px;font-weight: bold;text-align:right;vertical-align:bottom;color:red;margin:0px;padding:0px;line-height:18px",
    "Display_Info": "font-size:14px;font-weight: bold;text-align:left;vertical-align:bottom;color:blue;margin-top:0px;margin-bottom:0px;padding:0px;line-height:18px",
    "Scheme Level": "background-color: #ffffff; font-style: italic;",
    "Calligraphy_Font": "font-family:'Dancing Script', cursive; font-size: 18px; color: #6a1b9a;",
    "Error_Message": "background-color: #E1A2AA; font-style: italic;margin-top:14px;margin-bottom:0px",


}







st.markdown('<BR><BR>',unsafe_allow_html=True)

if not st.session_state.authenticated:
    user_login()
    st.stop()


else:
    st.markdown('<BR><BR>',unsafe_allow_html=True)

    left, right, extreme_right = st.columns([15,3,3])
    right.markdown('<p style="{}">{}</p><BR>'.format(styles['Field_Label'], st.session_state.auth_name), unsafe_allow_html=True)


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
        col1, col2, buf = st.columns([6,14,14])

        display_columns = [ 'CUSTOMER_NAME', 'MOBILE_NO', 'EMAIL',
           'SHIRT_COLOUR', 'CHEST_SIZE', 'HOW_TALL', 'BODY_TYPE', 'SHIRT_FIT','POCKETS',
           'HEMLINE', 'HALF_SLEEVE', 'SHIRT_LENGTH', 'ACROSS_SHOULDER', 'WAIST',
           'COLLAR', 'SLEEVE_LENGTH']

        col1.markdown('<p style="{}">Order Number:</p><BR><BR>'.format(styles['Field_Label']), unsafe_allow_html=True)
        upd_order_number = col2.selectbox("Select Order Name:",[order for order in df['ORDER_NUMBER']],0,label_visibility="collapsed")

        order_dtls = df[df['ORDER_NUMBER'] == upd_order_number].iloc[0]
        order_status = order_dtls['ORDER_STATUS']
        addl_notes = order_dtls['ADDITIONAL_NOTES']
        delivery_addr = order_dtls['DELIVERY_ADDR']

        #st.write(order_dtls[display_columns].to_dict())

        order_dtls_dict = order_dtls[display_columns].to_dict()

        col1, col2, col3, col4 = st.columns([6,12,6,12])

        counter = 0

        for j in order_dtls_dict.keys():
            if counter % 2 == 0:
                col1.markdown('<p style="{}">{}:</p><BR>'.format(styles['Field_Label_Top'],j), unsafe_allow_html=True)
                col2.markdown('<p style="{}">{}</p><BR>'.format(styles['Display_Info'],order_dtls_dict[j]), unsafe_allow_html=True)

            else:
                col3.markdown('<p style="{}">{}:</p><BR>'.format(styles['Field_Label_Top'],j), unsafe_allow_html=True)
                col4.markdown('<p style="{}">{}</p><BR>'.format(styles['Display_Info'],order_dtls_dict[j]), unsafe_allow_html=True)

            counter += 1

        if st.session_state.auth_name == "admin" or order_status in ['Initiated','Payment Done']:
            st.write("-------------")

            col1, col2, col3 = st.columns([5,9,15])

            def_status_key = order_status_options.index(order_status)

            updated_order_status = col1.selectbox("Update Status:",order_status_options,def_status_key)
            updated_delivery_addr = col2.text_area("Update Delievery Address ", delivery_addr,height=150)
            updated_addl_notes = col3.text_area("Update Additional Notes", addl_notes, height=150)

            upd_button = col2.button("Update Order")

            if upd_button:


                if updated_order_status == order_status and updated_delivery_addr.strip() == delivery_addr.strip() and updated_addl_notes.strip() == addl_notes.strip():
                    st.warning("No Change Detected for update")
                else:
                    update_order(upd_order_number, updated_order_status,updated_delivery_addr,updated_addl_notes)

            del_button = col3.button("Delete Order")

            if del_button:
                delete_order(upd_order_number)
                st.rerun()
