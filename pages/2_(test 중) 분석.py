import io
import pandas as pd
import streamlit as st
from datetime import date
import openpyxl
import re

from utils import KIND_OPTIONS, SITE_OPTIONS, PROCESS_OPTIONS, UNIT_OPTIONS
from utils import load_sheet_data

# — Streamlit UI
st.set_page_config(page_title="부동내역 필터링", layout="wide")
st.title("BM/PD 내역 분석")

# 1) 사이트 선택
selected_site = st.selectbox("🔍 분석할 사이트를 선택하세요", SITE_OPTIONS)

# 2) 전체 데이터 로드
df, error = load_sheet_data()
if error:
    st.error(error)
    st.stop()

# 3) ‘site’ 컬럼 자동 감지 로직
cols = df.columns.tolist()
if "site" in df.columns:
    site_col = "site"
else:
    # ‘사이트’, ‘Site’ 키워드로 후보 탐색
    candidates = [c for c in cols if "사이트" in c or "Site" in c or "SITE" in c]
    if candidates:
        site_col = candidates[0]
        st.warning(f"‘{site_col}’ 컬럼을 사이트 식별용으로 자동 설정했습니다.")
    else:
        st.error(f"사이트 컬럼을 찾을 수 없습니다.\n→ 현재 컬럼 목록: {cols}")
        st.stop()

# 4) 선택된 사이트로 필터링
df_site = df[df[site_col] == selected_site].reset_index(drop=True)

# 5) 결과 출력
st.subheader(f"{selected_site} 데이터 ({len(df_site)}건)")
st.dataframe(df_site)
# 1) 시간 컬럼 자동 탐지
time_cols = {}
for col in df_site.columns:
    if re.search(r'발생', col):
        time_cols['발생시간'] = col
    elif re.search(r'완료', col):
        time_cols['조치완료'] = col

# 2) 컬럼이 잘 잡혔는지 확인
if '발생시간' not in time_cols or '조치완료' not in time_cols:
    st.error(f"시간 컬럼을 찾을 수 없습니다. 탐지된 컬럼: {time_cols}")
    st.stop()

# 3) datetime 변환
df_site[time_cols['발생시간']] = pd.to_datetime(df_site[time_cols['발생시간']])
df_site[time_cols['조치완료']] = pd.to_datetime(df_site[time_cols['조치완료']])

# 4) 이후 분석 예시 (다섯 가지 아이디어 모두 포함)

# 4-1) 호기별 상위 5개 이슈
group = (
    df_site
    .groupby(['호기', '현상', '원인'])
    .size()
    .reset_index(name='발생횟수')
)
top_issues = (
    group
    .sort_values(['호기', '발생횟수'], ascending=[True, False])
    .groupby('호기')
    .head(5)
)
st.subheader("1. 호기별 상위 5개 이슈")
st.dataframe(top_issues)

# 4-2) 호기별 평균 조치 소요시간
df_site['소요시간'] = df_site[time_cols['조치완료']] - df_site[time_cols['발생시간']]
avg_time = (
    df_site
    .groupby('호기')['소요시간']
    .mean()
    .reset_index()
)
st.subheader("2. 호기별 평균 조치 소요시간")
st.dataframe(avg_time)

# 4-3) 호기별 일별 이벤트 트렌드
df_site['발생일'] = df_site[time_cols['발생시간']].dt.date
trend = (
    df_site
    .groupby(['발생일', '호기'])
    .size()
    .unstack(fill_value=0)
)
st.subheader("3. 호기별 일별 이벤트 트렌드")
st.line_chart(trend)

# 4-4) 원인별 호기 분포
cause_dist = (
    df_site
    .groupby(['원인', '호기'])
    .size()
    .reset_index(name='count')
)
st.subheader("4. 원인별 호기 분포")
st.dataframe(cause_dist)

# 4-5) 우선순위 지표 생성
freq = df_site.groupby('호기').size().rename('발생횟수')
mean_sec = df_site.groupby('호기')['소요시간'].mean().dt.total_seconds().rename('평균소요_초')
priority = (
    pd.concat([freq, mean_sec], axis=1)
    .assign(우선순위_지표=lambda d: d['발생횟수'] * d['평균소요_초'])
    .reset_index()
)
st.subheader("5. 호기별 우선순위 지표")
st.dataframe(priority)