#!/usr/bin/env python3

import streamlit as st
import geopandas as gpd
import pandas as pd
import leafmap
import os
from PIL import Image

# Set wide mode
st.set_page_config(layout='wide')

# Set session state variables
if 'zoom_center_x' not in st.session_state:
    st.session_state.zoom_center_x = 33
if 'zoom_center_y' not in st.session_state:
    st.session_state.zoom_center_y = -96
if 'zoom_level' not in st.session_state:
    st.session_state.zoom_level = 4

# Main page text
st.title("USGS/FORE-SCE Land Use Change Basins, 1978-2021")


def get_centroid(gage_id_geo):
    df = gpd.read_file("./Data/Geojsons/{}.geojson".format(gage_id_geo))
    st.session_state.zoom_center_y = float(df["geometry"].centroid.x)
    st.session_state.zoom_center_x = float(df["geometry"].centroid.y) - 0.3
    st.session_state.zoom_level = 9
    return df


def show_data(gage_id):
    df2 = get_centroid(gage_id)
    main_map = leafmap.Map(center=(st.session_state.zoom_center_x, st.session_state.zoom_center_y),
                           zoom=st.session_state.zoom_level, draw_control=False, measure_control=False,
                           google_map="HYBRID")
    main_map.add_gdf(df2, layer_name=gage_id, zoom_to_layer=False, fill_colors=['blue'])
    main_map.to_streamlit(responsive=True)

    col1, col2 = st.columns(2)
    with col1:
        image = Image.open("./Data/Plots/Tab_area_ID{}_changes.png".format(gage_id))
        st.image(image, caption='Cell changes')

    with col2:
        try:
            video = open("./Data/Timelapses/{}.mp4".format(gage_id), 'rb')
            video_bytes = video.read()
            st.video(video_bytes)
        except FileNotFoundError:
            pass
    csv_df = pd.read_csv("./Data/CSVs/Tab_area_ID{}_final.csv".format(gage_id))
    st.write(csv_df)


with st.container():
    st.sidebar.title("Selecting data:")
    basin = st.sidebar.selectbox('Select a basin:', ('05123600', '02315500', '02246000', '02301990', '02310947',
                                                     '02322800', '08079600', '02296500', '02167450', '03435500',
                                                     '02110500', '08070000', '02246150', '08189500', '02300700',
                                                     '03527220', '08070200', '02315550', '03164000'))

with st.container():
    if basin:
        show_data(basin)
