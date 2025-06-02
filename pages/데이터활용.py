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

# 데이터 로드 및 전처리 함수 (URL 지원)
@st.cache_data # 데이터 로딩 결과를 캐시하여 성능 향상
def load_data(url, is_gender_separated=False):
    try:
        df = pd.read_csv(url, encoding='cp949') # 한글 인코딩 문제 방지
    except UnicodeDecodeError:
        df = pd.read_csv(url, encoding='utf-8')
    except Exception as e: # URL 접근 오류 등 다양한 예외 처리
        st.error(f"데이터를 불러오는 중 오류 발생: {url}")
        st.error(f"오류 메시지: {e}")
        st.error("GitHub Raw URL이 정확한지, 파일이 공개되어 있는지 확인해주세요.")
        return None

    if df is None: # 파일 로드 실패 시
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

# 연령대별 인구 집계 함수
def get_population_by_age_category(age_population_series):
    youth_pop = 0  # 0-14세
    working_age_pop = 0  # 15-64세
    elderly_pop = 0  # 65세 이상

    for age_label, pop in age_population_series.items():
        try:
            age_numeric_str_match = re.match(r"(\d+)", age_label)
            if age_numeric_str_match:
                age = int(age_numeric_str_match.group(1))
            else: 
                st.warning(f"연령 라벨 '{age_label}'에서 숫자 부분을 추출하지 못했습니다. 이 데이터는 집계에서 제외됩니다.")
                continue

            if 0 <= age <= 14:
                youth_pop += pop
            elif 15 <= age <= 64:
                working_age_pop += pop
            elif age >= 65: 
                elderly_pop += pop
        except ValueError:
            st.warning(f"연령 라벨 '{age_label}'을(를) 처리하는 중 오류 발생. 이 데이터는 집계에서 제외됩니다.")
            continue
            
    total_pop_for_categories = youth_pop + working_age_pop + elderly_pop
    return youth_pop, working_age_pop, elderly_pop, total_pop_for_categories

# --- 스트림릿 앱 UI 구성 ---
st.set_page_config(layout="wide", page_title="대한민국 인구 현황 대시보드")
st.title("📊 대한민국 월별 연령별 인구 현황")
st.markdown("""
이 대시보드는 GitHub에 업로드된 CSV 데이터를 기반으로 대한민국 행정구역별 인구 현황을 보여줍니다.
- **데이터 출처**: GitHub Raw CSV 파일 (아래 URL 참조)
""")

# --- GitHub Raw CSV URL 설정 ---
# 중요: 아래 URL을 실제 GitHub Raw 파일 주소로 변경해주세요.
# 예시: GITHUB_TOTAL_POP_URL = "https://raw.githubusercontent.com/your_username/your_repository/main/path/to/your_total_pop_file.csv"
GITHUB_TOTAL_POP_URL = "https://raw.githubusercontent.com/Statground/Public-Data-Storage/main/Age_Gender_Population/202504_202504_%EC%97%B0%EB%A0%B9%EB%B3%84%EC%9D%B8%EA%B5%AC%ED%98%84%ED%99%A9_%EC%9B%94%EA%B0%84_%EB%82%A8%EB%85%80%ED%95%A9%EA%B3%84.csv" # 예시 URL, 실제 URL로 변경 필요
GITHUB_GENDER_POP_URL = "https://raw.githubusercontent.com/Statground/Public-Data-Storage/main/Age_Gender_Population/202504_202504_%EC%97%B0%EB%A0%B9%EB%B3%84%EC%9D%B8%EA%B5%AC%ED%98%84%ED%99%A9_%EC%9B%94%EA%B0%84%20_%EB%82%A8%EB%85%80%EA%B5%AC%EB%B6%84.csv" # 예시 URL, 실제 URL로 변경 필요

st.sidebar.markdown("### 데이터 소스")
st.sidebar.info(f"""
남녀 합계 데이터: [GitHub Link]({GITHUB_TOTAL_POP_URL})
남녀 구분 데이터: [GitHub Link]({GITHUB_GENDER_POP_URL})

위 링크의 Raw CSV 파일을 사용합니다.
""")


df_total_pop = load_data(GITHUB_TOTAL_POP_URL)
df_gender_pop = load_data(GITHUB_GENDER_POP_URL, is_gender_separated=True)


if df_total_pop is not None and df_gender_pop is not None:
    admin_districts = df_total_pop.index.tolist()
    if not admin_districts:
        st.error("데이터에서 행정구역 정보를 찾을 수 없습니다. CSV 파일 형식을 확인해주세요.")
    else:
        selected_district = st.sidebar.selectbox("행정구역 선택", admin_districts)

        st.header(f"📍 {selected_district} 인구 현황")

        date_prefix_total = ""
        if df_total_pop.columns[0].startswith("20"):
            date_prefix_total = df_total_pop.columns[0].split('_')[0] + "_"
        
        date_prefix_gender_male = ""
        date_prefix_gender_female = ""
        for col in df_gender_pop.columns:
            if col.startswith("20") and "_남_" in col:
                date_prefix_gender_male = col.split('_남_')[0] + "_남_"
                break
        for col in df_gender_pop.columns:
            if col.startswith("20") and "_여_" in col:
                date_prefix_gender_female = col.split('_여_')[0] + "_여_"
                break

        if not selected_district:
            st.warning("분석할 행정구역을 선택해주세요.")
        else:
            try:
                # 1. 총 인구수 (남녀 합계 데이터)
                st.subheader("1. 총 인구 정보")
                total_pop_col_name = f"{date_prefix_total.replace('_','')}계_총인구수"
                if total_pop_col_name not in df_total_pop.columns:
                    potential_cols = [col for col in df_total_pop.columns if '_계_총인구수' in col]
                    if potential_cols:
                        total_pop_col_name = potential_cols[0]
                    else:
                        st.error("총 인구수 컬럼을 찾을 수 없습니다.")
                        total_pop_col_name = None

                current_total_population = 0
                if total_pop_col_name:
                    current_total_population = df_total_pop.loc[selected_district, total_pop_col_name]
                    st.metric(label=f"{selected_district} 총 인구수 ({date_prefix_total.replace('_','')})", value=f"{current_total_population:,.0f} 명")

                # '계'가 포함된 연령 컬럼 prefix 찾기
                age_col_prefix_total = ""
                for col in df_total_pop.columns:
                    if col.startswith(date_prefix_total.replace('_','')) and "_계_" in col and "세" in col:
                         age_col_prefix_total = col.split('0세')[0] 
                         break
                if not age_col_prefix_total and date_prefix_total:
                    age_col_prefix_total = date_prefix_total + "계_"
                
                total_age_cols = get_age_columns(df_total_pop.columns, age_col_prefix_total)
                age_population_total = None
                if total_age_cols:
                    age_population_total = df_total_pop.loc[selected_district, total_age_cols]
                    age_population_total.index = [col.replace(age_col_prefix_total, '') for col in total_age_cols]

                # 2. 인구 구조 분석
                st.subheader("2. 인구 구조 분석")
                if age_population_total is not None and not age_population_total.empty:
                    youth_pop, working_age_pop, elderly_pop, sum_categories = get_population_by_age_category(age_population_total)

                    if sum_categories > 0 : 
                        youth_ratio = (youth_pop / sum_categories) * 100
                        working_age_ratio = (working_age_pop / sum_categories) * 100
                        elderly_ratio = (elderly_pop / sum_categories) * 100

                        st.markdown("#### 연령대별 인구 비율")
                        col_struct1, col_struct2, col_struct3 = st.columns(3)
                        col_struct1.metric("유소년인구 (0-14세)", f"{youth_ratio:.1f}%", f"{youth_pop:,.0f} 명")
                        col_struct2.metric("생산가능인구 (15-64세)", f"{working_age_ratio:.1f}%", f"{working_age_pop:,.0f} 명")
                        col_struct3.metric("고령인구 (65세 이상)", f"{elderly_ratio:.1f}%", f"{elderly_pop:,.0f} 명")

                        structure_data = {
                            '구분': ['유소년인구 (0-14세)', '생산가능인구 (15-64세)', '고령인구 (65세 이상)'],
                            '인구수': [youth_pop, working_age_pop, elderly_pop]
                        }
                        df_structure = pd.DataFrame(structure_data)
                        fig_structure_pie = px.pie(df_structure, names='구분', values='인구수', 
                                                   title=f'{selected_district} 인구 구조',
                                                   color_discrete_sequence=px.colors.qualitative.Pastel)
                        fig_structure_pie.update_traces(textinfo='percent+label', insidetextorientation='radial')
                        st.plotly_chart(fig_structure_pie, use_container_width=True)
                    else:
                        st.warning("인구 구조 분석을 위한 데이터가 충분하지 않거나 총 인구가 0입니다.")
                else:
                    st.warning(f"'{age_col_prefix_total}'로 시작하는 연령별 인구 데이터를 찾을 수 없어 인구 구조 분석을 할 수 없습니다. (남녀 합계 데이터)")

                # 3. 연령별 인구 분포 (전체)
                st.subheader("3. 연령별 인구 분포 (전체)")
                group_ages = st.sidebar.checkbox("연령대별 그룹화 (10세 단위)", value=True) 

                if age_population_total is not None and not age_population_total.empty:
                    if group_ages:
                        try:
                            max_age_val = age_population_total.index.map(lambda x: int(re.sub(r'[^0-9]', '', x))).max()
                            bins = list(range(0, 101, 10)) + [max_age_val + 1]
                            labels = [f"{bins[i]}-{bins[i+1]-1}세" for i in range(len(bins)-2)] + [f"{bins[-2]}세 이상"]
                            
                            age_population_total_grouped = pd.Series(index=labels, dtype='int64').fillna(0)
                            for age_str, pop in age_population_total.items():
                                age_val = int(re.sub(r'[^0-9]', '', age_str)) 
                                for i in range(len(bins)-1):
                                    if bins[i] <= age_val < bins[i+1]:
                                        age_population_total_grouped[labels[i]] += pop
                                        break
                            fig_age_dist_total = px.bar(age_population_total_grouped, 
                                                        x=age_population_total_grouped.index, 
                                                        y=age_population_total_grouped.values,
                                                        labels={'x': '연령대', 'y': '인구수'},
                                                        title=f"{selected_district} 연령대별 인구 분포")
                        except Exception as e:
                            st.error(f"연령대별 그룹화 중 오류 발생: {e}")
                            fig_age_dist_total = None 
                    else:
                        fig_age_dist_total = px.bar(age_population_total, 
                                                    x=age_population_total.index, 
                                                    y=age_population_total.values,
                                                    labels={'x': '연령', 'y': '인구수'},
                                                    title=f"{selected_district} 세부 연령별 인구 분포")
                    if fig_age_dist_total:
                        fig_age_dist_total.update_layout(xaxis_title="연령(대)", yaxis_title="인구수")
                        st.plotly_chart(fig_age_dist_total, use_container_width=True)
                else:
                    st.warning(f"'{age_col_prefix_total}'로 시작하는 연령별 인구 데이터를 찾을 수 없습니다. (남녀 합계 데이터)")

                # 4. 성별 인구 정보
                st.subheader("4. 성별 인구 정보")
                male_total_col = f"{date_prefix_gender_male.replace('_남_','')}남_총인구수"
                female_total_col = f"{date_prefix_gender_female.replace('_여_','')}여_총인구수"

                if male_total_col not in df_gender_pop.columns:
                    potential_cols = [col for col in df_gender_pop.columns if '_남_총인구수' in col]
                    if potential_cols: male_total_col = potential_cols[0]
                    else: male_total_col = None
                
                if female_total_col not in df_gender_pop.columns:
                    potential_cols = [col for col in df_gender_pop.columns if '_여_총인구수' in col]
                    if potential_cols: female_total_col = potential_cols[0]
                    else: female_total_col = None

                male_population = 0
                female_population = 0

                if male_total_col and female_total_col:
                    male_population = df_gender_pop.loc[selected_district, male_total_col]
                    female_population = df_gender_pop.loc[selected_district, female_total_col]

                    col1, col2, col3 = st.columns(3)
                    col1.metric(label=f"남성 총 인구수 ({date_prefix_gender_male.split('_')[0]})", value=f"{male_population:,.0f} 명")
                    col2.metric(label=f"여성 총 인구수 ({date_prefix_gender_female.split('_')[0]})", value=f"{female_population:,.0f} 명")
                    
                    if female_population > 0:
                        sex_ratio = (male_population / female_population) * 100
                        col3.metric(label="성비 (여성 100명당 남성 수)", value=f"{sex_ratio:.1f} 명")
                    else:
                        col3.metric(label="성비", value="N/A (여성 인구 0)")
                else:
                    st.warning("남성 또는 여성 총 인구수 컬럼명을 데이터에서 찾을 수 없습니다. (남녀 구분 데이터)")

                # 5. 인구 피라미드
                st.subheader("5. 인구 피라미드")
                male_age_cols = get_age_columns(df_gender_pop.columns, date_prefix_gender_male)
                female_age_cols = get_age_columns(df_gender_pop.columns, date_prefix_gender_female)

                if not male_age_cols or not female_age_cols:
                    st.warning("남성 또는 여성 연령별 인구 데이터를 찾을 수 없습니다. (남녀 구분 데이터)")
                else:
                    male_age_pop = df_gender_pop.loc[selected_district, male_age_cols].rename(lambda x: x.replace(date_prefix_gender_male, ''))
                    female_age_pop = df_gender_pop.loc[selected_district, female_age_cols].rename(lambda x: x.replace(date_prefix_gender_female, ''))
                    
                    age_labels_raw = [col.replace(date_prefix_gender_male, '') for col in male_age_cols] 
                    
                    if group_ages:
                        try:
                            max_age_val_pyramid = max(
                                male_age_pop.index.map(lambda x: int(re.sub(r'[^0-9]', '', x))).max(),
                                female_age_pop.index.map(lambda x: int(re.sub(r'[^0-9]', '', x))).max() 
                            )
                            bins_pyramid = list(range(0, 101, 10)) + [max_age_val_pyramid + 1]
                            labels_pyramid = [f"{bins_pyramid[i]}-{bins_pyramid[i+1]-1}세" for i in range(len(bins_pyramid)-2)] + [f"{bins_pyramid[-2]}세 이상"]
                            
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
                        except Exception as e:
                            st.error(f"인구 피라미드 그룹화 중 오류 발생: {e}")
                            y_labels, male_data, female_data = age_labels_raw, male_age_pop, female_age_pop 
                    else: 
                        y_labels = age_labels_raw
                        male_data = male_age_pop
                        female_data = female_age_pop

                    if not male_data.empty and not female_data.empty:
                        fig_pyramid = go.Figure()
                        fig_pyramid.add_trace(go.Bar(
                            y=y_labels,
                            x=-male_data.values, 
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
                        
                        max_abs_pop = max(abs(male_data.min()), male_data.max(), abs(female_data.min()), female_data.max()) if not male_data.empty and not female_data.empty else 1000

                        fig_pyramid.update_layout(
                            title=f'{selected_district} 인구 피라미드{" (10세 단위)" if group_ages else " (세부 연령)"}',
                            yaxis_title='연령(대)',
                            xaxis_title='인구수',
                            barmode='relative', 
                            bargap=0.1,
                            xaxis=dict(
                                tickvals=[-max_abs_pop, 0, max_abs_pop], 
                                ticktext=[f"{max_abs_pop:,.0f}", "0", f"{max_abs_pop:,.0f}"] 
                            ),
                            legend_title_text='성별'
                        )
                        st.plotly_chart(fig_pyramid, use_container_width=True)
                    else:
                        st.warning("인구 피라미드를 그릴 데이터가 부족합니다.")

                # 6. 데이터 테이블 표시
                st.subheader("6. 데이터 보기")
                show_total_data = st.checkbox("남녀 합계 데이터 테이블 보기")
                if show_total_data:
                    st.dataframe(df_total_pop.loc[[selected_district]])
                
                show_gender_data = st.checkbox("남녀 구분 데이터 테이블 보기")
                if show_gender_data:
                    st.dataframe(df_gender_pop.loc[[selected_district]])

            except KeyError as e:
                st.error(f"선택된 '{selected_district}'에 대한 데이터를 처리하는 중 오류가 발생했습니다: {e}. CSV 파일의 행정구역명과 컬럼명을 확인해주세요.")
            except Exception as e:
                st.error(f"데이터 시각화 중 예기치 않은 오류 발생: {e}")
else:
    st.error("GitHub에서 데이터 파일을 불러오는 데 실패했습니다. URL과 파일 접근 권한을 확인해주세요.")

st.sidebar.markdown("---")
st.sidebar.markdown("본 대시보드는 Streamlit을 사용하여 제작되었습니다.")

