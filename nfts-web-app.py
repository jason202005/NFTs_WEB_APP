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
import json

################
# About this Web APP

# image = Image.open('app/download.jpeg')

# st.set_page_config(layout="wide")
# st.image(image, use_column_width=True)

st.write("""
# Metaverse Web App

This app predicts the **Pricing**  of molecules!

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
                return filedownload(df, str(time_start.month), str(time_start.year))
                # df.to_csv(data_folder+'NFT_OpenSea_'+str(time_start.month)+'_'+str(time_start.year)+'.csv.gz',
                #             index=False)
        time.sleep(1)
    
    if len(df)>0:
        # df.to_csv(data_folder+'NFT_OpenSea_'+str(time_start.month)+'_'+str(time_start.year)+'.csv.gz', index=False)
        return filedownload(df, str(time_start.month), str(time_start.year))
    else:
        print('No data in this month')
        

def filedownload(df, startm, starty):
    csv = df.to_csv('NFT_OpenSea_'+startm+'_'+starty+'.csv.gz',
                            index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="crypto.csv">Download CSV File</a>'
    return href
        

################
# Layout (sidebar)
st.sidebar.header('User Input Features')
start_date = st.sidebar.date_input(
     "From",
     datetime.date(2022, 4, 1), key="1")
end_date = st.sidebar.date_input(
     "To",
     datetime.date(2022, 4, 6), key="2")


st.sidebar.header('User Input Features')
USERS_input1 = ""
APIKEYSTR = st.sidebar.text_input("OPENSEA API input", USERS_input1, key="1")

st.sidebar.header('User Input Features')

## Read USERS input
USERS_input = "0x7bd29408f11d2bfc23c34f18275bbf23bb716bc7"

CONTRACT_ADDRESS = st.sidebar.text_input("Contract Address", USERS_input, key="2")
# USERS = "C\n" + USERS #Adds C as a dummy, first item
# USERS = USERS.split('\n')

st.header('Input Contract Address')
CONTRACT_ADDRESS
# USERS[1:] # Skips the dummy first item
print(APIKEYSTR)

col2, col3 = st.columns(2)
col2.header("Download CSV")

####################
#layout (column 1 and 2)
if len(APIKEYSTR):

    lines_to_save_data = 5000
    limit = 50

    dt_start_time = pd.to_datetime(start_date)
    dt_end_time = pd.to_datetime(end_date)
   
        
    dt_time = [dt_start_time, dt_end_time]

    for i in range(len(dt_time)-1):
        files = API_request_Opensea(limit, dt_time[-1-i], dt_time[-2-i], lines_to_save_data, APIKEYSTR, CONTRACT_ADDRESS)

    col2.markdown(files, unsafe_allow_html=True)    