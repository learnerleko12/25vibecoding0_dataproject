import streamlit as st
import plotly.express as px
import pandas as pd

# Load the data (you can replace this with your actual data loading logic)
df1 = pd.read_csv('/mnt/data/202504_202504_연령별인구현황_남녀합계.csv', encoding='cp949')

# Set up Streamlit UI
st.title('서울특별시 인구 데이터 시각화')
st.write('연령별, 성별로 서울특별시의 인구 데이터를 시각화한 그래프입니다.')

# Let the user select a region from the list
region = st.selectbox('지역을 선택하세요:', df1['행정구역'].unique())

# Filter the dataframe based on the selected region
df_region = df1[df1['행정구역'] == region]

# Let the user select the age group
age_group = st.selectbox('연령대를 선택하세요:', [col for col in df_region.columns if '계_' in col])

# Filter columns for the selected age group
df_plot = df_region[['행정구역', age_group]]

# Create a line chart using Plotly
fig = px.line(df_plot, x='행정구역', y=age_group, title=f'{region}의 {age_group} 인구 수')

# Show the plot
st.plotly_chart(fig)
