import datetime
import numpy as np
import pandas as pd
import streamlit as st
# import pickle
from PIL import Image
import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import time
from Historical_Price import Historical_Price
import io
import json
import ast

################
# About this Web APP

# image = Image.open('app/download.jpeg')

# st.set_page_config(layout="wide")
# st.image(image, use_column_width=True)

st.set_page_config(layout="wide") 
st.write("""
# Metaverse Web App

Data obtained from the OpenSea API.

***
""")
################

################
# function: reading data from opensea
# ref: (link)
def API_request_Opensea(limit, time_data, time_start, lines_to_save_data, APIKEY, contract_address):
    offset = 0
    counter = 0
    df = pd.DataFrame({}, dtype=str)
    # url = "https://api.opensea.io/api/v1/events"
    while(time_data>time_start):
        # querystring = {"only_opensea":"true","offset":str(offset),"limit":str(limit), "event_type":"successful", 'occurred_before':time_data} "&occurred_after=1648823844000
        url = "https://api.opensea.io/api/v1/events?only_opensea=true&asset_contract_address="+contract_address+"&event_type=successful&occurred_before="+str(time_data)

        headers = {
            "Accept": "application/json",
            "X-API-KEY": APIKEY
        }
        response = requests.request("GET", url, headers=headers)

        #print(response.status_code)
        if response.status_code==200:
            df_supp = pd.DataFrame({}, dtype=str)
            for key in response.json()['asset_events']:
                df_supp = df_supp.append(key, ignore_index=True)
            
            df = df.append(df_supp, ignore_index=True)
            
            time_data_supp = pd.to_datetime(df_supp.created_date.unique()).min()
            
            if offset>0:
                if (time_data -  time_data_supp)>pd.Timedelta('5 hours'): 
                    offset=0
                    time_data=time_data_supp
                else: offset+=limit
            else:
                if time_data == time_data_supp: offset+=limit
                else: time_data = time_data_supp
            
            
            counter +=limit
            if counter%lines_to_save_data==0:
                print(len(df_supp), len(df), pd.to_datetime(time_data), time_data_supp, offset)
                return filedownload(df)
                # df.to_csv(data_folder+'NFT_OpenSea_'+str(time_start.month)+'_'+str(time_start.year)+'.csv.gz',
                #             index=False)
        time.sleep(1)
    
    if len(df)>0:
        # df.to_csv(data_folder+'NFT_OpenSea_'+str(time_start.month)+'_'+str(time_start.year)+'.csv.gz', index=False)
        return filedownload(df)
    else:
        print('No data in this month')
        

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="crypto.csv">Download CSV File</a>'
    return href

################
# Layout (sidebar)

option = st.sidebar.selectbox(
     'What would you like to do?',
     ('Download NFTs Data', 'Data Analysis'))


################
# for option: Download NFTs Data
if option == 'Download NFTs Data':

    st.sidebar.header('Time Period')
    start_date = st.sidebar.date_input(
        "From",
        datetime.date(2022, 4, 1), key="1")
    end_date = st.sidebar.date_input(
        "To",
        datetime.date(2022, 4, 6), key="2")


    st.sidebar.header('API KEY')
    USERS_input1 = ""
    APIKEYSTR = st.sidebar.text_input("OPENSEA API input", USERS_input1, key="1")

    st.sidebar.header('NFTs Contract addresses')

    ## Read USERS input
    USERS_input = "0x7bd29408f11d2bfc23c34f18275bbf23bb716bc7"

    CONTRACT_ADDRESS = st.sidebar.text_input("Contract Address", USERS_input, key="2")
    # USERS = "C\n" + USERS #Adds C as a dummy, first item
    # USERS = USERS.split('\n')

    runbtn = st.sidebar.button('Run')
    if runbtn:
        st.write('Running')
    else:
        st.write('Please click the Run button to start downloading data')
    st.header('Input Contract Address')
    CONTRACT_ADDRESS
    # USERS[1:] # Skips the dummy first item
    print(APIKEYSTR)

    # col2, col3 = st.columns(2)
    st.markdown("## Download CSV")
    if  len(APIKEYSTR) and runbtn:
        lines_to_save_data = 5000
        limit = 50

        dt_start_time = pd.to_datetime(start_date)
        dt_end_time = pd.to_datetime(end_date)

            
        dt_time = [dt_start_time, dt_end_time]

        for i in range(len(dt_time)-1):
            files = API_request_Opensea(limit, dt_time[-1-i], dt_time[-2-i], lines_to_save_data, APIKEYSTR, CONTRACT_ADDRESS)

        st.markdown(files, unsafe_allow_html=True)   
    
################
# for option: Upload & Analysize NFTs
if option == 'Data Analysis':
    sand = None
    cryptoOptions = st.sidebar.multiselect(
     'What crypto curriences do you want to show in the graph?',
     ['ETH', 'SAND', 'MANA'],['ETH', 'SAND', 'MANA'])

    if 'SAND' in cryptoOptions:
        print("SAND is active")
        sand=pd.read_csv("data/crypto data 2021-11-06 to 2022-11-07/SAND_USD Binance Historical Data.csv")
        sand['Date'] = pd.to_datetime(sand['Date'], format='%b %d, %Y')
        sand['Date'] = sand['Date'].dt.strftime('%Y-%m-%d')
    
    if 'MANA' in cryptoOptions:
        print("MANA is active")
        mana=pd.read_csv("data/crypto data 2021-11-06 to 2022-11-07/MANA_USD OKEx Historical Data.csv")
        mana['Date'] = pd.to_datetime(mana['Date'], format='%b %d, %Y')
        mana['Date'] = mana['Date'].dt.strftime('%Y-%m-%d')

    if 'ETH' in cryptoOptions:
        print("ETH is active")
        eth=pd.read_csv("data/crypto data 2021-11-06 to 2022-11-07/Ethereum Historical Data - Investing.com.csv")
        eth['Date'] = pd.to_datetime(eth['Date'], format='%b %d, %Y')
        eth['Date'] = eth['Date'].dt.strftime('%Y-%m-%d')

    downloadcsv = st.sidebar.checkbox('Download adjusted csv files (MAX file size: 200MB)')
    upload_your_own_csv = st.sidebar.checkbox('Upload you own CSV files ')
    if upload_your_own_csv:
        uploaded_file = st.sidebar.file_uploader("Decentraland Data", key=1)
        uploaded_file2 = st.sidebar.file_uploader("Sandbox Data", key=2)
    else:
        uploaded_file = "data/nft data 2021-11-06 to 2022-11-07/Decentraland_NFT_OpenSea_11_2021.csv"
        uploaded_file2 = "data/nft data 2021-11-06 to 2022-11-07/SandBox_NFT_OpenSea_11_2021.csv"
    data1, data2 = None,None
    df_created_quantity, df_created_quantity2 = None, None
    df_created_totalPrice, df_created_totalPrice2 = None, None
    if uploaded_file is not None:
        #read csv
        data1=pd.read_csv(uploaded_file)
        asset = data1['payment_token']
        payment_token_list = []
        token_unit = []
        for row in data1['payment_token']:
            payment_token_list.append(ast.literal_eval(row)['symbol'])
            token_unit.append(ast.literal_eval(row)['decimals'])

        data1.insert(18, "payment_token_type", payment_token_list, True)
        data1.insert(19, "token_unit", token_unit, True)
     
        # st.dataframe(data1) 
        # convert 'created_date' to yyyy-mm-dd
        data1['created_date'] = pd.to_datetime(data1['created_date'], format='%Y-%m-%d')
        data1['created_date'] = data1['created_date'].dt.strftime('%Y-%m-%d')
        if 'SAND' not in cryptoOptions:
            st.markdown("## File 1")
            st.dataframe(data1.head(5))
        df_created_quantity = data1[['created_date', 'quantity']]
        df_created_totalPrice = data1[['created_date', 'total_price']]

    if uploaded_file2 is not None:
        #read csv
        data2=pd.read_csv(uploaded_file2)
        asset2 = data2['payment_token']
        payment_token_list2 = []
        token_unit2 = []
        for row in data2['payment_token']:
            payment_token_list2.append(ast.literal_eval(row)['symbol'])
            token_unit2.append(ast.literal_eval(row)['decimals'])

        data2.insert(18, "payment_token_type", payment_token_list2, True)
        data2.insert(19, "token_unit", token_unit2, True)
        data2['created_date'] = pd.to_datetime(data2['created_date'], format='%Y-%m-%d')
        data2['created_date'] = data2['created_date'].dt.strftime('%Y-%m-%d')
        if 'MANA' not in cryptoOptions:
            st.markdown("## File 2")
            st.dataframe(data2.head(5)) 
        # for data2 the big one
        df_created_quantity2 = data2[['created_date', 'quantity']]
        df_created_totalPrice2 = data2[['created_date', 'total_price']]
        # buffer = io.StringIO()
        # df_created_totalPrice2.info(buf=buffer)
        # s = buffer.getvalue()
        # st.text(s)
    
    if uploaded_file is not None and uploaded_file2 is not None:
        print("yes")
        # df_created_quantity_sum = df_created_quantity.groupby( 'created_date').sum()
        # df_created_quantity_sum2 = df_created_quantity2.groupby( 'created_date').sum()
        # df_created_quantity_sum = df_created_quantity_sum.rename(columns={"quantity":"Decentraland"})
        # df_created_quantity_sum2 = df_created_quantity_sum2.rename(columns={"quantity":"Sandbox"})
        # result = df_created_quantity_sum.join(df_created_quantity_sum2) #join by index

        # # df_created_totalPrice = df_created_totalPrice.sort_values(by='total_price', ascending=True)
        # df_created_totalPrice = df_created_totalPrice.rename(columns={"total_price":"Decentraland"})
        # df_created_totalPrice['Decentraland'] = df_created_totalPrice['Decentraland'].astype(float).div(1000000000000000000).round(4)

        # df_created_totalPrice2 = df_created_totalPrice2.rename(columns={"total_price":"Sandbox"})
        # df_created_totalPrice2['Sandbox'] = df_created_totalPrice2['Sandbox'].astype(float).div(1000000000000000000).round(4)

        # df_created_totalPrice = df_created_totalPrice.set_index('created_date')
        # df_created_totalPrice2 = df_created_totalPrice2.set_index('created_date')
        # result2 = df_created_totalPrice.join(df_created_totalPrice2) #join by index
        
        if 'SAND' in cryptoOptions:
            # print("yes1")
            st.markdown("## Sandbox's data combined with SAND/USD")
            withsandprice = data2.join(sand.set_index('Date'), on='created_date')   
            withsandprice["usd_price"] =  withsandprice["total_price"].astype(float) / (10**withsandprice["token_unit"].astype(float))
            st.dataframe(withsandprice.head(5))
            # @st.cache(suppress_st_warning=True)
            if downloadcsv:
                st.markdown(filedownload(withsandprice), unsafe_allow_html=True)   
        
        if 'MANA' in cryptoOptions:
            st.markdown("## Decentraland's data combined with MANA/USD")
            withmanaprice = data1.join(mana.set_index('Date'), on='created_date')        
            st.dataframe(withmanaprice.head(5))
            if downloadcsv:
                st.markdown(filedownload(withmanaprice), unsafe_allow_html=True)   

        if len(cryptoOptions) < 1:
            st.markdown("## Total Sales per day")
            # st.line_chart(result)

            st.markdown("## Total Price per day")
            # st.bar_chart(result2)

        
    
       

##################### Layout Application ##################
# container1 = st.container()
# col1, col2 = st.columns(2)





# with container1:
#     with col1:
#         # scatter_fig
#     with col2:
#         # bar_fig


# container2 = st.container()
# col3, col4 = st.columns(2)

# with container2:
#     with col3:
#         # hist_fig
#     with col4:
#         # hexbin_fig
