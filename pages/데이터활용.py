import pandas as pd
import streamlit as st
import plotly.express as px

# 파일 경로
file_path = '분202504_202504_연령별인구현황_월간 _남녀구분.csv'

# 데이터 불러오기
data = pd.read_csv(file_path, encoding='cp949')

# 서울특별시 데이터 필터링
seoul_data = data[data['행정구역'].str.contains('서울특별시')]

# 남자/여자 인구 합계 계산
age_columns = seoul_data.columns[2:]
male_population = seoul_data.iloc[:, 2::2].sum()
female_population = seoul_data.iloc[:, 3::2].sum()

# 연령대 라벨 추출
age_labels = [col.split(' ')[0] for col in age_columns[::2]]

# 길이 맞추기
min_length = min(len(age_labels), len(male_population), len(female_population))
age_labels = age_labels[:min_length]
male_population = male_population[:min_length]
female_population = female_population[:min_length]

# 데이터프레임 생성
population_pyramid = pd.DataFrame({
    'Age': age_labels,
    'Male': male_population.values,
    'Female': female_population.values
})
population_pyramid['Age'] = population_pyramid['Age'].astype(str)

# Streamlit 앱 구성
st.title('Seoul Population Pyramid')

fig = px.bar(population_pyramid, x='Male', y='Age', orientation='h', title='Male Population', color_discrete_sequence=['blue'])
fig.add_bar(x=population_pyramid['Female'], y=population_pyramid['Age'], orientation='h', name='Female Population', marker_color='red')

fig.update_layout(barmode='overlay', xaxis_title='Population', yaxis_title='Age', legend_title='Gender')

st.plotly_chart(fig)
