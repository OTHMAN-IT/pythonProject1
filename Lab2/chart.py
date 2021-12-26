# requests: make HTTP requests
# Beautiful: library for parsing HTML and XML documents; in order to extract data.
# Pandas: library for data manipulation.
import os
import requests
import csv
from  bs4 import BeautifulSoup
from datetime import datetime
import  pandas as pd
import pymongo
import numpy as np
import folium
from geopy.geocoders import Nominatim
from flask import Flask, render_template, request
import matplotlib.pyplot as plt

client=pymongo.MongoClient("mongodb+srv://covidUser:covid19@sandbox.igqok.mongodb.net/test")

##Pour Stats {Cases Deaths Recovered}##
database = client.get_database("covid19DB")
collection = database.get_collection("chatBot")
collection2 = database.get_collection("byCountry")

page=requests.get('https://www.worldometers.info/coronavirus/')
soup=BeautifulSoup(page.content,'html.parser')

## Global Data
cas=soup.find_all("div", id='maincounter-wrap')
for w in cas:
   cases = cas[0].find("span").text.replace(" ","").replace(",", "")
   deaths = cas[1].find("span").text.replace(" ","")
   recoveries = cas[2].find("span").text.replace(" ","")
print("Number of cases: {}; deaths: {}; and recoveries: {}.".format(cases, deaths, recoveries))

## Table
table = soup.find("table",id="main_table_countries_today")
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
df = df.fillna("0")

########################################################
dfhead = df.head()
dfhead = dfhead.iloc[:,:6]
dfhead['Total Cases'] = dfhead['Total Cases'].str.replace(',', '').astype(int)
dfhead['Total Deaths'] = dfhead['Total Deaths'].str.replace(',', '').astype(int)
dfhead['Total Recovered'] = dfhead['Total Recovered'].str.replace(',', '').astype(int)
########################################################

df['Total Cases'] = df['Total Cases'].str.replace(',', '').astype(int)
result = df.to_html()

#########################################################################
dfMap = df[["Countries","Total Cases"]]

#########################################################################

covid_in=pd.DataFrame(
    {
        'cases':cases,
        'deaths':deaths,
        'recoveries': recoveries,
    }, index=[0]
)

##Data Covid Global
data = covid_in.to_dict(orient="records")
collection.insert_many(data)

##Data Covid Global
data2 = df.to_dict(orient="records")
collection2.insert_many(data2)

########################CASES#########################"
dfM = dfMap.head()
ax = dfM.plot.bar(x='Countries', y='Total Cases', rot=0)
plt.savefig('plotCases.jpg')

########################DEATHS#########################"
ax = dfhead.plot.line(x='Countries', y='Total Deaths', rot=0, subplots=True)

########################RECOVERED#########################"
ax = dfhead.plot.pie(x='Countries', y='Total Recovered', rot=0)

########################ROW###############################"

app = Flask(__name__)

@app.route("/")
def run():
    return render_template("bot.html", data=data, result=result, ax=ax)
app.run()