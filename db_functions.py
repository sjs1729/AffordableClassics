import pandas as pd
import mysql.connector
from mysql.connector import Error
import streamlit as st


# Database connection details
db_config = {
    'host': st.secrets["DB_HOST"],
    'user':  st.secrets["DB_USER"],
    'password':  st.secrets["DB_PASSWORD"],
    'database':  st.secrets["DB_NAME"],
}

# Function to connect to the MySQL database
def connect_to_database():
    #try:
    connection = mysql.connector.connect(**db_config)
    st.write(connection)
    return connection
    #except Error as e:
        #st.error(f"Error connecting to database: {e}")
        #return None


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
              SHIRT_FIT
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
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
                    curr_submission["shirt_fit"]
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


@st.cache_data()
def fetch_all_orders():
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
            df = pd.read_sql("SELECT * FROM CUSTOMER_ORDERS", connection)
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
