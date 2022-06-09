import streamlit as st
import pandas as pd
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import folium
from streamlit_folium import folium_static
from folium.plugins import Fullscreen
from PIL import Image



token = 'pk.eyJ1Ijoia3Jva3JvYiIsImEiOiJja2YzcmcyNDkwNXVpMnRtZGwxb2MzNWtvIn0.69leM_6Roh26Ju7Lqb2pwQ'  # your mapbox token
tileurl = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}@2x.png?access_token=' + str(token)

#User input
#don't forget to mention in description for users that it will take the highest level of admin levels
st.sidebar.text('''Hello, welcome to poverty mapper.
Please enter the street or city or 
province or country that you would 
like poverty to be mapped on. 
We recommend to be as precise 
as possible. 
The radius is adjustable in meters.''')
st.sidebar.image("scale.png", use_column_width=True)
city = st.sidebar.text_input("City")
province = st.sidebar.text_input("Province")
country = st.sidebar.text_input("Country")
radius = st.sidebar.text_input ("Radius (in meters)")

# geolocator
geolocator = Nominatim(user_agent="GTA Lookup")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
location = geolocator.geocode(city+", "+province+", "+country)
#in the case there is no input from user, to avoid error we added a conditional
if location is not None:
    lat = location.latitude
    lon = location.longitude

#introducing folium
    m = folium.Map(location=[lat,lon],
                zoom_start=10,
                tiles=tileurl,
                attr='Mapbox',
                    control_scale=False)
    Fullscreen().add_to(m)

    pi = 0.5

    if pi <=0.2:
        col = 'lightyellow'
    elif pi <= 0.4:
        col = 'gold'
    elif pi <= 0.6:
        col = 'coral'
    elif pi <= 0.8:
        col = 'orangered'
    elif pi <= 1.0:
        col = 'firebrick'
    
 
 #adding folium marker   
    folium.Circle(
    radius=f"{radius}",
    location=[lat, lon],
    popup= f"poverty index ={pi}",
    color=f"{col}",
    fill=True,).add_to(m)
    folium_static(m)

