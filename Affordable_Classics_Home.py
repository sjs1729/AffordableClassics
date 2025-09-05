import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
import platform


# Path or URL for your logo
LOGO_PATH = "AC_Logo.png"  # Replace with the actual path or URL
CSV_FILE = "SizeChart.csv"    # Replace with the actual CSV file name


st.set_page_config(
    page_title="Affordable Classics",
    page_icon="AC_Logo.ico",
    layout="wide"
    )


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

st.write(platform.system())

c1,c2,c3 = st.columns((10,2,10))
c2.markdown('<BR>',unsafe_allow_html=True)
c2.image(LOGO_PATH, width=85)  # Adjust width as needed


st.markdown('<p style="font-size:40px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Affordable Classics</p>', unsafe_allow_html=True)

html_text = '<BR><div style="font-family: Arial, sans-serif; font-size: 1.1em; line-height: 1.5;color:#941751"> \
  <strong>Experience the luxury of a custom-tailored, linen-blend shirt designed just for you—without breaking the bank.</strong><br> \
  Our bespoke creations, bring comfort, style and personal flair right to your doorstep. \
  <em>Place your order today and embrace the elegance of Affordable Classics.</em></div><BR><BR>'

st.markdown(html_text, unsafe_allow_html=True)


c1,buf,c2 = st.columns((26,3,12))
c2.image("Shirt_White.png", width=180)  # Adjust width as needed

html_subtext = '<BR><BR><div style="font-family: Arial, sans-serif; font-size: 1.0em; line-height: 1.5; color:#941751"> \
  Currently we are offering the  choice of colours - <span><strong>Magnificient White</strong></span>, <span><strong>Navy Blue</strong></span>, <span><strong>Indigo</strong></span> & <span><strong>Aqua Blue</strong></span>.<br><br> \
  The Linen blend fabric is so comfortable that you will never want to take it off. <br><br>\
  <em>Hurry, place your order now (<span><strong>Side Menu --> Buy a Shirt</strong></span>) and be a part of <strong><span>Affordable Classics</strong></span>.</em></div><BR><BR>'

c1.markdown(html_subtext, unsafe_allow_html=True)


st.markdown('<BR><p style="font-size:18px;font-weight: bold;text-align:left;vertical-align:middle;color:blue;margin:0px;padding:0px">Contact:</p>', unsafe_allow_html=True)
st.markdown(":phone: +91 9836064237")
st.markdown(":email: [helpdesk@gro-wealth.in](emailto:helpdesk@gro-wealth.in)")
