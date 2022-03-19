# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Start

# %%
import pandas as pd
import numpy as np
from datetime import datetime

# %%
purchase_data = pd.read_excel("./Analyst_dataset.xlsx", sheet_name='Purchase Exit Survey Data')
airings_data = pd.read_excel("./Analyst_dataset.xlsx", sheet_name='Airings')
lookup_data = pd.read_excel("./Analyst_dataset.xlsx", sheet_name='Lookup', skiprows=1)

# %% [markdown]
# # Preprocessing

# %%
lookup_data.shape

# %%
lookup_data = lookup_data.dropna(how='all')

# %%
lookup_data.shape

# %%
lookup_data['Exit Survey'] = lookup_data['Exit Survey'].str.lower()
lookup_data['Airings'] = lookup_data['Airings'].str.upper()

# %%
airings_data['Network'] = airings_data['Network'].str.upper()

# %% [markdown]
# # Transposing Purchase Exit Survey Data - Converting dates from columns to rows in Purchase Exit Survey Data

# %%
current_year = purchase_data.iloc[0,:].dropna()
current_year = int(current_year)
current_year

# %%
months = []
for month in purchase_data.iloc[2,2:].dropna():
    months.append(month)
months

# %%
# current_month = months[0]
# i = 0
# for count, day in enumerate(day_nums, start=1):
#     if str(day) > str(purchase_data.iloc[3, 2+count]):
#         i += 1
#         current_month = month[i]
#         current_date = str(current_year) + '-' + current_month + '-' + str(day)
#         print(current_date)
#         #print(count)
#     else:
#         current_date = str(current_year) + '-' + current_month + '-' + str(day)
#         print(current_date)
#         #print(count)

day_nums = np.array(purchase_data.iloc[3,2:], dtype=int)

parsed_dates = []
current_month = months[0]
i = 0
for count, today in enumerate(day_nums, start=1):
    try:
        tomorrow = day_nums[count]
    except:
        pass
        # current_date = str(current_year) + '-' + current_month + '-' + str(today)
        # current_date = datetime.strptime(current_date, '%Y-%B-%d').date()
        # parsed_dates.append(current_date)
        #print(type(current_date))
    if today > tomorrow:
        current_date = str(current_year) + '-' + current_month + '-' + str(today)
        current_date = datetime.strptime(current_date, '%Y-%B-%d').date()
        i += 1
        current_month = months[i]
        parsed_dates.append(current_date)
        #print(current_date)
        #print(count)
    else:
        current_date = str(current_year) + '-' + current_month + '-' + str(today)
        current_date = datetime.strptime(current_date, '%Y-%B-%d').date()
        #print(current_date)
        parsed_dates.append(current_date)
        #print(count)

# %%
purchase_data.iloc[3,2:] = parsed_dates

# %%
purchase_data_transpose = purchase_data.iloc[3:,:].transpose()
#new_df.head()

# %%
purchase_data_transpose.index = purchase_data_transpose.iloc[:, 0]

# %%
purchase_data_transpose = purchase_data_transpose.iloc[1:]

# %%
purchase_data_transpose = purchase_data_transpose.drop(labels=3, axis=1)

# %%
purchase_data_transpose.columns = purchase_data_transpose.iloc[0]

# %%
purchase_data_transpose = purchase_data_transpose.drop(labels='Source')

# %%
purchase_data_transpose.index = pd.to_datetime(purchase_data_transpose.index)

# %%
purchase_data_transpose.rename_axis('date', inplace=True)
#purchase_data_transpose

# %%
purchase_data_transpose.shape

# %% [markdown]
# # Overall metrics by Network

# %% [markdown]
# ## Sum of Purchases by Network

# %%
sum_of_purchases = purchase_data_transpose.sum(axis=0)
sum_of_purchases = sum_of_purchases.to_frame()
sum_of_purchases = sum_of_purchases.rename(columns={0:'Purchases'})
sum_of_purchases.index = sum_of_purchases.index.str.lower()

# %%
sum_of_purchases.shape

# %% [markdown]
# ## Joining Purchases to Lookup Data

# %%
lookup_data.info()

# %%
overall_tbl = lookup_data.merge(right=sum_of_purchases, left_on='Exit Survey', right_on='Source', how='left')
overall_tbl.drop(labels='Exit Survey.1', axis=1, inplace=True)
#overall_tbl.rename(columns={0:'Purchases'}, inplace=True)
overall_tbl.set_index('Exit Survey', inplace=True)
overall_tbl.shape

# %% [markdown]
# ## Spend and Lift by Network

# %%
airings_spend_and_lift = airings_data.groupby('Network')[['Spend', 'Lift']].agg('sum')
airings_spend_and_lift.shape

# %% [markdown]
# ## Joining Purchases/Lookup to Spend and Lift

# %%
overall_tbl = overall_tbl.merge(right=airings_spend_and_lift,left_on='Airings', right_index=True, how='left')
overall_tbl.shape

# %% [markdown]
# ## Computing Metrics by Network

# %%
overall_tbl['Conversion Rate'] = overall_tbl['Purchases'] / overall_tbl['Lift'] * 100
overall_tbl['Cost Per Acquisition'] = overall_tbl['Spend'] / overall_tbl['Purchases']
overall_tbl['Cost Per Visitor'] = overall_tbl['Spend'] / overall_tbl['Lift']
overall_tbl['Percent of Purchases'] = overall_tbl['Purchases'] / sum(overall_tbl['Purchases'].fillna(0)) * 100
overall_tbl['Percent of Spend'] = overall_tbl['Spend'] / sum(overall_tbl['Spend'].fillna(0)) * 100
overall_tbl['Percent Pur > Percent Spend'] = overall_tbl['Percent of Purchases'] > overall_tbl['Percent of Spend']
overall_tbl

# %%
overall_tbl.shape

# %% [markdown]
# ## Done

# %% [markdown]
# # Grouped Metrics by Network and Month

# %% [markdown]
# ## Purchase Data by Network and Month

# %%
purchase_data_by_month = purchase_data_transpose.groupby(pd.Grouper(freq='M')).agg('sum')
purchase_data_by_month

# %%
purchase_data_by_month = purchase_data_by_month.transpose()
purchase_data_by_month = purchase_data_by_month.stack().to_frame()
purchase_data_by_month.rename(columns={0:'Purchases'}, inplace=True)
purchase_data_by_month = purchase_data_by_month.reset_index()
purchase_data_by_month['Source'] = purchase_data_by_month['Source'].str.lower()
purchase_data_by_month

# %%
purchase_data_by_month.shape

# %% [markdown]
# ## Airings Sheet

# %%
airings_data.info()

# %%
# airings_data.groupby([pd.Grouper(key='Date/Time ET', freq='M'), 'Network'])[['Spend', 'Lift']].agg('sum')

# %% [markdown]
# ## Preparing Lookup Data for Join

# %%
lookup_data = lookup_data.drop('Exit Survey.1', axis=1)
# lookup_data = lookup_data.set_index('Exit Survey')
# lookup_data = lookup_data.rename_axis('Source')
lookup_data

# %%
lookup_data.shape

# %% [markdown]
# ## Joining Purchases by network and month to Lookup Data

# %%
# joined_tbl = lookup_data[['Exit Survey', 'Airings']].merge(right=purchase_data_by_date, left_on='Exit Survey', right_on='Source', how='left')
# #joined_tbl.drop(labels='Exit Survey', axis=1, inplace=True)
# joined_tbl

# %%
# purchase_grouped = purchase_data_by_month.join(lookup_data, how='right')
# purchase_grouped

# %%
by_month_tbl = lookup_data.merge(right=purchase_data_by_month, left_on='Exit Survey', right_on='Source', how='left').set_index(['Exit Survey', 'date'])
by_month_tbl

# %%
print(by_month_tbl.to_string())

# %%
by_month_tbl.shape

# %% [markdown]
# ## Spend and Lift by Network and Month

# %%
# NEED TO drop Network as an index and make a column, join with purchase_grouped and keep the 
airings_spend_lift_grouped = airings_data.groupby(['Network', pd.Grouper(key='Date/Time ET', freq='M')])[['Spend', 'Lift']].agg('sum')
airings_spend_lift_grouped

# %%
# airings_spend_lift_grouped.reset_index()

# %%
by_month_tbl.reset_index().head()

# %%
# purchase_grouped.reset_index()

# %%
airings_spend_lift_grouped.reset_index().head()

# %% [markdown]
# ## Joining Purchases/Lookup to Spend and Lift by Network and Month

# %%
# month_and_network_grouped = purchase_grouped.reset_index().merge(right=airings_spend_lift_grouped.reset_index(), left_on=['Airings', 'date'], right_on=['Network', 'Date/Time ET'], how='left')
# month_and_network_grouped

new_tbl = by_month_tbl.reset_index().merge(right=airings_spend_lift_grouped.reset_index(), left_on=['Airings', 'date'], right_on=['Network', 'Date/Time ET'], how='left')
new_tbl.head()

# %%
new_tbl.shape

# %%
# month_and_network_grouped= month_and_network_grouped.set_index(['Source', 'date']).drop(labels=['Airings', 'Network', 'Date/Time ET'], axis=1)
# month_and_network_grouped

new_tbl = new_tbl.set_index(['Exit Survey', 'date']).drop(labels=['Airings', 'Network', 'Date/Time ET', 'Source'], axis=1)
new_tbl

# %%
new_tbl.shape

# %%
print(new_tbl.to_string())

# %%
new_tbl['Conversion Rate'] = new_tbl['Purchases'] / new_tbl['Lift'] * 100
new_tbl['Cost Per Acquisition'] = new_tbl['Spend'] / new_tbl['Purchases']
new_tbl['Cost Per Visitor'] = new_tbl['Spend'] / new_tbl['Lift']
new_tbl['Percent of Purchases'] = new_tbl['Purchases'] / sum(new_tbl['Purchases'].fillna(0)) * 100
new_tbl['Percent of Spend'] = new_tbl['Spend'] / sum(new_tbl['Spend'].fillna(0)) * 100
new_tbl['Percent Pur > Percent Spend'] = new_tbl['Percent of Purchases'] > new_tbl['Percent of Spend']
new_tbl

# %%
print(new_tbl.to_string())

# %% [markdown]
# ## Done

# %%
airings_data.query('Network == "FOOD"')

# %%

# %% [markdown]
# # What networks have purchases but no spend?

# %%
airings_data.query('Spend == 0')['Network'].value_counts()

# %%
airings_data.groupby('Network')[['Spend', 'Lift']].agg('sum')

# %%
