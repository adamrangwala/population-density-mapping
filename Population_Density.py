#######################
# Import libraries
import geemap.foliumap as geemap
import ee   #mapping
import streamlit as st
import datetime
from dateutil.relativedelta import relativedelta
import Settings
from Settings import STYLES
from Utils import GeoCodingError, get_aoi

#######################
# Page Configuration
st.set_page_config(
    page_title="Make You own Heatmaps",   
    layout="centered", 
    page_icon="https://user-images.githubusercontent.com/351125/62718454-384c9f00-b9dc-11e9-8f1d-377fea19b6dd.png", 
    initial_sidebar_state="expanded",
)

#######################
# Sidebar
with st.sidebar:
    st.title('🏂 Configuration')

    address = st.text_input(
        "Location",
        key="address",
        value = "Chicago, IL"
    )

    # Select year for population density
    year = st.slider(
        label='Select Year',
        min_value=datetime.date.today().year - 25,
        max_value=datetime.date.today().year - 5,
        value=datetime.date.today().year-5,
        key='year'
    )
            
    # Select map color theme
    style = st.selectbox(
        "Map Color Theme",
        options=list(STYLES.keys()),    
        key="style",
    )

    st.write("")

    max = st.slider("Select maximum density [population per pixel]",
            min_value=0.0,
            max_value=40.0,
            value=20.0,
            step=.5
            )
    
    legend = st.toggle("Legend Visibility", value=True)

#######################
# Print page header
st.markdown("# Make a Population Density Map")

# About text section
st.markdown("""

The maps created with this application use the [WorldPop dataset](https://www.worldpop.org/).
Specifically, estimates of population are calculated for each pixel: where 1 pixel represents a real world area of 100x100m.
""", unsafe_allow_html=True)

#######################
# Loading icon
with st.spinner("Creating map... (may take up to a minute)"):
    try:
        # Load City Boundaries
        aoi = get_aoi(address=address)
    except GeoCodingError as e:
        st.error(f"Error: {str(e)}")
        st.stop()

#######################
# Map Configuration

# Convert Shapely aoi object to ee geometry
points = ee.Geometry.MultiPoint(list(aoi.exterior.coords)) 

aoi_ee = ee.Geometry.Polygon(list(aoi.exterior.coords))
buffered_aoi_ee = aoi_ee.buffer(10000)   #10km buffer

# Load Landsat 8 imagery
population = (
    ee.ImageCollection("WorldPop/GP/100m/pop")
    .filterDate(f"{year}-01-01", f"{year}-12-31")
    .filterBounds(buffered_aoi_ee)
)

# Format for streamlit
m = geemap.Map()

# Add Heat Map layer
m.addLayer(population, {"min":0, "max": max, "palette": STYLES[style]}, "Population Heat Map")
m.centerObject(buffered_aoi_ee)

# Define a legend dictionary
if legend:
    legend_dict = {
    "Low Population": STYLES[style][0],
    "Medium Population": STYLES[style][int(len(STYLES[style])/2)],
    "High Population": STYLES[style][-1],
    }
    # Add legend to the map
    m.add_legend(title="Population Density", legend_dict=legend_dict)
    m.to_streamlit(height=500)

#######################
# Map Description
st.markdown("""
Besides creating an artful representation of cities, population density maps have many practical use cases.
                                                       
:building_construction: **Urban Planning**: Identifying areas to plan for housing development, public transportation routes, and public service distribution.<br />
:briefcase: **Market analysis**: Identifying areas with high potential customer bases for businesses.<br />
:syringe: **Disease Control**: Identifying areas to target disease prevention efforts.<br />
:house_buildings: **Real Estate**: Identifying areas with growing population density for property valuation.<br />

For higher-level population density maps, websites like the [2020 Census Demographic Data Map Viewer](https://maps.geo.census.gov/ddmv/map.html) might be a better alternative for showing county-level densities.
                             
Your feedback is valuable! If you encounter any issues, have suggestions for improvements, or would like to contribute to this project, please post an issue in the [project repository](https://github.com/adamrangwala).

""", unsafe_allow_html=True)
