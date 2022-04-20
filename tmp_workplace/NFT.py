#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# read csv file and store in dataframe
data1 = pd.read_csv('DNFT.csv')
data2 = pd.read_csv('NFT_Opensea.csv')


# In[4]:


data1.head()


# In[41]:


data1.info()


# In[44]:


data1.columns


# In[5]:


# convert 'created_date' to yyyy-mm-dd
data1['created_date'] = pd.to_datetime(data1['created_date'], format='%Y-%m-%d')
data1['created_date'] = data1['created_date'].dt.strftime('%Y-%m-%d')
data1


# In[6]:


# convert 'created_date' to yyyy-mm-dd
data2['created_date'] = pd.to_datetime(
    data2['created_date'], format='%Y-%m-%d')
data2['created_date'] = data2['created_date'].dt.strftime('%Y-%m-%d')
data2


# In[7]:


df_created_quantity = data1[['created_date', 'quantity']]
df_created_totalPrice = data1[['created_date', 'total_price']]

# for data2 the big one

df_created_quantity2 = data2[['created_date', 'quantity']]
df_created_totalPrice2 = data2[['created_date', 'total_price']]


# In[8]:


df_created_totalPrice2.info()


# # Total Sales per day

# In[9]:


# # plot the quantity for each day for both data with barchart side by side and expand the size of plot to maximum width
# ax = df_created_quantity_sum.plot(
#     kind='bar', figsize=(20, 10), legend=True, fontsize=12)
# ax2 = df_created_quantity_sum2.plot(
#     kind='bar', figsize=(20, 10), legend=True, fontsize=12)
# # df_created_quantity_sum.plot(kind='bar', color='blue', figsize=(50, 10))
# # df_created_quantity_sum2.plot(kind='bar', color='red', figsize=(50, 10))
# plt.plot(df_created_quantity_sum)
# plt.plot(df_created_quantity_sum2)
# plt.legend(['Blue', 'Red'])
# plt.show()


# ## Line plot

# In[10]:


# group by created_date and sum up the quantity
df_created_quantity_sum = df_created_quantity.groupby( 'created_date').sum()
df_created_quantity_sum2 = df_created_quantity2.groupby( 'created_date').sum()


ax = df_created_quantity_sum.plot(figsize=(50, 10),rot=90, legend=True, fontsize=12)

df_created_quantity_sum2.plot(ax=ax,figsize=(50, 10), rot=90, legend=True, fontsize=12)


# In[11]:


df_created_totalPrice.describe()


# In[12]:


# show the item in total_price which has minimum string length
df_created_totalPrice.sort_values(by='total_price', ascending=True)


# In[ ]:





# In[13]:


df_created_totalPrice['total_price'] = df_created_totalPrice['total_price'].astype(
    str).astype('float64') / 10.**18
df_created_totalPrice2['total_price'] = df_created_totalPrice2['total_price'].astype(
    str).astype('float64') / 10.**18


# In[14]:


df_created_totalPrice


# ## Bar chart

# In[18]:


def addlabels(x, y):
    for i in range(len(x)):
        plt.text(i, y[i], y[i], ha='center', va='bottom', fontsize=80, rotation=90)
X = df_created_quantity_sum.index
DNFT =  df_created_quantity_sum['quantity']

NFT = df_created_quantity_sum2['quantity']
# print(NFT.shape())
print()

X_axis = np.arange(len(X))

plt.bar(X_axis - 0.2, DNFT, 0.4, label='DNFT')
addlabels(X, DNFT.values)
plt.bar(X_axis + 0.2, NFT, 0.4, label='NFT')
addlabels(X, NFT.values)
plt.xticks(X_axis, X, rotation=90, fontsize=150)
# increase the font size of the x-axis label
plt.xlabel("Date", fontsize=200)
plt.ylabel("total quantity", fontsize=200)
plt.title("Total quantity of NFT and DNFT",  fontsize=200)
plt.legend(loc='upper center', prop = {'size':200})
# increase the size of the plot
plt.rcParams['figure.figsize'] = [500, 50]
plt.show()


# # Total Price per day

# In[19]:





# group by created_date and sum up the total_price
df_created_totalPrice_sum = df_created_totalPrice.groupby( 'created_date').sum()
df_created_totalPrice_sum2 = df_created_totalPrice2.groupby( 'created_date').sum()
# plot the total_price for each day for both data
ax = df_created_totalPrice_sum.plot(
    figsize=(50, 10), rot=90, legend=True, fontsize=12)

df_created_totalPrice_sum2.plot(ax=ax, figsize=(
    50, 10), rot=90, legend=True, fontsize=12)


# In[33]:


def addlabels(x, y):
    for i in range(len(x)):
        plt.text(i, y[i], y[i], ha='left',
                 va='bottom', fontsize=30, rotation=90)


def addlabels1(x, y):
    for i in range(len(x)):
        plt.text(i, y[i], y[i], ha='right',
                 va='bottom', fontsize=30, rotation=90)

X = df_created_totalPrice_sum.index
DNFT = df_created_totalPrice_sum['total_price']
# round off DNFT to 0 decimal places
DNFT = np.around(DNFT, decimals=0)

NFT = df_created_totalPrice_sum2['total_price']
# round off NFT to 0 decimal places
NFT = np.around(NFT, decimals=0)
# print(NFT.shape())

X_axis = np.arange(len(X))

plt.bar(X_axis - 0.2, DNFT, 0.4, label='DNFT')
addlabels(X, NFT.values)
plt.bar(X_axis + 0.2, NFT, 0.4, label='NFT')
addlabels1(X, DNFT.values)
plt.xticks(X_axis, X, rotation=90, fontsize=150)
# increase the font size of the x-axis label
plt.xlabel("Date", fontsize=200)
plt.ylabel("total price", fontsize=200)
plt.title("Total price of NFT and DNFT",  fontsize=200)
plt.legend(loc='upper center', prop = {'size':200})
# increase the size of the plot
plt.rcParams['figure.figsize'] = [500, 50]
plt.show()


# # Average price per day in ETH

# In[45]:


# group by created_date and take average of the total_price
df_created_totalPrice_avg = df_created_totalPrice.groupby( 'created_date').mean()
df_created_totalPrice_avg2 = df_created_totalPrice2.groupby( 'created_date').mean()
df_created_totalPrice_avg


# ## Line Chart

# In[46]:


ax = df_created_totalPrice_avg.plot(
    figsize=(50, 10), rot=90, legend=True, fontsize=12)

df_created_totalPrice_avg2.plot(ax=ax, figsize=(
   50, 10), rot=90, legend=True, fontsize=12)


# ## Bar chart

# In[47]:


def addlabels(x, y):
    for i in range(len(x)):
        plt.text(i, y[i], y[i], ha='left',
                 va='bottom', fontsize=30, rotation=90)


def addlabels1(x, y):
    for i in range(len(x)):
        plt.text(i, y[i], y[i], ha='right',
                 va='bottom', fontsize=30, rotation=90)


X = df_created_totalPrice_avg.index
DNFT = df_created_totalPrice_avg['total_price']
# round off DNFT to 0 decimal places
DNFT = np.around(DNFT, decimals=0)

NFT = df_created_totalPrice_avg2['total_price']
# round off NFT to 0 decimal places
NFT = np.around(NFT, decimals=0)
# print(NFT.shape())

X_axis = np.arange(len(X))

plt.bar(X_axis - 0.2, DNFT, 0.4, label='DNFT')
addlabels(X, NFT.values)
plt.bar(X_axis + 0.2, NFT, 0.4, label='NFT')
addlabels1(X, DNFT.values)
plt.xticks(X_axis, X, rotation=90, fontsize=150)
# increase the font size of the x-axis label
plt.xlabel("Date", fontsize=200)
plt.ylabel("Average price", fontsize=200)
plt.title("Average price of NFT and DNFT",  fontsize=200)


# # Floor price per day in ETH

# ## Line plot

# In[48]:


df_created_totalPrice_floor = df_created_totalPrice.groupby(
    'created_date').min()
df_created_totalPrice_floor2 = df_created_totalPrice2.groupby(
    'created_date').min()
ax = df_created_totalPrice_floor.plot(
    figsize=(50, 10), rot=90, legend=True, fontsize=12)

df_created_totalPrice_floor2.plot(ax=ax, figsize=(
    50, 10), rot=90, legend=True, fontsize=12)


# ## Bar chart

# In[49]:


def addlabels(x, y):
    for i in range(len(x)):
        plt.text(i, y[i], y[i], ha='left',
                 va='bottom', fontsize=30, rotation=90)


def addlabels1(x, y):
    for i in range(len(x)):
        plt.text(i, y[i], y[i], ha='right',
                 va='bottom', fontsize=30, rotation=90)


X = df_created_totalPrice_floor.index
DNFT = df_created_totalPrice_floor['total_price']
# round off DNFT to 0 decimal places
DNFT = np.around(DNFT, decimals=0)

NFT = df_created_totalPrice_floor2['total_price']
# round off NFT to 0 decimal places
NFT = np.around(NFT, decimals=0)
# print(NFT.shape())

X_axis = np.arange(len(X))

plt.bar(X_axis - 0.2, DNFT, 0.4, label='DNFT')
addlabels(X, NFT.values)
plt.bar(X_axis + 0.2, NFT, 0.4, label='NFT')
addlabels1(X, DNFT.values)
plt.xticks(X_axis, X, rotation=90, fontsize=150)
# increase the font size of the x-axis label
plt.xlabel("Date", fontsize=200)
plt.ylabel("Floor price", fontsize=200)
plt.title("Floor price of NFT and DNFT",  fontsize=200)


# # Max Price per Day in ETH 

# ## Line chart

# In[51]:


df_created_totalPrice_max = df_created_totalPrice.groupby(
    'created_date').max()
df_created_totalPrice_max2 = df_created_totalPrice2.groupby(
    'created_date').max()
ax = df_created_totalPrice_max.plot(
    figsize=(50, 10), rot=90, legend=True, fontsize=12)

df_created_totalPrice_max2.plot(ax=ax, figsize=(
    50, 10), rot=90, legend=True, fontsize=12)


# ## Bar chart

# In[52]:


def addlabels(x, y):
    for i in range(len(x)):
        plt.text(i, y[i], y[i], ha='left',
                 va='bottom', fontsize=30, rotation=90)


def addlabels1(x, y):
    for i in range(len(x)):
        plt.text(i, y[i], y[i], ha='right',
                 va='bottom', fontsize=30, rotation=90)


X = df_created_totalPrice_max.index
DNFT = df_created_totalPrice_max['total_price']
# round off DNFT to 0 decimal places
DNFT = np.around(DNFT, decimals=0)

NFT = df_created_totalPrice_max2['total_price']
# round off NFT to 0 decimal places
NFT = np.around(NFT, decimals=0)
# print(NFT.shape())

X_axis = np.arange(len(X))

plt.bar(X_axis - 0.2, DNFT, 0.4, label='DNFT')
addlabels(X, NFT.values)
plt.bar(X_axis + 0.2, NFT, 0.4, label='NFT')
addlabels1(X, DNFT.values)
plt.xticks(X_axis, X, rotation=90, fontsize=150)
# increase the font size of the x-axis label
plt.xlabel("Date", fontsize=200)
plt.ylabel("Maximum price", fontsize=200)
plt.title("Maximum price of NFT and DNFT",  fontsize=200)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




