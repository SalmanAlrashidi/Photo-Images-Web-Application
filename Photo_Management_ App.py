import streamlit as st
from streamlit_option_menu import option_menu
from pexels_api import API
import mysql.connector
from mysql.connector import Error


# API key for Pexels API
PEXELS_API_KEY = ''
api = API(PEXELS_API_KEY)
PAGE_LIMIT = 2
RESULTS_PER_PAGE = 1
page = 1
counter = 0

# CSS styling for background image
page_bg_img ="""
<style>
[data-testid='stAppViewContainer'] {
background-image: url("https://64.media.tumblr.com/e2037d2a3ec72560113e7da993182aa7/a77f45d80c2b8b96-06/s1280x1920/0b7ada6dcd13ac893bf8cf26f8b2be15e395bc24.pnj");
background-size: cover;
}
[data-testid="stHeader"]{
background-color: rgba(0,0,0,0);
}
</style>
"""

# Function to add a photo to the "liked" table in the MySQL database
def addLike(id,url):
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(host='localhost',
        database='',
        user='',
        password='')
        # If the connection is successful, add the id and url to the "liked" table
        if connection.is_connected():
            cursor = connection.cursor()
            mySql_insert_query = """INSERT INTO liked (id,url) 
                                VALUES (%s, %s) """
            record = (id,url)
            cursor.execute(mySql_insert_query, record)
            # Save changes to the database
            connection.commit()
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        # Close the connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

def getLikes():
    #Creates connection with the DB
    try:
        connection = mysql.connector.connect(host='localhost',
        database='',
        user='',
        password='')

        #If connection is successful, retrieves all records from table liked
        if connection.is_connected():
            sql_select_Query = "select * from liked"
            cursor = connection.cursor()
            cursor.execute(sql_select_Query)
            records = cursor.fetchall()

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        #Closes connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
    #Process list of tuples into a dict for ease of use
    records = dict(records)
    return records

# This function is used to delete a photo from the 'liked' table in the MySQL database
def deletePhoto(id):
    #Creates connection with the DB
    try:
        connection = mysql.connector.connect(host='localhost',
        database='',
        user='',
        password='')

        #If connection is successful, retrieves all records from table liked
        if connection.is_connected():
            sql_select_Query = "delete from liked where id=%s"
            id = str(id)
            cursor = connection.cursor()
            cursor.execute(sql_select_Query,(id,))

            #Saves Changes
            connection.commit()
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:

        #Closes connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


st.markdown(page_bg_img,unsafe_allow_html=True)

selected = option_menu(
    menu_title = None,
    options = ["Home","Albums","Photos"],
    icons = ["house","journal-album","images"],
    menu_icon= "cast",
    default_index=0,
    orientation= "horizontal",
    )
if selected == "Home":
    st.title(f"{selected}")
if selected == "Albums":
    st.title(f"{selected}")

    #Gets all liked images and assigns it to records
    records = getLikes()

    #Loops through the dictionary and writes the id and image url for each image
    count=0
    for key in records:
        st.write("ID: ",key)
        st.image(records[key])
        st.button("Delete",key=count,on_click=deletePhoto(key))
        count +=1
if selected == "Photos":
    st.title(f"{selected}")
    with st.form(key='searchform'):
        nav1, nav2 = st.columns([1,2])
        with nav1:
            search_term = st.text_input("Search job")
        with nav2:
            st.text('search')
            submit_search = st.form_submit_button(label='Search')
    st.success("You searched for {}".format(search_term))
    col1, col2 = st.columns([1,2])
    with col1:
        if submit_search:
            api.search(search_term, page=page, results_per_page=RESULTS_PER_PAGE)
            photos = api.get_entries()
            st.write("Total results: ", api.total_results)
            while page < PAGE_LIMIT:
                for photo in photos:
                    st.write("-----------------------------------------------")
                    st.write("Photo id: ", photo.id)
                    st.write("Photo width: ", photo.width)
                    st.write("Photo height: ", photo.height)
                    st.image(photo.original)
                    st.button("\tLike", key=counter,on_click=addLike(photo.id,photo.original))
                    counter += 1
                    if not api.has_next_page:
                        break
                    page += 1
