import streamlit as st
import folium
import requests
from streamlit_folium import st_folium

# 최신 US states geojson 링크
geojson_url = "https://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_040_00_500k.json"

st.title("🇺🇸 미국 50개 주 경계 색상 지도")

# 주 리스트는 GeoJSON 파일의 'NAME'과 정확히 일치해야 합니다.
state_list = [
    '전체', 'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
    'Connecticut', 'Delaware', 'District of Columbia', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois',
    'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts',
    'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada',
    'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota',
    'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina',
    'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
    'West Virginia', 'Wisconsin', 'Wyoming'
]
state = st.selectbox("주를 선택하세요:", state_list)

# GeoJSON 데이터 요청
response = requests.get(geojson_url)
geojson_data = response.json()

# Folium 지도 생성
m = folium.Map(location=[37.8, -96], zoom_start=4)

def style_function(feature):
    # GeoJSON의 주 이름은 'NAME' 필드에 있음!
    if state == '전체' or feature['properties']['NAME'] == state:
        return {
            'fillColor': 'orange',
            'color': 'black',
            'weight': 2,
            'fillOpacity': 0.7
        }
    else:
        return {
            'fillColor': 'lightgray',
            'color': 'gray',
            'weight': 1,
            'fillOpacity': 0.3
        }

folium.GeoJson(
    geojson_data,
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(fields=['NAME'])
).add_to(m)

st_folium(m, width=800, height=600)
