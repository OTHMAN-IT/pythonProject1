import json
import falcon
import folium
import numpy as np
import requests, pandas as pd
from bs4 import BeautifulSoup
###TEST
def covid():
 api_covid = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/11-22-2021.csv')
 getGroupCountry = api_covid.groupby('Country_Region').sum()[['Confirmed', 'Deaths']]
 data_covid = getGroupCountry.sort_values("Confirmed", ascending=False)
 return data_covid

data_covid = covid()

display_field = [(country, confirmed, deaths) for country, confirmed, deaths in zip(data_covid.index, data_covid['Confirmed'], data_covid['Deaths'])]

###########################################################################""""

api_covid = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/11-22-2021.csv')
api_covid.head()
map = folium.Map(location = [25.025885, -78.035889],
           tiles = 'OpenStreetMap',
           zoom_start = 5)
folium.Circle(
    location = [25.025885, -78.035889],
    radius = 1000,
    color = 'red',
    fill = True,
    popup = 'confirmed {}'.format(20)).add_to(map)

def circle_maker(x):
  folium.Circle(location = [x[0], x[1]],
                radius = float(x[2])*3/100,
                color='red',
                popup = '<h3><b>{}</b></h3> \n<b>Cases</b>: {}\n <b>Deaths</b>: {}'.format(x[3], x[2], x[4])).add_to(map)

api_covid[['Lat', 'Long_', 'Confirmed', 'Combined_Key', 'Deaths']].dropna(subset = ['Lat', 'Long_']).apply(lambda x: circle_maker(x), axis = 1)
###
display_map = map._repr_html_()

##########################################################################

def sum_cases():
    api_covid = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/11-19-2021.csv')
    getGroupCountry1 = api_covid.groupby('Country_Region').sum()[['Confirmed']]
    data_covid1 = getGroupCountry1.sum().tolist()
    return data_covid1


data_covid1 = sum_cases()

############################################################################

def sum_deaths():
    api_covid = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/11-22-2021.csv')
    getGroupCountry2 = api_covid.groupby('Country_Region').sum()[['Deaths']]
    data_covid2 = getGroupCountry2.sum().tolist()
    return data_covid2

data_covid2 = sum_deaths()

def top5():
    api_covid = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/11-19-2021.csv')
    getTopConf = api_covid.groupby('Country_Region').sum()[['Confirmed']]
    data_covid3 = getTopConf.nlargest(5, 'Confirmed').sort_values("Confirmed", ascending=False)
    return data_covid3

data_covid3 = top5()

display_field1 = [(country, confirmed) for country, confirmed in zip(data_covid3.index, data_covid3['Confirmed'])]

from flask import Flask, render_template, request
app = Flask(__name__)
@app.route("/")
def test():
    return render_template("index.html", data_covid = data_covid,
                                        display_map = display_map,
                                        display_field = display_field,
                                        data_covid1 = data_covid1,
                                        data_covid2 = data_covid2,
                                        data_covid3 = data_covid3,
                                        display_field1 = display_field1)

if __name__ == "__main__":

    app.run(debug=True)
