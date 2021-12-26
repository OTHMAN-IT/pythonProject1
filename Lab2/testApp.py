# requests: make HTTP requests
# Beautiful: library for parsing HTML and XML documents; in order to extract data.
# Pandas: library for data manipulation.
import os
import  requests
import csv
from  bs4 import BeautifulSoup
from datetime import datetime
import  pandas as pd
import pymongo
page=requests.get('https://www.worldometers.info/coronavirus/')
soup=BeautifulSoup(page.content,'html.parser')
soup = BeautifulSoup(page.content, 'html.parser')

table = soup.find("table", id="main_table_countries_today")
get_table_data = table.tbody.find_all("tr")

dic = {}

for i in range(len(get_table_data)):
    try:
        key = get_table_data[i].find_all("a", href=True)[0].string
    except:
        key = get_table_data[i].find_all("td")[0].string

    values = [j.string for j in get_table_data[i].find_all('td')]

    dic[key] = values

column_names = [
    "num", "Countries",
    "Total Cases", "New Cases", "Total Deaths", "New Deaths",
    "Total Recovered", "New Recovered", "Active Cases", "Serious Critical",
    "Tot Cases/1M Pop", "Tot Deaths/1M Pop"
]

df = pd.DataFrame(dic).iloc[:, :].T.iloc[1:, :12]

df.index_name = "Country"

df.columns = column_names

df.drop('num', inplace=True, axis=1)



