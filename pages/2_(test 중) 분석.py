import io
import pandas as pd
import streamlit as st
from datetime import date, timedelta
import openpyxl
import re
from utils import KIND_OPTIONS, SITE_OPTIONS, PROCESS_OPTIONS, UNIT_OPTIONS
from utils import load_sheet_data
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# 페이지 설정
st.set_page_config(page_title="부동내역 필터링", layout="wide")
st.title("BM/PD 내역 분석")

# 1) 사이트 선택
selected_site = st.selectbox("🔍 분석할 사이트를 선택하세요", SITE_OPTIONS)

# 2) 전체 데이터 로드
df, error = load_sheet_data()
if error:
    st.error(error)
    st.stop()

# 3) ‘site’ 컬럼 자동 감지
cols = df.columns.tolist()
if "site" in df.columns:
    site_col = "site"
else:
    candidates = [c for c in cols if "사이트" in c or "Site" in c or "SITE" in c]
    if candidates:
        site_col = candidates[0]
        st.warning(f"‘{site_col}’ 컬럼을 사이트 식별용으로 자동 설정했습니다.")
    else:
        st.error(f"사이트 컬럼을 찾을 수 없습니다.\n→ 현재 컬럼 목록: {cols}")
        st.stop()

df_site = df[df[site_col] == selected_site].reset_index(drop=True)
st.subheader(f"{selected_site} 데이터 ({len(df_site)}건)")
st.dataframe(df_site)

# 4) 시간 컬럼 자동 탐지 및 변환
time_cols = {}
for col in df_site.columns:
    if re.search(r'발생', col):
        time_cols['발생시간'] = col
    elif re.search(r'완료', col):
        time_cols['조치완료'] = col

if '발생시간' not in time_cols or '조치완료' not in time_cols:
    st.error(f"시간 컬럼을 찾을 수 없습니다. 탐지된 컬럼: {time_cols}")
    st.stop()

df_site[time_cols['발생시간']] = pd.to_datetime(df_site[time_cols['발생시간']])
df_site[time_cols['조치완료']] = pd.to_datetime(df_site[time_cols['조치완료']])

# 컬럼명 정리 & time_cols 매핑 재설정 (필요시 수정)
df_site.columns = df_site.columns.str.strip()
time_cols = {
    '발생시간': time_cols['발생시간'],
    '조치완료': time_cols['조치완료']
}

# 5) 호기 선택 UI 및 소요시간 계산
st.subheader(f"호기 선택")
ho_list = sorted(df_site['호기'].unique())
selected_hos = st.multiselect("", ho_list, default=[])

if not selected_hos:
    st.info("하나 이상의 호기를 선택해주세요.")
else:
    df_sel = df_site[df_site['호기'].isin(selected_hos)].copy()
    df_sel['소요시간'] = df_sel[time_cols['조치완료']] - df_sel[time_cols['발생시간']]

    # 6) 각 호기별 분석
    for ho in selected_hos:
        ho_df = df_sel[df_sel['호기'] == ho]

        # 6-1) 발생횟수 Top 5
        cnt = (
            ho_df
            .groupby(['Machine','Unit',"Assy'"])
            .size()
            .reset_index(name='발생횟수')
            .sort_values('발생횟수', ascending=False)
            .head(5)
        )

        # 6-2) 총 소요시간 Top 5
        total = (
            ho_df
            .groupby(['Machine','Unit',"Assy'"])['소요시간']
            .sum()
            .reset_index()
        )
        total['총소요_초'] = total['소요시간'].dt.total_seconds()
        top_time = total.sort_values('총소요_초', ascending=False).head(5)

        with st.expander(f"호기 {ho} — Assy'별 Top5", expanded=True):
            st.markdown(f"#### 호기 {ho} — 발생횟수 vs 총소요시간")

            col1, col2 = st.columns(2)

            # ---- 발생횟수 AgGrid ----
            with col1:
                st.caption("발생횟수 Top 5")
                gb1 = GridOptionsBuilder.from_dataframe(cnt)
                gb1.configure_selection("single")
                grid1 = AgGrid(
                    cnt,
                    gridOptions=gb1.build(),
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    fit_columns_on_grid_load=True,
                )
                selected = grid1["selected_rows"]
                if isinstance(selected, pd.DataFrame):
                    selected = selected.to_dict("records")
                if selected:
                    m, u, a = selected[0]["Machine"], selected[0]["Unit"], selected[0]["Assy'"]
                    detail = ho_df[(ho_df["Machine"]==m)&(ho_df["Unit"]==u)&(ho_df["Assy'"]==a)]
                    st.write("**[발생횟수 Top 상세 목록]**")
                    st.dataframe(detail, use_container_width=True)

            # ---- 총소요시간 AgGrid ----
            with col2:
                st.caption("총 소요시간 Top 5 (초)")
                gb2 = GridOptionsBuilder.from_dataframe(
                    top_time[['Machine','Unit',"Assy'",'총소요_초']]
                )
                gb2.configure_selection("single")
                grid2 = AgGrid(
                    top_time[['Machine','Unit',"Assy'",'총소요_초']],
                    gridOptions=gb2.build(),
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    fit_columns_on_grid_load=True,
                )
                selected2 = grid2["selected_rows"]
                if isinstance(selected2, pd.DataFrame):
                    selected2 = selected2.to_dict("records")
                if selected2:
                    m2, u2, a2 = selected2[0]["Machine"], selected2[0]["Unit"], selected2[0]["Assy'"]
                    detail2 = ho_df[(ho_df["Machine"]==m2)&(ho_df["Unit"]==u2)&(ho_df["Assy'"]==a2)]
                    st.write("**[총 소요시간 Top 상세 목록]**")
                    st.dataframe(detail2, use_container_width=True)

import pandas as pd
import altair as alt
import streamlit as st
from datetime import timedelta

# (이전 코드에서 df_site 준비된 상태라고 가정)

# --- 일별 이벤트 트렌드 (최근 14일) ---
st.subheader("호기별 일별 이벤트 트렌드 (최근 14일)")
df_site['발생일'] = pd.to_datetime(df_site[time_cols['발생시간']]).dt.normalize()

today = pd.to_datetime('today').normalize()
recent = df_site[df_site['발생일'] >= (today - timedelta(days=30))]

# 피벗 테이블을 'long' 포맷으로 풀기
trend = (
    recent
    .groupby(['발생일','호기'])
    .size()
    .reset_index(name='count')
)

# Altair 차트 그리기
chart = (
    alt.Chart(trend)
    .mark_line(point=True)
    .encode(
        x=alt.X(
            '발생일:T',
            axis=alt.Axis(
                format='%m-%d',      # 월-일(예: 07-22) 포맷
                tickCount='day'
            )
        ),
        y=alt.Y('count:Q', title='이벤트 수'),
        color=alt.Color('호기:N', title='호기'),
        tooltip=['발생일:T', '호기:N', 'count:Q']
    )
    .properties(
        width=800,
        height=300
    )
    .interactive()
)

st.altair_chart(chart, use_container_width=True)
