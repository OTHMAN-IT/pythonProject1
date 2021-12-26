import folium
from flask import Flask, render_template, request
lat = 33.584324142602426
long = -7.6423763
map = folium.Map(location=[lat, long],zoom_start=3)
folium.Circle(
        location=[lat, long],
        radius=50,
        fill=True,
        opacity=0.8,
    ).add_to(map)
map.save("templates/map.html")
app = Flask(__name__)
@app.route("/")
def hello_world():
    return render_template("map.html")
app.run()