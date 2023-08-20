# INSY 660 - Coding Foundations for Analytics
# Final Project - Group 14
# Part 2 - Product Analytics
# Niki Mahmoodzadeh, Jared Balakrishnan

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px


# Specifying the correct data type mapping for the dataframes that will be read from .csv files. Important to do so since pandas' object type slows down as the size of the dataset grows larger.
category_mapping_types_conversion = {
    "category_id": "int64",
    "category_name": "string"
}

menu_mapping_types_conversion = {
    "item_id": "int64",
    "item_name": "string",
    "description": "string",
    "price": "float32",
    "category_id": "int64",
    "is_vegetarian": "boolean",
    "is_spicy": "boolean",
    "is_gluten_free": "boolean"
}

orders_mapping_types_conversion = {
    "order_id": "int64",
    "item_id": "int64",
    "customer_id": "int64",
    "quantity": "int64",
    "special_request": "string",
    "subtotal": "float64",
    "payment_method": "category",
    "order_status": "category"
}

feedback_mapping_types_conversion = {
    "Customer_ID": "int64",
    "Item_ID": "int64",
    "Feedback_Text": "string",
    "Rating": "float64",
    "Feedback_Category": "category"
}

# Writing functions to process each available dataset, do some processing and return a pandas dataframe
@st.cache_data
def read_orders_dataset(filename: str) -> pd.DataFrame:
    """Reading in the .csv file containing order data"""
    orders_raw = pd.read_csv(filename)
    orders = orders_raw.astype(orders_mapping_types_conversion)
    orders['order_placed'] = pd.to_datetime(orders['order_placed'])
    return orders 

@st.cache_data
def read_category_data(filename:str) -> pd.DataFrame:
    """Read in the .csv file containing the categories for the Quéchat menu items."""
    categories_raw = pd.read_csv(filename)
    categories = categories_raw.astype(category_mapping_types_conversion)
    return categories

@st.cache_data
def read_menu_data(filename: str) -> pd.DataFrame:
    """Read in the .csv file containing the menu for the Quéchat Restaurant."""
    menu_raw = pd.read_csv(filename)
    menu = menu_raw.astype(menu_mapping_types_conversion)
    return menu

@st.cache_data
def read_feedback_dataset(filename: str) -> pd.DataFrame:
    """ Read in the .csv file containing existing feedback data."""
    feedback_raw = pd.read_csv(filename)
    feedback = feedback_raw.astype(feedback_mapping_types_conversion)
    feedback['Submission_Timestamp'] = pd.to_datetime(feedback['Submission_Timestamp'])
    return feedback

# reading in the files to generate our dataframes
categories_df = read_category_data('categories.csv')
menu_df = read_menu_data('menu.csv')
orders_df = read_orders_dataset('order_data.csv')

feedback_df = read_feedback_dataset('feedback_data.csv')
feedback_df.columns = map(str.lower, feedback_df.columns) 

# Merging dataframes to consolidate data for different purposes
orders_menu = orders_df.merge(menu_df, how="left", on="item_id")
overall_data = orders_menu.merge(categories_df, how="left", on="category_id")
feedback_overall = feedback_df.merge(menu_df, how="left", on="item_id")

# Calculating overall business metrics
# GMV - Gross Merchandise Value
# Average Order - $ amount of the average order placed at the restaurant
gmv = f"$ {((overall_data['price'] * overall_data['quantity']).sum()):.0f}"
avg_order = f"$ {((overall_data['price'] * overall_data['quantity']).mean()).round(2)}"

# Orders Placed - Total Number of Orders Placed
# Orders Completed - Total Number of Orders fulfilled by the restaurant
# Orders Canceled - Total Number of Orders that were canceled by the customers
orders_placed = f"{overall_data['order_id'].nunique()}"
orders_completed = f"{overall_data[overall_data['order_status'].isin(['Completed', 'In Progress'])]['order_id'].nunique()}"
orders_canceled = f"{overall_data[overall_data['order_status'] == 'Cancelled']['order_id'].nunique()}"


most_ordered = overall_data['item_name'].value_counts().idxmax() # most ordered item on the menu
most_ordered_category = overall_data['category_name'].value_counts().idxmax() # most ordered category on the menu
most_favorite_item = feedback_overall[feedback_overall['rating'] == 5.0]['item_name'].value_counts().idxmax() # most favorite item based on customer feedback
most_liked_aspect = feedback_overall[feedback_overall['rating'] == 5.0]['feedback_category'].value_counts().idxmax() # most favorite aspect of the restaurant based on customer feedback
least_liked_aspect = feedback_overall[feedback_overall['rating'] < 2.0]['feedback_category'].value_counts().idxmax() # least favorite aspect of the restaurant based on customer feedback

# Customer Trend Metrics
unique_customers = overall_data['customer_id'].nunique() # Number of unique customers served

# Processing to calculate statistics for repeat customers
repeat_customers = pd.DataFrame(overall_data['customer_id'].value_counts())
repeat_customers.reset_index(inplace=True)
repeat_customers.columns = ['customer_id', 'occurrences']

most_valuable_customer = overall_data['customer_id'].value_counts().idxmax() # customer that placed the most orders
more_than_twice = repeat_customers[repeat_customers['occurrences'] > 2]['customer_id'].count() # customers that placed more than 2 orders
more_than_five = repeat_customers[repeat_customers['occurrences'] > 5]['customer_id'].count() # customers that placed more than 5 orders
more_than_ten = repeat_customers[repeat_customers['occurrences'] > 10]['customer_id'].count() # customers that placed more than 10 orders

# Processing to understand payment trends
payment_trends = pd.DataFrame(overall_data['payment_method'].value_counts())
payment_trends.reset_index(inplace=True)
payment_trends.columns = ['Payment Method', 'Number of Transactions']

def follow_up():

    follow_up_overall = st.text_input("Is there anything else you would like to know today?")

    if follow_up_overall == "y":
        pass
    elif follow_up_overall == "n":
        st.markdown("Thank you so much for visiting the Quechat Analytics Portal. See you soon!")

def overall_metrics():

    """Function to synthesize overall metrics."""

    col1, col2, col3 = st.columns(3, gap="medium")
    col1.metric("GMV", value = gmv)
    col2.metric("Orders Placed", value = overall_data['order_id'].nunique())
    col3.metric("Unique Customers Served", value=unique_customers)

    col4, col5, col6 = st.columns(3, gap="medium")

    col4.metric("Average Order Value", value=avg_order)
    col5.metric("Orders Completed", value= orders_completed)
    col6.metric("Orders Canceled", value = orders_canceled)

    st.markdown(f"Your restaurant recorded {gmv} in sales. There were a total of {orders_placed} orders placed, of which {orders_completed} were fulfilled and {orders_canceled} were canceled.")

    follow_up()

def payment_metrics():
        
        """ Function to render payment metrics onto the browser."""

        st.subheader('Payment Trends')

        st.markdown(f"The most preferred payment method used by your customers was {overall_data['payment_method'].value_counts().idxmax()}, used in transactions. ")

        st.markdown("Below shown is a breakdown of the payment methods used by customers to pay for services at your restaurant:")

        plot_y = payment_trends['Number of Transactions'].tolist()
        plot_labels = payment_trends['Payment Method'].tolist()

        fig, ax = plt.subplots()
        plt.pie(plot_y, labels= plot_labels, autopct='%1.1f%%')
        st.pyplot(fig)

        follow_up()

def customer_metrics():

    """Function to synthesize customer-specific metrics."""

    st.subheader('Customer Trends')
    st.markdown(f"Your customers absolutely love coming back to your restaurant! Out of your {unique_customers} unique customers, {more_than_twice} ordered more than twice. {more_than_five} ordered more than 5 times, and {more_than_ten} ORDERED MORE THAN 10 TIMES!")
    st.markdown(f"Your MVC (Most Valuable Customer) ordered from you a record {14} times!")
    st.markdown(f"Customers love your *{most_ordered_category}* items the most.")
    st.markdown(f"The most popular item among your customers is the *{most_ordered}*.")
    st.markdown(f"According to customer feedback, the most loved item on your menu is the *{most_favorite_item}*.")
    st.markdown(f"Finally, what do customers like the most about your restaurant? It is the **{most_liked_aspect}**.")
    st.markdown(f"However, this doesn't mean that customers don't have recommendations. Taking into account the feedback received from your customers, the most recommended area of improvement for your restaurant is its **{least_liked_aspect}**.")
    follow_up()


# Overall Chatbot workflow - this is what is shown on the browser

st.markdown('## Hi Niki, Welcome to your Analytics portal.')

st.markdown("Here you will be able to find more information about your restaurant's performance. We hope that the analytics compiled will help you understand your business better, and help you improve your service and keep your customers happy.")

st.markdown("The following information is available for you to examine via this portal:")
st.markdown("""
- Overall Analytics
- Payment Trends
- Customer Behavior
- Charts            
            """)

st.markdown("To get your answers to these questions, please work with our online assistant below: ")

def analytics_chatbot():

    """Trigger the chat bot"""

    opening_question = st.text_input("Hi Niki, what would you like to know more about today? ")

    if opening_question.lower() == "overall":
        
        overall_metrics()

    elif opening_question.lower() == "payments":

        payment_metrics()
    
    elif opening_question.lower() == "customer":

        customer_metrics()



analytics_chatbot()