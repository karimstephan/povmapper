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
radius_ = st.sidebar.text_input ("Radius (in km)")
city = st.sidebar.text_input("City")
province = st.sidebar.text_input("Province")
country = st.sidebar.text_input("Country")


#poverty index input
pi = 0.5

# geolocator
geolocator = Nominatim(user_agent="GTA Lookup")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
location = geolocator.geocode(city+", "+province+", "+country)

#in the case there is no input from user, to avoid error we added a conditional
if location is not None:
    lat = location.latitude
    lon = location.longitude


#Population count

    pop_image_collection= ee.ImageCollection("CIESIN/GPWv411/GPW_Population_Count")
    #scale remains constant
    scale = 1000
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
    df = df.loc[df['time'] == 1577836800000]

  #variables to input in interactive map  
    population_count= int(df['population_count'].sum())
    pop_pov_line = int(population_count*pi)
    if radius is not None:
         st.text(f'Radius: {radius_} km')

#folium map on streamlit
    m = folium.Map(location=[lat,lon],
                zoom_start=10,
                tiles=tileurl,
                attr='Mapbox',
                    control_scale=False)
    Fullscreen().add_to(m)


# colors for different pi levels
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
    radius=(int(f"{radius_}") * 1000),
    location=[lat, lon],
    popup=f'''poverty index ={pi}
    Total population(2020): {population_count}
    Population living below the poverty line: {pop_pov_line}''',
    color=f"{col}",
    fill=True,).add_to(m)
    folium_static(m)

