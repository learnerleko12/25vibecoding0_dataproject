import pandas as pd
import plotly.express as px

# Load the data from the CSV file with proper encoding
file_path = '분202504_202504_연령별인구현황_월간 _남녀구분.csv'
data = pd.read_csv(file_path, encoding='cp949')

# Extract the rows for 서울특별시
seoul_data = data[data['행정구역'].str.contains('서울특별시')]

# Extract age columns for male and female separately
male_columns = [col for col in seoul_data.columns if '남자' in col]
female_columns = [col for col in seoul_data.columns if '여자' in col]

# Aggregate the male and female populations by age
male_population = seoul_data[male_columns].sum()
female_population = seoul_data[female_columns].sum()

# Extract age labels from columns
age_labels = [col.split()[0] for col in male_columns]

# Create a DataFrame for the population pyramid
population_pyramid = pd.DataFrame({
    'Age': age_labels,
    'Male': male_population.values,
    'Female': female_population.values
})

# Create the population pyramid using Plotly
fig = px.bar(population_pyramid, 
             x='Age', 
             y=['Male', 'Female'], 
             orientation='h', 
             title='Population Pyramid (Male vs Female)',
             labels={'value': 'Population', 'Age': 'Age'},
             barmode='overlay')

# Show the plot
fig.show()

