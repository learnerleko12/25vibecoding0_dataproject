import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# 데이터 클리닝 함수: 숫자로 변환 (쉼표 제거)
def clean_population_data(value):
    if isinstance(value, str):
        return int(value.replace(',', ''))
    return value

# 행정구역 이름 정리 함수 (예: "서울특별시  (1100000000)" -> "서울특별시")
def clean_admin_district_name(name):
    if isinstance(name, str):
        match = re.match(r"([^(]+)\s*\(", name)
        if match:
            return match.group(1).strip()
    return name

# 데이터 로드 및 전처리 함수
@st.cache_data # 데이터 로딩 결과를 캐시하여 성능 향상
def load_data(file_path, is_gender_separated=False):
    try:
        df = pd.read_csv(file_path, encoding='cp949') # 한글 인코딩 문제 방지
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='utf-8')
    except FileNotFoundError:
        st.error(f"{file_path} 파일을 찾을 수 없습니다. 동일한 디렉토리에 파일이 있는지 확인하세요.")
        return None

    # 첫 번째 열 이름을 '행정구역'으로 표준화 (실제 파일에 따라 다를 수 있음)
    if df.columns[0] != '행정구역':
        df.rename(columns={df.columns[0]: '행정구역'}, inplace=True)

    df['행정구역'] = df['행정구역'].apply(clean_admin_district_name)
    df.set_index('행정구역', inplace=True)

    # 인구수 데이터 클리닝
    for col in df.columns:
        if '인구수' in col or '세' in col: # 총인구수, 연령구간인구수, 0세, 1세 등
            df[col] = df[col].apply(clean_population_data)
    return df

# 연령 컬럼 추출 함수
def get_age_columns(df_columns, prefix):
    age_cols = []
    for col in df_columns:
        if col.startswith(prefix) and (col.endswith('세') or col.endswith('세 이상')):
            if '연령구간인구수' not in col and '총인구수' not in col : # 전체 합계 컬럼 제외
                 age_cols.append(col)
    # '0세', '1세', ..., '100세 이상' 순으로 정렬하기 위한 키 함수
    def age_sort_key(col_name):
        age_part = col_name.replace(prefix, '').replace('세', '').replace(' 이상', '')
        return int(age_part) if age_part.isdigit() else 101 # '100세 이상'을 가장 뒤로
    
    return sorted(age_cols, key=age_sort_key)


# --- 스트림릿 앱 UI 구성 ---
st.set_page_config(layout="wide", page_title="대한민국 인구 현황 대시보드")
st.title("📊 대한민국 월별 연령별 인구 현황")
st.markdown("""
이 대시보드는 제공된 CSV 데이터를 기반으로 대한민국 행정구역별 인구 현황을 보여줍니다.
- **데이터 출처**: `202504_202504_연령별인구현황_월간_남녀합계.csv`, `202504_202504_연령별인구현황_월간 _남녀구분.csv` (가상 데이터)
- **참고**: 실제 데이터를 사용하려면 아래 파일 업로더를 사용하거나 코드 내 파일 경로를 수정하세요.
""")

# 파일 업로드 기능 (선택 사항)
uploaded_file_total = st.sidebar.file_uploader("1. 남녀 합계 인구 데이터 (CSV)", type="csv", key="total_pop_uploader")
uploaded_file_gender = st.sidebar.file_uploader("2. 남녀 구분 인구 데이터 (CSV)", type="csv", key="gender_pop_uploader")

# 기본 파일 경로 설정 (업로드된 파일이 없을 경우 사용)
# 중요: 이 파일들은 Streamlit 앱을 실행하는 Python 스크립트와 동일한 디렉토리에 있어야 합니다.
# 또는, 정확한 파일 경로를 지정해야 합니다.
DEFAULT_TOTAL_POP_FILE = '202504_202504_연령별인구현황_월간_남녀합계.csv'
DEFAULT_GENDER_POP_FILE = '202504_202504_연령별인구현황_월간 _남녀구분.csv'

df_total_pop = None
df_gender_pop = None

if uploaded_file_total:
    df_total_pop = load_data(uploaded_file_total)
else:
    st.sidebar.info(f"남녀 합계 기본 파일: `{DEFAULT_TOTAL_POP_FILE}` 사용 중")
    df_total_pop = load_data(DEFAULT_TOTAL_POP_FILE)

if uploaded_file_gender:
    df_gender_pop = load_data(uploaded_file_gender, is_gender_separated=True)
else:
    st.sidebar.info(f"남녀 구분 기본 파일: `{DEFAULT_GENDER_POP_FILE}` 사용 중")
    df_gender_pop = load_data(DEFAULT_GENDER_POP_FILE, is_gender_separated=True)


if df_total_pop is not None and df_gender_pop is not None:
    # 행정구역 선택
    admin_districts = df_total_pop.index.tolist()
    if not admin_districts:
        st.error("데이터에서 행정구역 정보를 찾을 수 없습니다. CSV 파일 형식을 확인해주세요.")
    else:
        selected_district = st.sidebar.selectbox("행정구역 선택", admin_districts)

        st.header(f"📍 {selected_district} 인구 현황")

        # 데이터에서 날짜 정보 추출 (컬럼명 기반)
        # 예: '2025년04월_계_총인구수' 에서 '2025년04월' 추출
        date_prefix_total = ""
        if df_total_pop.columns[0].startswith("20"): # '20'으로 시작하는 연도 가정
            date_prefix_total = df_total_pop.columns[0].split('_')[0] + "_"
        
        date_prefix_gender_male = ""
        date_prefix_gender_female = ""
        # 남성 데이터 컬럼에서 prefix 찾기
        for col in df_gender_pop.columns:
            if col.startswith("20") and "_남_" in col:
                date_prefix_gender_male = col.split('_남_')[0] + "_남_"
                break
        # 여성 데이터 컬럼에서 prefix 찾기
        for col in df_gender_pop.columns:
            if col.startswith("20") and "_여_" in col:
                date_prefix_gender_female = col.split('_여_')[0] + "_여_"
                break

        if not selected_district:
            st.warning("분석할 행정구역을 선택해주세요.")
        else:
            # 1. 총 인구수 (남녀 합계 데이터)
            st.subheader("1. 총 인구 정보")
            try:
                total_pop_col_name = f"{date_prefix_total.replace('_','')}계_총인구수" # '2025년04월계_총인구수'
                # 만약 위 컬럼명이 없다면, 첫번째 '_계_총인구수' 포함 컬럼 사용
                if total_pop_col_name not in df_total_pop.columns:
                    potential_cols = [col for col in df_total_pop.columns if '_계_총인구수' in col]
                    if potential_cols:
                        total_pop_col_name = potential_cols[0]
                    else:
                        st.error("총 인구수 컬럼을 찾을 수 없습니다.")
                        total_pop_col_name = None

                if total_pop_col_name:
                    total_population = df_total_pop.loc[selected_district, total_pop_col_name]
                    st.metric(label=f"{selected_district} 총 인구수 ({date_prefix_total.replace('_','')})", value=f"{total_population:,.0f} 명")

                # 2. 연령별 인구 분포 (남녀 합계 데이터)
                st.subheader("2. 연령별 인구 분포 (전체)")
                
                # '계'가 포함된 연령 컬럼 prefix 찾기 (예: '2025년04월_계_')
                age_col_prefix_total = ""
                for col in df_total_pop.columns:
                    if col.startswith(date_prefix_total.replace('_','')) and "_계_" in col and "세" in col: # '2025년04월_계_0세'
                         age_col_prefix_total = col.split('0세')[0] # '2025년04월_계_'
                         break
                if not age_col_prefix_total and date_prefix_total: # '2025년04월_계_' 같은 형태가 없을 경우
                    age_col_prefix_total = date_prefix_total + "계_"


                total_age_cols = get_age_columns(df_total_pop.columns, age_col_prefix_total)

                if not total_age_cols:
                    st.warning(f"'{age_col_prefix_total}'로 시작하는 연령별 인구 데이터를 찾을 수 없습니다. (남녀 합계 데이터)")
                else:
                    age_population_total = df_total_pop.loc[selected_district, total_age_cols]
                    age_population_total.index = [col.replace(age_col_prefix_total, '') for col in total_age_cols]
                    
                    # 연령대별 그룹화 옵션
                    group_ages = st.sidebar.checkbox("연령대별 그룹화 (10세 단위)", value=True)
                    if group_ages:
                        bins = list(range(0, 101, 10)) + [age_population_total.index.map(lambda x: int(re.sub(r'[^0-9]', '', x))).max() + 1]
                        labels = [f"{bins[i]}-{bins[i+1]-1}세" for i in range(len(bins)-2)] + [f"{bins[-2]}세 이상"]
                        
                        age_population_total_grouped = pd.Series(index=labels, dtype='int64').fillna(0)
                        for age_str, pop in age_population_total.items():
                            age_val = int(re.sub(r'[^0-9]', '', age_str)) # "80-89세" 등 문자열 처리 대비
                            for i in range(len(bins)-1):
                                if bins[i] <= age_val < bins[i+1]:
                                    age_population_total_grouped[labels[i]] += pop
                                    break
                        fig_age_dist_total = px.bar(age_population_total_grouped, 
                                                    x=age_population_total_grouped.index, 
                                                    y=age_population_total_grouped.values,
                                                    labels={'x': '연령대', 'y': '인구수'},
                                                    title=f"{selected_district} 연령대별 인구 분포")
                    else:
                        fig_age_dist_total = px.bar(age_population_total, 
                                                    x=age_population_total.index, 
                                                    y=age_population_total.values,
                                                    labels={'x': '연령', 'y': '인구수'},
                                                    title=f"{selected_district} 세부 연령별 인구 분포")
                    fig_age_dist_total.update_layout(xaxis_title="연령(대)", yaxis_title="인구수")
                    st.plotly_chart(fig_age_dist_total, use_container_width=True)

                # 3. 성별 인구 정보 (남녀 구분 데이터)
                st.subheader("3. 성별 인구 정보")
                
                male_total_col = f"{date_prefix_gender_male.replace('_남_','')}남_총인구수" # '2025년04월남_총인구수'
                female_total_col = f"{date_prefix_gender_female.replace('_여_','')}여_총인구수" # '2025년04월여_총인구수'

                # 컬럼명 정확히 일치하지 않을 경우 대비
                if male_total_col not in df_gender_pop.columns:
                    potential_cols = [col for col in df_gender_pop.columns if '_남_총인구수' in col]
                    if potential_cols: male_total_col = potential_cols[0]
                    else: male_total_col = None
                
                if female_total_col not in df_gender_pop.columns:
                    potential_cols = [col for col in df_gender_pop.columns if '_여_총인구수' in col]
                    if potential_cols: female_total_col = potential_cols[0]
                    else: female_total_col = None

                if male_total_col and female_total_col:
                    male_population = df_gender_pop.loc[selected_district, male_total_col]
                    female_population = df_gender_pop.loc[selected_district, female_total_col]

                    col1, col2 = st.columns(2)
                    col1.metric(label=f"남성 총 인구수 ({date_prefix_gender_male.split('_')[0]})", value=f"{male_population:,.0f} 명")
                    col2.metric(label=f"여성 총 인구수 ({date_prefix_gender_female.split('_')[0]})", value=f"{female_population:,.0f} 명")

                    # 4. 인구 피라미드 (남녀 구분 데이터)
                    st.subheader("4. 인구 피라미드")
                    male_age_cols = get_age_columns(df_gender_pop.columns, date_prefix_gender_male)
                    female_age_cols = get_age_columns(df_gender_pop.columns, date_prefix_gender_female)

                    if not male_age_cols or not female_age_cols:
                        st.warning("남성 또는 여성 연령별 인구 데이터를 찾을 수 없습니다. (남녀 구분 데이터)")
                    else:
                        male_age_pop = df_gender_pop.loc[selected_district, male_age_cols].rename(lambda x: x.replace(date_prefix_gender_male, ''))
                        female_age_pop = df_gender_pop.loc[selected_district, female_age_cols].rename(lambda x: x.replace(date_prefix_gender_female, ''))
                        
                        # 연령 라벨 통일 (예: '0세', '1세', ... )
                        age_labels = [col.replace(date_prefix_gender_male, '').replace('세 이상', '세+').replace('세','') for col in male_age_cols]
                        
                        # 그룹화 적용
                        if group_ages:
                            bins_pyramid = list(range(0, 101, 10)) + [max(male_age_pop.index.map(lambda x: int(re.sub(r'[^0-9]', '', x))).max(), 
                                                                        female_age_pop.index.map(lambda x: int(re.sub(r'[^0-9]', '', x))).max()) +1]
                            labels_pyramid = [f"{bins_pyramid[i]}-{bins_pyramid[i+1]-1}" for i in range(len(bins_pyramid)-2)] + [f"{bins_pyramid[-2]}+"]
                            
                            male_age_pop_grouped = pd.Series(index=labels_pyramid, dtype='int64').fillna(0)
                            female_age_pop_grouped = pd.Series(index=labels_pyramid, dtype='int64').fillna(0)

                            for age_str, pop in male_age_pop.items():
                                age_val = int(re.sub(r'[^0-9]', '', age_str))
                                for i in range(len(bins_pyramid)-1):
                                    if bins_pyramid[i] <= age_val < bins_pyramid[i+1]:
                                        male_age_pop_grouped[labels_pyramid[i]] += pop
                                        break
                            for age_str, pop in female_age_pop.items():
                                age_val = int(re.sub(r'[^0-9]', '', age_str))
                                for i in range(len(bins_pyramid)-1):
                                    if bins_pyramid[i] <= age_val < bins_pyramid[i+1]:
                                        female_age_pop_grouped[labels_pyramid[i]] += pop
                                        break
                            y_labels = labels_pyramid
                            male_data = male_age_pop_grouped
                            female_data = female_age_pop_grouped

                        else: # 그룹화 안 할 경우
                            y_labels = age_labels
                            male_data = male_age_pop
                            female_data = female_age_pop


                        fig_pyramid = go.Figure()
                        fig_pyramid.add_trace(go.Bar(
                            y=y_labels,
                            x=-male_data.values, # 남성 인구는 음수로 표현
                            name='남성',
                            orientation='h',
                            marker=dict(color='cornflowerblue')
                        ))
                        fig_pyramid.add_trace(go.Bar(
                            y=y_labels,
                            x=female_data.values,
                            name='여성',
                            orientation='h',
                            marker=dict(color='lightcoral')
                        ))
                        fig_pyramid.update_layout(
                            title=f'{selected_district} 인구 피라미드{" (10세 단위)" if group_ages else " (세부 연령)"}',
                            yaxis_title='연령(대)',
                            xaxis_title='인구수',
                            barmode='relative', # 막대를 서로 겹치지 않게 표시 (음수/양수)
                            bargap=0.1,
                            xaxis=dict(
                                tickvals=[-max(male_data.max(), female_data.max()), 0, max(male_data.max(), female_data.max())], # x축 눈금 설정
                                ticktext=[f"{max(male_data.max(), female_data.max()):,.0f}", "0", f"{max(male_data.max(), female_data.max()):,.0f}"] # x축 눈금 텍스트
                            ),
                            legend_title_text='성별'
                        )
                        st.plotly_chart(fig_pyramid, use_container_width=True)
                else:
                    st.warning("남성 또는 여성 총 인구수 컬럼명을 데이터에서 찾을 수 없습니다. (남녀 구분 데이터)")


            except KeyError as e:
                st.error(f"선택된 '{selected_district}'에 대한 데이터를 처리하는 중 오류가 발생했습니다: {e}. CSV 파일의 행정구역명과 컬럼명을 확인해주세요.")
            except Exception as e:
                st.error(f"데이터 시각화 중 예기치 않은 오류 발생: {e}")

            # 5. 데이터 테이블 표시
            st.subheader("5. 데이터 보기")
            show_total_data = st.checkbox("남녀 합계 데이터 테이블 보기")
            if show_total_data:
                st.dataframe(df_total_pop.loc[[selected_district]])
            
            show_gender_data = st.checkbox("남녀 구분 데이터 테이블 보기")
            if show_gender_data:
                st.dataframe(df_gender_pop.loc[[selected_district]])
else:
    st.error("데이터 파일을 불러오는 데 실패했습니다. 파일 경로와 내용을 확인해주세요.")

st.sidebar.markdown("---")
st.sidebar.markdown("본 대시보드는 Streamlit을 사용하여 제작되었습니다.")

