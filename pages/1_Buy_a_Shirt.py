import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt
import plotly.graph_objects as go
#from plotly.subplots import make_subplots
import plotly.express as px
from shared_functions import *
from db_functions import *
from login_functions import *
import re
import smtplib
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
CSV_FILE = "SizeChart.csv"    # Replace with the actual CSV file name


order_sequence = 1

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.auth_name = None
    st.session_state.auth_email = None
    st.session_state.auth_mobile = None
    st.session_state.auth_address = None

if 'sequence' not in st.session_state:
    st.session_state.sequence = 0

def generate_order_no():

    # Current date/time
    now = dt.datetime.now()

    # Format the date/time part: YYMMDDHHMISS
    datetime_part = now.strftime('%y%m%d%H%M%S')

    st.session_state.sequence += 1
    # Format the sequence as a 3-digit number
    sequence_part = f"{st.session_state.sequence:03d}"

    # Construct the full order number
    order_no = f"O{datetime_part}{sequence_part}"


    return order_no


def submit_order(current_submission, dims, multiline_text, order_status, database_off="N"):

    order_no = generate_order_no()

    if database_off == "N":
        order_insert_status = insert_order(order_no,current_submission,dims,multiline_text,order_status)
        if order_insert_status == 0:
            st.success("Thank you for your order! Our Team will contact you for payment and shipping details")
        else:
            st.warning("Database Error!")

    pdf_bytes = generate_pdf_report(order_no, current_submission, dims, multiline_text, order_status)

    # Create a download button for the PDF
    st.download_button(
        label="Download Order Summary",
        data=pdf_bytes,
        key='download_button_1',
        file_name="Order_Summary_{}.pdf".format(st.session_state.auth_name)
    )



def validate_order(name, mobile_number, email):

    validation_OK = "N"

    if name:

        if mobile_number and email:
            if re.fullmatch(r"^[0-9]{10}$", mobile_number):
                if re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
                    validation_OK = "Y"
                else:
                    st.warning("Invalid email address. Please enter a valid email.")
            else:
                st.warning("Invalid mobile number. Please enter a 10-digit number.")


        else:
            st.warning("Name AND Valid Mobile Number,Email is necessary for processing the order")
    else:
        st.warning("Name cannot be blank for processing the order")

    return validation_OK


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




c1,c2,c3 = st.columns((1,12,2))
c3.markdown('<BR>',unsafe_allow_html=True)
c3.image(LOGO_PATH, width=60)  # Adjust width as needed


c2.markdown('<p style="font-size:40px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Buy a Shirt</p>', unsafe_allow_html=True)
styles = {
    "Field_Label": "font-size:16px;font-weight: bold;text-align:right;vertical-align:bottom;color:blue;margin:0px;padding:0px;line-height:32px",
    "Field_Label_Left": "font-size:16px;font-weight: bold;text-align:left;vertical-align:bottom;color:blue;margin:0px;padding:0px;line-height:32px",
    "Field_Label_Top": "font-size:16px;font-weight: bold;text-align:center;vertical-align:bottom;color:blue;margin:0px;padding:0px;line-height:32px",
    "Display_Info": "font-size:15px;font-weight: bold;text-align:left;vertical-align:bottom;color:green;margin-top:8px;margin-bottom:4px;padding:0px;line-height:32px",
    "Scheme Level": "background-color: #ffffff; font-style: italic;",
    "Calligraphy_Font": "font-family:'Dancing Script', cursive; font-size: 18px; color: #6a1b9a;",
    "Error_Message": "background-color: #E1A2AA; font-style: italic;margin-top:14px;margin-bottom:0px",


}

def shirt_price(personalise=False):
    if personalise == "None":
        return 699
    else:
        return 749


# Load brand size data
@st.cache_data
def load_brand_data():
    df = pd.read_csv(CSV_FILE)
    return df

df_brands = load_brand_data()


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
        st.rerun()


    left.write("   ")
    placeholder_price = left.empty()

    t_basic_info, t_conf_shirt,  t_size_guide = st.tabs(['Shirt Details','Shirt Measurements', 'Size Guide'])


    with t_basic_info:

        st.markdown('<BR>', unsafe_allow_html=True)

        # Map the selected option to colors
        color_map = {
            "White": "#FFFFFF",
            "Navy Blue": "#000080",
            "Indigo": "#4B0082",
            "Aqua Blue": "#217FA2"
        }
        letters = [chr(i) for i in range(65, 91)]
        letters.insert(0, "gW")
        letters.insert(0, "None")

        col1, buf, col2, col3 = st.columns([10,1,10,8])

        with col1:

            half_sleeve=st.checkbox(":blue[**Half Sleeve?**]",value=True)
            color_option = st.selectbox(":blue[**Choose Shirt Colour**]", ["White", "Navy Blue", "Indigo", "Aqua Blue"])
            selected_color = color_map[color_option]
            pockets = st.selectbox(":blue[**Pocket Type**]", ["No Pocket", "Single Pocket", "Double Pocket"],1)
            hemline = st.selectbox(":blue[**Shirt Hemline**]", ["Straight", "Straight with Cut","Rounded"],0)


            personalise_letter = st.selectbox(":blue[Embroidered Initials?]", letters,0, help="Do you want a Monogrammed Initials of your choice on the shirt pocket")

        with col2:
            st.markdown(
                f"""
                <BR><BR><div style="width: 75px; height: 38px; background-color: {selected_color}; border: 1px solid black;margin-top:32px"></div><BR><BR><BR><BR>
                """,
                unsafe_allow_html=True
            )
            if personalise_letter != "None":
                st.markdown('<BR><BR><BR><p style="{}">{}</p>'.format(styles['Calligraphy_Font'],personalise_letter), unsafe_allow_html=True)

        st.markdown('<BR>',unsafe_allow_html=True)
        submitted_1 = st.button(key="button1",label="Submit Order")

    with t_conf_shirt:


        st.markdown('<BR>', unsafe_allow_html=True)


        # Get the selected color
        col1, buf, col2, col3 = st.columns([10,0.2,8,5])

        with col1:
            how_tall = st.selectbox(":blue[**How Tall are you?**]", ["Short", "Average", "Tall","Very Tall"],1)

            body_type = st.selectbox(":blue[**Body Type**]", ["Skinny", "Slim","Regular","Overweight","Significantly Overweight"],2)

            chest_size = st.selectbox(":blue[**Chest Size**]", [a for a in range(36,51)],11,help="Snugly fit measuring tape wrapped around the chest")

            shirt_fit = st.selectbox(":blue[**Fit**]", ["Loose", "Regular", "Slim"],1)





        with col2:
            st.markdown('<BR>', unsafe_allow_html=True)

            if how_tall == "Short":
                st.markdown('<p style="{}">Less than 5 Feet 5 inch</p>'.format(styles['Display_Info']), unsafe_allow_html=True)
            elif how_tall == "Average":
                st.markdown('<p style="{}">Between 5 Feet 5 inch  - 5 Feet 8 inch</p>'.format(styles['Display_Info']), unsafe_allow_html=True)
            elif how_tall == "Tall":
                st.markdown('<p style="{}">5 Feet 9  - 6 Feet</p>'.format(styles['Display_Info']), unsafe_allow_html=True)
            else:
                st.markdown('<p style="{}">Greater than 6 Feet</p>'.format(styles['Display_Info']), unsafe_allow_html=True)

            st.markdown('<BR><p style="{}">  </p>'.format(styles['Display_Info']), unsafe_allow_html=True)

            if body_type == "Skinny":
                st.markdown('<p style="{}">BMI less than 18</p>'.format(styles['Display_Info']), unsafe_allow_html=True)
            elif body_type == "Slim":
                st.markdown('<p style="{}">BMI between 18 and 22</p>'.format(styles['Display_Info']), unsafe_allow_html=True)
            elif body_type == "Regular":
                st.markdown('<p style="{}">BMI between 22 and 27</p>'.format(styles['Display_Info']), unsafe_allow_html=True)
            elif body_type == "Overweight":
                st.markdown('<p style="{}">BMI between 28 and 30</p>'.format(styles['Display_Info']), unsafe_allow_html=True)
            else:
                st.markdown('<p style="{}">BMI greater than 30</p>'.format(styles['Display_Info']), unsafe_allow_html=True)








        c1,c2 = st.columns((15,8))


        st.markdown('<BR>',unsafe_allow_html=True)


        c1.markdown('<p style="{}">Additional Notes:</p>'.format(styles['Field_Label_Left']), unsafe_allow_html=True)
        multiline_text = c1.text_area("You can provide additional info (e.g. Actual Height / Weight, Brand and Size that best fits you, etc) ", "", height=150)
        st.markdown('<BR>',unsafe_allow_html=True)


        ignore_duplicate_order = st.checkbox("Ignore Duplicate/Multiple Order", value=False, help="Check this box if you want to allow same/duplicate order to be submitted")

        placeholder_price.markdown(f":green[**Shirt Price: {display_amount(shirt_price(personalise_letter))}**]")



        st.markdown('<BR>',unsafe_allow_html=True)
        submitted_2 = st.button(key="button2",label="Submit Order")


    if submitted_1 or submitted_2:

        #validation_OK = validate_order(name, mobile_number, email)


        #if validation_OK =="Y":



        current_submission = {
            "name": st.session_state.auth_name,
            "email": st.session_state.auth_email,
            "mobile_number": st.session_state.auth_mobile,
            "delivery_addr": st.session_state.auth_address,
            "color_option": color_option,
            "how_tall": how_tall,
            "body_type": body_type,
            "chest_size": chest_size,
            "pockets": pockets,
            "personalise_letter": personalise_letter,
            "hemline":hemline,
            "half_sleeve": half_sleeve,
            "shirt_fit":shirt_fit,
            "shirt_price": shirt_price(personalise_letter)

        }

        if how_tall == "Short":
            height = 64
        elif how_tall == "Average":
            height = 67
        elif how_tall == "Tall":
            height = 71
        else:
            height = 73


        if body_type == "Skinny":
            bmi = 18
        elif body_type == "Slim":
            bmi = 22
        elif body_type == "Regular":
            bmi = 25
        elif body_type == "Overweight":
            bmi = 28
        else:
            bmi = 32


        dims = calculate_recommended_dimensions(height, bmi, chest_size, half_sleeve)

        #st.write(current_submission['email'])


        # Check if there's a previous submission stored in session_state
        if "previous_submission" not in st.session_state:
            # If no previous submission, store the current submission
            st.session_state.previous_submission = current_submission

            submit_order(current_submission,dims,multiline_text,'Initiated')



        else:
            # Compare current submission with the last submission
            if st.session_state.previous_submission == current_submission:
                # No change from previous submission
                st.warning("No changes detected since last submission! Check Ignore Duplicate Order to ignore validation and Proceed")




                # Step 3: If user checks the box, do further processing and hide the checkbox
                if ignore_duplicate_order:
                    #st.write(ignore_duplicate_order)

                    st.success("User chose to ignore the validation warning. Proceeding...")

                    submit_order(current_submission,dims,multiline_text,'Initiated')





            else:
                # Update session_state with the new submission
                st.session_state.previous_submission = current_submission

                submit_order(current_submission,dims,multiline_text,'Initiated')





    #with t_my_orders:

    #    if mobile_number:

    #        df_orders = fetch_past_orders(mobile_number)

    #        if len(df_orders) > 0:
    #            st.markdown('<p style="{}">Past Orders for Mobile No - {}</p><BR>'.format(styles['Field_Label_Left'],mobile_number), unsafe_allow_html=True)

    #            st.dataframe(df_orders)
    #        else:
    #            st.markdown('<BR><p style="font-size:16px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">No Orders exists for you</p>', unsafe_allow_html=True)

    #    else:
    #        st.markdown('<BR><p style="font-size:16px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">No Orders exists for you</p>', unsafe_allow_html=True)


    with t_size_guide:

        c1,buf,c4 = st.columns((4,1,4))

        c4.markdown('<BR><p style="font-size:18px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Size Guide</p>', unsafe_allow_html=True)
        c4.image("SizeGuide.PNG", width=400)  # Adjust width as needed

        c1.markdown('<BR><BR>',unsafe_allow_html=True)

        #c1.dataframe(df_brands)

        with c1:
            c1_1, c1_2 =st.columns((3,4))

            brand_list =df_brands['Brand'].unique().tolist()
            c1_1.markdown('<p style="font-size:16px;font-weight: bold;text-align:right;vertical-align:middle;color:blue;margin-top:5px;padding:5px">Choose Brand:</p>', unsafe_allow_html=True)
            brand = c1_2.selectbox("Brand",brand_list,0, label_visibility='collapsed')

            brand_size_list = df_brands[df_brands['Brand']== brand]['Size'].tolist()

            c1_1.markdown('<p style="font-size:16px;font-weight: bold;text-align:right;vertical-align:middle;color:blue;margin-top:5px;padding:5px">Brand Size:</p>', unsafe_allow_html=True)
            brand_size = c1_2.selectbox("Brand Size",brand_size_list,0, label_visibility='collapsed')

            dtls = df_brands[(df_brands['Brand'] == brand) & (df_brands['Size']==brand_size)].iloc[0]

            c1_1.markdown('<p style="font-size:16px;font-weight: bold;text-align:right;vertical-align:middle;color:blue;margin-top:5px;padding:5px">Chest:</p>', unsafe_allow_html=True)
            c1_2.markdown(f'<p style="font-size:16px;font-weight: bold;text-align:left;vertical-align:middle;color:red;margin-top:5px;padding:5px">{dtls["Chest"]}</p>', unsafe_allow_html=True)

            c1_1.markdown('<p style="font-size:16px;font-weight: bold;text-align:right;vertical-align:middle;color:blue;margin-top:5px;padding:5px">Length:</p>', unsafe_allow_html=True)
            c1_2.markdown(f'<p style="font-size:16px;font-weight: bold;text-align:left;vertical-align:middle;color:red;margin-top:5px;padding:5px">{dtls["Length"]}</p>', unsafe_allow_html=True)

            c1_1.markdown('<p style="font-size:16px;font-weight: bold;text-align:right;vertical-align:middle;color:blue;margin-top:5px;padding:5px">Across Shoulder:</p>', unsafe_allow_html=True)
            c1_2.markdown(f'<p style="font-size:16px;font-weight: bold;text-align:left;vertical-align:middle;color:red;margin-top:5px;padding:5px">{dtls["Across Shoulder"]}</p>', unsafe_allow_html=True)

            c1_1.markdown('<p style="font-size:16px;font-weight: bold;text-align:right;vertical-align:middle;color:blue;margin-top:5px;padding:5px">Waist:</p>', unsafe_allow_html=True)
            c1_2.markdown(f'<p style="font-size:16px;font-weight: bold;text-align:left;vertical-align:middle;color:red;margin-top:5px;padding:5px">{dtls["Waist"]}</p>', unsafe_allow_html=True)

            c1_1.markdown('<p style="font-size:16px;font-weight: bold;text-align:right;vertical-align:middle;color:blue;margin-top:5px;padding:5px">Sleeve:</p>', unsafe_allow_html=True)
            c1_2.markdown(f'<p style="font-size:16px;font-weight: bold;text-align:left;vertical-align:middle;color:red;margin-top:5px;padding:5px">{dtls["Sleeve"]}</p>', unsafe_allow_html=True)

            c1_1.markdown('<p style="font-size:16px;font-weight: bold;text-align:right;vertical-align:middle;color:blue;margin-top:5px;padding:5px">Collar:</p>', unsafe_allow_html=True)
            c1_2.markdown(f'<p style="font-size:16px;font-weight: bold;text-align:left;vertical-align:middle;color:red;margin-top:5px;padding:5px">{dtls["Collar"]}</p>', unsafe_allow_html=True)








    #st.write(dims)
