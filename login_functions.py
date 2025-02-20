import streamlit as st
import hashlib
import re
from shared_functions import *
from db_functions import *





if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.auth_name = None
    st.session_state.auth_email = None
    st.session_state.auth_mobile = None
    st.session_state.auth_address = None



styles = {
    "Field_Label": "font-size:16px;font-weight: bold;text-align:right;vertical-align:bottom;color:blue;margin:0px;padding:0px;line-height:32px",
    "Field_Label_Left": "font-size:16px;font-weight: bold;text-align:left;vertical-align:bottom;color:blue;margin:0px;padding:0px;line-height:32px",
    "Field_Label_Top": "font-size:16px;font-weight: bold;text-align:center;vertical-align:bottom;color:blue;margin:0px;padding:0px;line-height:32px",
    "Display_Info": "font-size:15px;font-weight: bold;text-align:left;vertical-align:bottom;color:green;margin-top:8px;margin-bottom:4px;padding:0px;line-height:32px",
    "Scheme Level": "background-color: #ffffff; font-style: italic;",
    "Calligraphy_Font": "font-family:'Dancing Script', cursive; font-size: 18px; color: #6a1b9a;",
    "Error_Message": "background-color: #E1A2AA; font-style: italic;margin-top:14px;margin-bottom:0px",


}

def user_login():

    # Streamlit App

    left, mid, right = st.columns((2,10,4))
    mid.title("Sign-in/Sign-up Screen")


    # Tabs for Sign-up and Login
    tab1, tab2 = mid.tabs(["  Sign-in  ", "  Sign-up  "])

    # Sign-up Tab
    with tab2:

        #st.header("Create an Account")

        name = st.text_input(":blue[**Full Name**]")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        mobile_number = st.text_input("Mobile Number")

        addr = st.text_area("Customer Address", "", height=150)

        if name.lower() == "admin":
            st.markdown('<p style="{}">{} is not a valid name</p><BR>'.format(styles['Error_Message'],name), unsafe_allow_html=True)


        if mobile_number:
            if re.fullmatch(r"^[0-9]{10}$", mobile_number):
                mobile_number_validation = True
            else:
                st.markdown('<p style="{}">Invalid mobile number. Please enter a 10-digit number.</p><BR>'.format(styles['Error_Message']), unsafe_allow_html=True)
                mobile_number_validation = False
        else:
            mobile_number_validation = False



        if email:
            if re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
                email_validation = True


            else:
                st.markdown('<p style="{}">Invalid email address. Please enter a valid email.</p><BR>'.format(styles['Error_Message']), unsafe_allow_html=True)
                email_validation = False
        else:
            email_validation = False


        if st.button("Sign Up"):
            #st.write(name,mobile_number_validation,password,email_validation)

            if name and email_validation and mobile_number_validation and password:
                add_user(name, email, mobile_number, password, addr)
            else:
                st.error("Please fill in all fields.")

    # Sign-in Tab
    with tab1:
        #st.header("Log In")
        login_email = st.text_input("Email Address", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Log In"):
            if login_email and login_password:
                auth_df = authenticate_user(login_email, login_password)
                auth_passwd = auth_df['PASSWORD'].iloc[0]

                if hash_password(login_password) == auth_passwd:
                    st.session_state.authenticated = True
                    st.session_state.auth_name = auth_df['CUSTOMER_NAME'].iloc[0]
                    st.session_state.auth_email = auth_df['EMAIL'].iloc[0]
                    st.session_state.auth_mobile = auth_df['MOBILE_NUMBER'].iloc[0]
                    st.session_state.auth_address = auth_df['CUSTOMER_ADDRESS'].iloc[0]

                if st.session_state.authenticated:
                    st.write("User is authenticated")
                    st.write(st.session_state.auth_name)
                    st.write(st.session_state.auth_email)
                    st.write(st.session_state.auth_mobile)
                    st.write(st.session_state.auth_address)

                    st.rerun()
