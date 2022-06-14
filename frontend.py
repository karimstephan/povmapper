import streamlit as st
import pandas as pd
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import folium
from streamlit_folium import folium_static
from folium.plugins import Fullscreen
from PIL import Image
import ee
import os
from google.oauth2 import service_account
from dotenv import load_dotenv, find_dotenv
import json
from haversine import inverse_haversine, Direction
import time
import requests


#setting up the progress bar on streamlit
my_bar = st.progress(0)

for percent_complete in range(100):
     time.sleep(0.1)
     my_bar.progress(percent_complete + 1)
my_bar.empty()

# information from le Wagon for tiles in Folium map
token = 'pk.eyJ1Ijoia3Jva3JvYiIsImEiOiJja2YzcmcyNDkwNXVpMnRtZGwxb2MzNWtvIn0.69leM_6Roh26Ju7Lqb2pwQ'  # your mapbox token
tileurl = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}@2x.png?access_token=' + str(token)

#functioning login to EE (not applicable to docker)
service_account = 'annuka@poverty-mapper.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, '/Users/annuka/Downloads/poverty-mapper-deef500638d8.json')
ee.Initialize(credentials)

#not functioning login to EE (applicable to docker):
# point to .env file
#env_path = find_dotenv() # automatic find
#CREDENTIAL_KEY = os.getenv('CREDENTIAL_KEY')
#credentials = service_account.Credentials.from_service_account_info(json.loads(CREDENTIAL_KEY))
##Initializing Google Earth Engine
#ee.Initialize(credentials))


#function with API, Population count based on gridded population
def frontend_manipulation(lat,lon, radius_):    
    
    # #API URL and poverty index input
    # url= 'https://povapi-ig6qgbx3oa-ew.a.run.app/predict?'
    # params = dict(lat=lat,lon=lon)
    # response=requests.get(url, params=params)
    # prediction= response.json()
    # pi = prediction['value']
    
    #pi placeholder
    pi=40
    
    #Population count based on lat, lon
    pop_image_collection= ee.ImageCollection("CIESIN/GPWv411/GPW_Population_Count")
    #scale remains constant
    scale = 1000
    #in the case there is no radius value entered by user, it will automatically be 1
    if radius_ == '':
        radius_=1
    #grid_size in km
    grid_size =int(f'{radius_}')
    radius=(grid_size * 2**0.5 )/2

    coord_ne = inverse_haversine((lat,lon), radius, Direction.NORTHEAST)
    coord_sw = inverse_haversine((lat,lon), radius, Direction.SOUTHWEST)

    coordinates_rectangle = ee.Geometry.Rectangle([
                                [coord_sw[1], coord_sw[0]],
                                [coord_ne[1], coord_ne[0]]
                                ])

    pop_region = pop_image_collection.select('population_count').getRegion(coordinates_rectangle, scale).getInfo()

    df = pd.DataFrame(pop_region)
    df.columns = df.iloc[0]
    df = df[1:]
    df = df.sort_values('time')
    df.reset_index(inplace=True, drop=True)
    #'1577836800000' is the value for 2020 data
    df = df.loc[df['time'] == 1577836800000]

    #variables to input in interactive map  
    population_count= int(df['population_count'].sum())
    pop_pov_line = int(population_count*(pi/100))
    
    #st.text(f'Location: {city}, {province}, {country}. lat, lon: {lat}, {lon}')
    st.text(f'Latitude: {lat}     Longitude: {lon}    Radius: {radius_} km')
    st.text(f'Poverty Index : {pi}%')
    st.text(f'Total population(2020): {population_count}')
    st.text(f'Population living below the poverty line: {pop_pov_line}')   

#folium map on streamlit
    m = folium.Map(location=[lat,lon],
                zoom_start=10,
                tiles=tileurl,
                attr='Mapbox',
                control_scale=False
                )
    Fullscreen().add_to(m)
    
# colors for different pi levels
    if pi <20:
        col = 'lightyellow'
    elif pi <40:
        col = 'gold'
    elif pi <60:
        col = 'coral'
    elif pi <80:
        col = 'orangered'
    elif pi <=100:
        col = 'firebrick'

#adding folium marker   
    folium.Circle(
    radius=(int(f"{radius_}") * 1000),
    location=[lat, lon],
    color=f"{col}",
    fill=True,).add_to(m)
    folium_static(m)


#Side bar and User input
st.sidebar.text('''Hello, welcome to Poverty Mapper.
Please enter coordinates or location name
that you would like an index of poverty 
to be calculated and mapped on. 
The radius is adjustable in 
kilometers.''')
st.title('Poverty Mapper')
st.sidebar.image("scale.png", use_column_width=True)
radius_ = st.sidebar.text_input ("Radius (in km)", 1)
user_input = st.sidebar.radio(
     "Select if you would like to enter coordinates or location",
     ('Coordinates', 'Location'))
if user_input == 'Location':
    locat = st.sidebar.text_input("Location (city and/or province and/or country)")

    # geolocator
    geolocator = Nominatim(user_agent="GTA Lookup")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    location = geolocator.geocode(locat)

    #in the case there is no input from user, to avoid error we added a conditional
    if location is not None:
        lat = location.latitude
        lon = location.longitude

        frontend_manipulation(lat,lon, radius_)

    else:
        st.text ('''Please enter a location. 
If a map does not appear, please check your spelling.''')

if user_input == 'Coordinates':
    lat = st.sidebar.number_input('Latitude')
    lon = st.sidebar.number_input('Longitude')
    
    frontend_manipulation(lat,lon, radius_)