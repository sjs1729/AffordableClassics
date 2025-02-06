import pandas as pd
import mysql.connector
from mysql.connector import Error
import streamlit as st
import hashlib



# Database connection details
db_config = {
    'host': '107.180.118.206',
    'user': 'growealth',
    'password': 'growealth@123',
    'database': 'growealth',
}


if 'signed_on' not in st.session_state:
    st.session_state.signed_on = {}


# Function to connect to the MySQL database
def connect_to_database():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def insert_order(order_no, curr_submission, shirt_dims, additional_notes, curr_status):

    #st.write("Checking Connected")
    #return 0
    # Connect to the MySQL database
    connection = connect_to_database()

    if connection.is_connected():
        # Fetch data using Pandas

        #st.write("Connected")


        insert_query = """
            INSERT INTO CUSTOMER_ORDERS (
              ORDER_NUMBER,
              CUSTOMER_NAME,
              MOBILE_NO,
              EMAIL,
              DELIVERY_ADDR,
              SHIRT_COLOUR,
              CHEST_SIZE,
              HOW_TALL,
              BODY_TYPE,
              POCKETS,
              HEMLINE,
              HALF_SLEEVE,
              SHIRT_LENGTH,
              ACROSS_SHOULDER,
              WAIST,
              COLLAR,
              SLEEVE_LENGTH,
              ADDITIONAL_NOTES,
              ORDER_STATUS,
              SHIRT_FIT,
              ORDER_PRICE
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        if curr_submission["half_sleeve"]:
            half_sleeve = "Y"
        else:
            half_sleeve = "N"

        # Create a cursor from the existing connection
        cursor = connection.cursor()
        try:
            # Execute the insert query with parameter binding
            cursor.execute(
                insert_query,
                (
                    order_no,
                    curr_submission["name"],
                    curr_submission["mobile_number"],
                    curr_submission["email"],
                    curr_submission["delivery_addr"],
                    curr_submission["color_option"],
                    curr_submission["chest_size"],
                    curr_submission["how_tall"],
                    curr_submission["body_type"],
                    curr_submission["pockets"],
                    curr_submission["hemline"],
                    half_sleeve,
                    shirt_dims["ShirtLength"],
                    shirt_dims["AcrossShoulder"],
                    shirt_dims["Waist"],
                    shirt_dims["Collar"],
                    shirt_dims["SleeveLength"],
                    additional_notes,
                    curr_status,
                    curr_submission["shirt_fit"],
                    curr_submission["shirt_price"]
                )
            )
            # Commit the transaction
            connection.commit()
            st.success("Customer Order inserted successfully!")
        except Exception as e:
            connection.rollback()
            st.error(f"Error inserting order: {e}")
            return -1

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                return 0
    else:

        return -1


def fetch_all_orders(user_email):
    """
    Fetches a dataset from a remote MySQL database based on a query.

    Args:
        query (str): The SQL query to execute.

    Returns:
        pd.DataFrame: The resulting dataset as a Pandas DataFrame.
    """
    try:
        #st.write("function called")
        # Connect to the MySQL database
        connection = connect_to_database()

        if connection.is_connected():
            # Fetch data using Pandas
            if user_email == 'helpdesk@gro-wealth.in':
                df = pd.read_sql(f"SELECT * FROM CUSTOMER_ORDERS", connection)
            else:
                df = pd.read_sql(f"SELECT * FROM CUSTOMER_ORDERS WHERE EMAIL = '{user_email}'", connection)

            return df

    except Error as e:
        print(f"Error: {e}")
        return None

    finally:
        if connection.is_connected():
            connection.close()


def fetch_past_orders(mobile_no):
    """
    Fetches a dataset from a remote MySQL database based on a query.

    Args:
        query (str): The SQL query to execute.

    Returns:
        pd.DataFrame: The resulting dataset as a Pandas DataFrame.
    """
    try:
        #st.write("function called")
        # Connect to the MySQL database
        connection = connect_to_database()

        if connection.is_connected():
            # Fetch data using Pandas
            df = pd.read_sql(f"SELECT * FROM CUSTOMER_ORDERS WHERE MOBILE_NO = '{mobile_no}'", connection)
            return df

    except Error as e:
        print(f"Error: {e}")
        return None

    finally:
        if connection.is_connected():
            connection.close()


def delete_order(order_no):

    #st.write("Checking Connected")
    #return 0
    # Connect to the MySQL database
    connection = connect_to_database()

    if connection.is_connected():
        # Fetch data using Pandas

        #st.write("Connected")


        delete_order_query = f"DELETE FROM  CUSTOMER_ORDERS WHERE ORDER_NUMBER = '{order_no}'"


        # Create a cursor from the existing connection
        cursor = connection.cursor()
        try:
            # Execute the insert query with parameter binding
            cursor.execute(delete_order_query)

            connection.commit()
            st.success(f"Customer Order {order_no} deleted successfully!")
        except Exception as e:
            connection.rollback()
            st.error(f"Error inserting order: {e}")
            return -1

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                return 0
    else:

        return -1


def update_order(order_no, order_status, delivery_addr, addl_notes):

    #st.write("Checking Connected")
    #return 0
    # Connect to the MySQL database
    connection = connect_to_database()
    if connection.is_connected():
        # Fetch data using Pandas

        #st.write("Connected")


        update_order_query = """
            UPDATE CUSTOMER_ORDERS SET ORDER_STATUS= %s,
                                       DELIVERY_ADDR = %s,
                                       ADDITIONAL_NOTES = %s
                                       WHERE ORDER_NUMBER = %s
            """


        #st.write(update_order_query )
        # Create a cursor from the existing connection
        cursor = connection.cursor()
        try:
            # Execute the insert query with parameter binding
            cursor.execute(update_order_query, (order_status, delivery_addr, addl_notes, order_no))
            #st.write(cursor.statement)

            connection.commit()
            st.success(f"Customer Order {order_no} updated successfully!")
        except Exception as e:
            connection.rollback()
            st.error(f"Error inserting order: {e}")
            return -1

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                return 0
    else:

        return -1


# Function to add user to the database
def add_user(name, email, mobile_number, password, addr):

    connection = connect_to_database()
    if connection.is_connected():
        try:
            cursor = connection.cursor()
            hashed_pw = hash_password(password)
            cursor.execute("INSERT INTO USERS (CUSTOMER_NAME, EMAIL, PASSWORD, MOBILE_NUMBER, CUSTOMER_ADDRESS) VALUES (%s, %s, %s, %s, %s)", (name, email, hashed_pw, mobile_number, addr))
            connection.commit()
            st.success("Sign-up successful! You can now log in.")
        except Error as e:
            st.error(f"Error: {e}")
        finally:
            cursor.close()
            connection.close()


def authenticate_user(email, password):
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            hashed_pw = hash_password(password)
            cursor.execute("SELECT * FROM USERS WHERE email = %s AND password = %s", (email, hashed_pw))
            user = cursor.fetchone()
            return user
        except Error as e:
            st.error(f"Error: {e}")
            return None
        finally:
            cursor.close()
            connection.close()


def authenticate_user(email, password):

    auth_user = {'status':0, 'user_id':'','name':'', 'mobile_no':'', 'address':''}

    try:
        #st.write("function called")
        # Connect to the MySQL database
        connection = connect_to_database()

        if connection.is_connected():
            # Fetch data using Pandas
            df = pd.read_sql(f"SELECT * FROM USERS WHERE EMAIL = '{email}'", connection)

            if len(df) == 0:
                st.warning(f"{email} does not exists, please register email by signing up")
                st.stop()
            elif len(df) == 1:
                return df
    except Error as e:
        print(f"Error: {e}")
        return None

    finally:
        if connection.is_connected():
            connection.close()
