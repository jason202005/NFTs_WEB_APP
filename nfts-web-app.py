import datetime
import numpy as np
import pandas as pd
from datetime import datetime
import streamlit as st
# import pickle
from PIL import Image
import streamlit as st
import base64
import matplotlib.pyplot as plt

from bs4 import BeautifulSoup
import requests
import time
import io
import json
import ast
from helpers.Historical_Price import Historical_Price

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

def classify_token(payment_token):
    currency = json.loads(payment_token.replace("'", '"'))['symbol']
    # decimal = 18
    if currency == 'ETH' or currency == 'WETH':
        return 'ETH'
    # decimal = 8
    elif currency == 'BTC' or currency == 'WBTC':
        return 'BTC'
    # decimal = 6
    elif currency == 'USDC':
        return 'USDC'
   # decimal = 18
    elif currency == 'MANA':
        return 'MANA'
   # decimal = 18
    elif currency == 'DAI':
        return 'DAI'
   # decimal = 18
    elif currency == 'SAND':
        return 'SAND'
    else:
        return 'Unknown'

def get_currency_price(row):
    return historical_price_engine.get_token_historical_price(row['payment_token'], row['created_date'])

def get_decimal_ratio(currency):
    if currency == 'ETH':
        return 1e18
    if currency == 'BTC':
        return 1e8
    if currency == 'USDC':
        return 1e6
    if currency == 'MANA':
        return 1e18
    if currency == 'DAI':
        return 1e18
    if currency == 'SAND':
        return 1e18
    return 1


def change_format(df):
    df['created_date'] = pd.to_datetime(df['created_date'], format='%Y-%m-%d')
    df['created_date'] = df['created_date'].dt.strftime('%Y-%m-%d')
    df['total_price'] = df['total_price'].astype(float)
    df['payment_token'] = df['payment_token'].apply(classify_token)
    df = df[df['payment_token'] != 'Unknown']
    token_unit = df['total_price'] / df['payment_token'].apply(get_decimal_ratio)
    df = df.join(pd.DataFrame({'token_unit': token_unit}))
    # usd_price = df['token_unit'] * df['payment_token'].apply(get_currency_price)
    # usd_price = df.apply(lambda x: x.token_unit * historical_price_engine.get_token_historical_price((x.payment_token, x.created_date), axis=1))
    # usd_price = df['token_unit'] * historical_price_engine.get_token_historical_price(df['payment_token'].to_numpy(), df['created_date'].to_numpy())
    usd_price = df['token_unit'] * df.apply(get_currency_price, axis = 1)
    df = df.join(pd.DataFrame({'usd_price': usd_price}))
    avg_price = df['usd_price'] / df['quantity']
    df = df.join(pd.DataFrame({'avg_price': avg_price}))
    return df

def get_df_created_quantity(df, quantity1, quantity2):
    return df[[quantity1, quantity2]]

def get_price_correlation(df1, df2):
    df_group = df1.groupby('created_date').mean()
    df_group2 = df2.groupby('created_date').mean()
    df_merged = df_group.merge(df_group2, how = 'inner', on = 'created_date')
    return df_merged['avg_price_x'].corr(df_merged['avg_price_y'])




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
        "From",key="1")
    end_date = st.sidebar.date_input(
        "To",key="2")


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
        sand=pd.read_csv("https://media.githubusercontent.com/media/jason202005/NFTs_WEB_APP/main/data/crypto%20data%202021-11-06%20to%202022-11-07/SAND_USD%20Binance%20Historical%20Data.csv")
        sand['Date'] = pd.to_datetime(sand['Date'], format='%b %d, %Y')
        sand['Date'] = sand['Date'].dt.strftime('%Y-%m-%d')
    
    if 'MANA' in cryptoOptions:
        print("MANA is active")
        mana=pd.read_csv("https://media.githubusercontent.com/media/jason202005/NFTs_WEB_APP/main/data/crypto%20data%202021-11-06%20to%202022-11-07/MANA_USD%20OKEx%20Historical%20Data.csv")
        mana['Date'] = pd.to_datetime(mana['Date'], format='%b %d, %Y')
        mana['Date'] = mana['Date'].dt.strftime('%Y-%m-%d')

    if 'ETH' in cryptoOptions:
        print("ETH is active")
        eth=pd.read_csv("https://media.githubusercontent.com/media/jason202005/NFTs_WEB_APP/main/data/crypto%20data%202021-11-06%20to%202022-11-07/Ethereum%20Historical%20Data%20-%20Investing.com.csv")
        eth['Date'] = pd.to_datetime(eth['Date'], format='%b %d, %Y')
        eth['Date'] = eth['Date'].dt.strftime('%Y-%m-%d')

    percentage_change = st.sidebar.checkbox("See the percentage change.")

    downloadcsv = st.sidebar.checkbox('Download adjusted csv files (MAX file size: 200MB)')
    upload_your_own_csv = st.sidebar.checkbox('Upload you own CSV files ')
    if upload_your_own_csv:
        uploaded_file = st.sidebar.file_uploader("Decentraland Data", key=1)
        uploaded_file2 = st.sidebar.file_uploader("Sandbox Data", key=2)
        # uploaded_file3 = st.sidebar.file_uploader("Sandbox Data", key=3)
    else:
        uploaded_file = "https://media.githubusercontent.com/media/jason202005/NFTs_WEB_APP/main/data/nft%20data%202021-11-06%20to%202022-11-07/Decentraland_NFT_OpenSea_11_2021.csv"
        uploaded_file2 = "https://media.githubusercontent.com/media/jason202005/NFTs_WEB_APP/main/data/nft%20data%202021-11-06%20to%202022-11-07/SandBox_NFT_OpenSea_11_2021.csv"
    data1, data2 = None,None
    df_created_quantity, df_created_quantity2 = None, None
    df_created_totalPrice, df_created_totalPrice2 = None, None
    
    if uploaded_file is not None and uploaded_file2 is not None:
        historical_price_engine = Historical_Price()
        #loading data
        data1=pd.read_csv(uploaded_file)
        data2=pd.read_csv(uploaded_file2)
        df_de = change_format(data1)
        df_sand = change_format(data2)
        # df_nftworld = change_format(df_nftworld)
        df_sand2 = get_df_created_quantity(df_sand, 'created_date', 'avg_price').groupby('created_date').mean()
        df_de2 = get_df_created_quantity(df_de, 'created_date', 'avg_price').groupby('created_date').mean()

        if not percentage_change:
            
            container1 = st.container()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("### Average price of sandbox")        
                if downloadcsv:
                    st.markdown(filedownload(df_sand2), unsafe_allow_html=True)   
                st.dataframe(df_sand2)
            with col2:
                st.markdown("### Average price of decentraland")    
                if downloadcsv:
                    st.markdown(filedownload(df_de2), unsafe_allow_html=True)   
                st.dataframe(df_de2)
            with col3:
                st.markdown("### Summary")   
                df_de2.insert(1, "Sandbox", df_sand2, True)
                if downloadcsv:
                    st.markdown(filedownload(df_de2), unsafe_allow_html=True)   
                df_de2.columns = ['Decentraland', 'Sandbox']
                st.dataframe(df_de2)

            # ax = df_sand2.plot(figsize=(50, 10),rot=90, legend=True, fontsize=12)
            # df_de2.plot(ax=ax, sharex=ax, figsize=(50, 10),rot=90, legend=True, fontsize=12)
            
            if 'SAND' in cryptoOptions:
                sand_price = sand[['Price', 'Date']]
                sand_price["Price"] = [float(str(i).replace(",", "")) for i in sand_price["Price"]]
                sand_price.columns = ['sand_price','Date']
                df_de2 = df_de2.join(sand_price.set_index('Date'))
            
            if 'MANA' in cryptoOptions:
                mana_price = mana[['Price', 'Date']]
                mana_price["Price"] = [float(str(i).replace(",", "")) for i in mana_price["Price"]]
                mana_price.columns = ['mana_price','Date']
                df_de2 = df_de2.join(mana_price.set_index('Date'))

            if 'ETH' in cryptoOptions:
                eth_price = eth[['Price', 'Date']]
                eth_price["Price"] = [float(str(i).replace(",", "")) for i in eth_price["Price"]]
                eth_price.columns = ['eth_price','Date']
                df_de2 = df_de2.join(eth_price.set_index('Date'))
            
                          
            st.markdown("## Avg price of decentraland and Sandbox with ETH price history")        
            st.line_chart(df_de2)

        elif bool(cryptoOptions) :
            df_sand2_change = df_sand2.pct_change()
            df_de2_change = df_de2.pct_change()
            eth_price_change = None
            result = None
            if 'SAND' in cryptoOptions:
                # st.dataframe(sand)
                sand_price_change = sand[['Date', 'Change %']]
                df_sand2_change = df_sand2_change.join(sand_price_change.set_index('Date'))
                df_sand2_change.columns = ['change_of_sandbox_nft', 'change_of_sand']
                df_sand2_change['change_of_sand'] = df_sand2_change['change_of_sand'].str.rstrip("%").astype(float)/100
                # st.dataframe(df_sand2_change)
                result = df_sand2_change
            if 'MANA' in cryptoOptions:
                # st.dataframe(eth)
                mana_price_change = mana[['Date', 'Change %']]
                df_de2_change = df_de2_change.join(mana_price_change.set_index('Date'))
                df_de2_change.columns = ['change_of_mana_nft', 'change_of_mana']
                df_de2_change['change_of_mana'] = df_de2_change['change_of_mana'].str.rstrip("%").astype(float)/100
                # st.dataframe(df_de2_change)
                result = df_de2_change
            if 'ETH' in cryptoOptions:
                # st.dataframe(eth)
                eth_price_change = eth[['Date', 'Change %']]
                eth_price_change = eth_price_change.set_index('Date')
                # st.dataframe(eth_price_change)
                eth_price_change.columns = [ 'change_of_eth']
                eth_price_change['change_of_eth'] = eth_price_change['change_of_eth'].str.rstrip("%").astype(float)/100
                # st.dataframe(df_de2_change)
                result = eth_price_change
            if 'SAND' in cryptoOptions and 'MANA' in cryptoOptions:
                result = df_sand2_change.join(df_de2_change)
            if 'SAND' in cryptoOptions and 'ETH' in cryptoOptions:
                result = eth_price_change.join(df_sand2_change)
            if 'MANA' in cryptoOptions and 'ETH' in cryptoOptions:
                result = df_de2_change.join(eth_price_change)
            if 'MANA' in cryptoOptions and 'SAND' in cryptoOptions and 'ETH' in cryptoOptions:
                result = df_de2_change.join(eth_price_change)
                result = result.join(df_sand2_change)

            st.dataframe(result)
            st.markdown("## Change of Avg price of decentraland and Sandbox ")        
            st.line_chart(result)

        if not bool(cryptoOptions) and percentage_change:
            st.markdown("## Please select crypto curriences you want to show in the graph on the left.")

    
