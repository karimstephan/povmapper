import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import folium
from streamlit_folium import folium_static
from folium.plugins import Fullscreen


token = 'pk.eyJ1Ijoia3Jva3JvYiIsImEiOiJja2YzcmcyNDkwNXVpMnRtZGwxb2MzNWtvIn0.69leM_6Roh26Ju7Lqb2pwQ'  # your mapbox token
tileurl = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}@2x.png?access_token=' + str(token)


#User input
#don't forget to mention in description for users that it will take the highest level of admin levels

street = st.sidebar.text_input("Street")
city = st.sidebar.text_input("City")
province = st.sidebar.text_input("Province")
country = st.sidebar.text_input("Country")

# geolocator
geolocator = Nominatim(user_agent="GTA Lookup")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
location = geolocator.geocode(street+", "+city+", "+province+", "+country)
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
 #adding folium marker   
    folium.Circle(
    radius=5000,
    location=[lat, lon],
    popup="poverty index =",
    color="red",
    fill=True,).add_to(m)
    folium_static(m)

