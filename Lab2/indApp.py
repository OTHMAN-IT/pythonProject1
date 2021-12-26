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
df['Total Cases'] = df['Total Cases'].str.replace(',', '').astype(int)
result = df.to_html()

#########################################################################
dfMap = df[["Countries","Total Cases"]]

########################################################################
geolocator = Nominatim(timeout=10, user_agent = "myGeolocator")
dfMap['gcode'] = dfMap.Countries.apply(geolocator.geocode)
dfMap['lat'] = [g.latitude for g in dfMap.gcode]
dfMap['long'] = [g.longitude for g in dfMap.gcode]
print(dfMap)
########################################################################
# Make an empty map
n = folium.Map(location=[20,0], tiles="OpenStreetMap", zoom_start=2)

# add marker one by one on the map
for i in range(0,len(dfMap)):
   folium.Circle(
      location=[dfMap.iloc[i]['lat'], dfMap.iloc[i]['long']],
       radius=float(dfMap.iloc[i]['Total Cases'])*3/100,
      popup=dfMap.iloc[i]['Total Cases'],
      icon=folium.DivIcon(html=f"""<div style="font-family: courier new; color: blue">{dfMap.iloc[i]['Total Cases']}</div>""")
   ).add_to(n)
   display_map = n._repr_html_()
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

#################################################"
ax = dfMap.plot.bar(x='Countries', y='Total Cases', rot=0)

app = Flask(__name__)

@app.route("/")
def run():
    return render_template("index.html", data=data,
                                         result=result,
                                         display_map=display_map)
app.run()