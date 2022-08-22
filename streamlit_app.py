#!/usr/bin/env python3

import streamlit as st
import geopandas as gpd
import pandas as pd
import leafmap.foliumap as leafmap
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
st.title("USGS/FORE-SCE Land Use Change Basins, 1979-2021")


def get_centroid(gage_id_geo, source):
    df = gpd.read_file("./Data/{}/Geojsons/{}.geojson".format(source, gage_id_geo))
    st.session_state.zoom_center_y = float(df["geometry"].centroid.x)
    st.session_state.zoom_center_x = float(df["geometry"].centroid.y)
    st.session_state.zoom_level = 12
    return df


def show_data(gage_id, data_source):
    if data_source == "USGS gagesII":
        source = "gagesII"
    elif data_source == "WRF-Hydro calibration basins":
        source = "calibration_basins"

    if gage_id == "All":
        df = gpd.read_file("./Data/{}/Geojsons/{}.geojson".format(source, gage_id))
        m = leafmap.Map(
            center=(33, -96),
            zoom=4,
            google_map="SATELLITE",
            plugin_Draw=True,
            Draw_export=True,
            locate_control=True,
            plugin_LatLngPopup=False,
        )
        m.add_gdf(df, layer_name=gage_id, zoom_to_layer=False, fill_colors=['blue'], info_mode='on_hover')
        m.to_streamlit(responsive=True)
    else:
        df2 = get_centroid(gage_id, source)
        m = leafmap.Map(
            center=(st.session_state.zoom_center_x, st.session_state.zoom_center_y),
            zoom=st.session_state.zoom_level,
            google_map="SATELLITE",
            plugin_Draw=True,
            Draw_export=True,
            locate_control=True,
            plugin_LatLngPopup=False,
        )
        m.add_gdf(df2, layer_name=gage_id, zoom_to_layer=False, fill_colors=['blue'], info_mode='on_hover')
        m.to_streamlit(responsive=True)

        col1, col2 = st.columns(2)
        with col1:
            st.write("Plotting Cell Changes")
            image = Image.open("./Data/{}/Plots/Tab_area_ID{}_changes.png".format(source, gage_id))
            st.image(image)

        with col2:
            st.write("Dataframe of All Cells")
            csv_df = pd.read_csv("./Data/{}/CSVs/Tab_area_ID{}_final.csv".format(source, gage_id), dtype={"Cell_Count": 'int'})
            cell_sum = csv_df["Cell_Count"].sum()
            urban_change_df = csv_df[(csv_df["New_LU_bin"] == "Urban") & (csv_df["Old_LU_bin"] != "Urban")]
            urban_change_sum = urban_change_df["Cell_Count"].sum()
            csv_df.rename(columns={'Old_LU_bin': '1978 Land Use', 'New_LU_bin': '2021 Land Use',
                                   'Cell_Count': 'Cell Count'}, inplace=True)
            st.dataframe(csv_df)
            st.write(f"Percent of cells that have changed to urban landcover: \n {urban_change_sum/cell_sum * 100:.2f}%")
        try:
            video = open("./Data/{}/Timelapses/{}.mp4".format(source, gage_id), 'rb')
            video_bytes = video.read()
            st.video(video_bytes)
        except FileNotFoundError:
            pass



with st.container():
    st.sidebar.title("Select basin data source:")
    data_source = st.sidebar.selectbox("Select a data source:", ("USGS gagesII", "WRF-Hydro calibration basins"))

    if data_source == "USGS gagesII":
        st.sidebar.title("Selecting basins:")
        basin = st.sidebar.selectbox('Select a basin:', ('02300700', '11180500', '02310147', '01208950', '03049800',
                                                         '03447894', '02246150', '05400650', '02301990', '02204130',
                                                         '02043500', '06914990'))
    elif data_source == "WRF-Hydro calibration basins":
        st.sidebar.title("Selecting basins:")
        basin = st.sidebar.selectbox('Select a basin:', ['08057200', '08154700', '06893500', '03535400',
                                                         '03292474', '03277075', '07165562', '07050690', '02335870',
                                                         '02336968', '02392975', '02457595', '02300700', '02207385',
                                                         '0209399200', '02095000', '02087359', '01381400', '01467042',
                                                         '01594526', '01464000', '01649500', '01465500', '04101370'])

with st.container():
    if basin:
        show_data(basin, data_source)
