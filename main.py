import streamlit as st
import folium
import requests
from streamlit_folium import st_folium

# 미국 50개 주의 GeoJSON 파일 URL (여기서는 공개된 GeoJSON 파일을 사용)
geojson_url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.geojson"

# Streamlit 앱 제목
st.title("🇺🇸 미국 50개 주 경계 색상 지도")

# 주 선택
state = st.selectbox("주를 선택하세요:", ['전체', 'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii'])

# GeoJSON 데이터 가져오기
response = requests.get(geojson_url)
geojson_data = response.json()

# 지도 생성 (기본 지도 설정)
m = folium.Map(location=[37.0902, -95.7129], zoom_start=5)

# 경계 색상 적용 함수
def style_function(feature):
    # 'state' 속성에 따라 색상을 다르게 설정
    if state == '전체' or feature['properties']['name'] == state:
        return {
            'fillColor': 'green',  # 선택된 주나 전체는 초록색
            'color': 'black',      # 경계선 색은 검정
            'weight': 2,
            'fillOpacity': 0.6
        }
    else:
        return {
            'fillColor': 'gray',   # 나머지 주는 회색
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.3
        }

# GeoJSON 데이터를 지도에 추가
folium.GeoJson(geojson_data, style_function=style_function).add_to(m)

# Streamlit에 지도 표시
st_folium(m, width=700, height=500)
