import io
import pandas as pd
import streamlit as st
from datetime import date, timedelta
import openpyxl
import re

from utils import KIND_OPTIONS, SITE_OPTIONS, PROCESS_OPTIONS, UNIT_OPTIONS, load_sheet_data
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

# — 페이지 설정
st.set_page_config(page_title="Assy 별 이슈 (고질이슈 파악)", layout="wide")
st.title("Assy 별 이슈 (고질이슈 파악)")

# 1) 사이트 선택
selected_site = st.selectbox("🔍 분석할 사이트를 선택하세요", SITE_OPTIONS, index=0)

# 2) 전체 데이터 로드
df, error = load_sheet_data()
if error:
    st.error(error)
    st.stop()

# 3) ‘site’ 컬럼 자동 감지
cols = df.columns.str.strip().str.lower()
if "site" in cols:
    site_col = df.columns[cols.tolist().index("site")]
else:
    candidates = [c for c in df.columns if re.search(r"사이트|Site|SITE", c)]
    if candidates:
        site_col = candidates[0]
        st.warning(f"‘{site_col}’ 컬럼을 사이트 식별용으로 자동 설정했습니다.")
    else:
        st.error(f"사이트 컬럼을 찾을 수 없습니다.\n→ 현재 컬럼 목록: {list(df.columns)}")
        st.stop()

# 4) 해당 사이트 필터링
df_site = df[df[site_col] == selected_site].reset_index(drop=True)
if df_site.empty:
    st.warning(f"‘{selected_site}’ 에 해당하는 데이터가 없습니다.")
    st.stop()

# st.subheader(f"{selected_site} 데이터 ({len(df_site)}건)")
# st.dataframe(df_site, use_container_width=True)

# 5) 시간 컬럼 자동 탐지 및 변환
time_cols = {}
for col in df_site.columns:
    if re.search(r"발생", col):
        time_cols["발생시간"] = col
    elif re.search(r"완료", col):
        time_cols["조치완료"] = col

if "발생시간" not in time_cols or "조치완료" not in time_cols:
    st.error(f"시간 컬럼을 찾을 수 없습니다. 탐지된 컬럼: {time_cols}")
    st.stop()

df_site[time_cols["발생시간"]] = pd.to_datetime(df_site[time_cols["발생시간"]])
df_site[time_cols["조치완료"]] = pd.to_datetime(df_site[time_cols["조치완료"]])

# 6) 컬럼명 정리 & time_cols 재매핑
df_site.columns = df_site.columns.str.strip()
occur_col = time_cols["발생시간"]
done_col  = time_cols["조치완료"]

# 6-1) Analysis Filters (Ho + Date)
st.markdown("### 호기 설정 및 기간 선택")

col_ho, col_date = st.columns([1.5, 1])

with col_ho:
    ho_list = sorted(df_site["호기"].dropna().unique())
    selected_hos = st.multiselect(
        "호기 선택",
        ho_list,
    )

with col_date:
    min_date = df_site[occur_col].min().date()
    max_date = df_site[occur_col].max().date()

    start_date, end_date = st.date_input(
        "Date Range (Occurrence)",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

# 6-2) 선택 필터 적용 (Ho + Date)  ✅ 이 블록을 agg 만들기 전에 추가하세요
df_f = df_site.copy()

# (1) 호기 필터: 아무것도 선택 안 했으면 전체 유지
if selected_hos:
    df_f = df_f[df_f["호기"].isin(selected_hos)]

# (2) 날짜 필터 (발생시간 기준)
df_f = df_f[
    (df_f[occur_col].dt.date >= start_date) &
    (df_f[occur_col].dt.date <= end_date)
].reset_index(drop=True)

if df_f.empty:
    st.warning("선택한 호기/기간 조건에 해당하는 데이터가 없습니다.")
    st.stop()

df_f["소요시간"] = df_f[done_col] - df_f[occur_col]

agg = (
    df_f
    .groupby(["Machine", "Unit", "Assy'", "호기"])
    .agg(
        횟수=("소요시간", "size"),
        총소요시간=("소요시간", "sum")
    )
    .reset_index()
)
agg["총소요_초"] = agg["총소요시간"].dt.total_seconds() / 60

# — (1) 발생횟수 피벗 & AgGrid
cnt_pivot = (
    agg
    .pivot_table(
        index=["Machine", "Unit", "Assy'"],
        columns="호기",
        values="횟수",
        fill_value=0
    )
    .reset_index()
)
st.subheader("Machine/Unit/Assy' 별 호기별 발생횟수")

js_cnt_style = JsCode("""
function(params) {
  if (params.value == null || params.value === 0) {
    return {};
  }

  const v = params.value;

  if (v >= 50) {
    return { color: 'white', backgroundColor: '#7f2704' };   // 매우 진한 오렌지
  } else if (v >= 30) {
    return { color: 'white', backgroundColor: '#a63603' };
  } else if (v >= 20) {
    return { color: 'white', backgroundColor: '#d94801' };
  } else if (v >= 10) {
    return { backgroundColor: '#f16913' };
  } else if (v >= 5) {
    return { backgroundColor: '#fdae6b' };
  } else if (v >= 1) {
    return { backgroundColor: '#fee6ce' };   // 아주 연한 오렌지
  }
}
""")

gb_cnt = GridOptionsBuilder.from_dataframe(cnt_pivot)
gb_cnt.configure_selection("single")
for c in cnt_pivot.columns:
    if c not in ["Machine", "Unit", "Assy'"]:
        gb_cnt.configure_column(c, cellStyle=js_cnt_style)
grid_opts_cnt = gb_cnt.build()

grid_cnt = AgGrid(
    cnt_pivot,
    gridOptions=grid_opts_cnt,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    fit_columns_on_grid_load=True,
    enable_enterprise_modules=False,
    allow_unsafe_jscode=True
)

# 선택된 행이 있는지 안전하게 검사
sel_rows = grid_cnt.get("selected_rows", [])

# sel_rows = grid_cnt.get("selected_rows", []) or []

if isinstance(sel_rows, pd.DataFrame):
    sel_rows = sel_rows.to_dict("records")

if sel_rows is None:
    sel_rows = []
elif len(sel_rows) > 0:

    sel = sel_rows[0]
    m, u, a = sel["Machine"], sel["Unit"], sel["Assy'"]
    detail_cnt = df_f[
        (df_f["Machine"] == m) &
        (df_f["Unit"]    == u) &
        (df_f["Assy'"]   == a)
    ]
    with st.expander(f"[{m} / {u} / {a}] 발생횟수 상세 목록", expanded=True):
        st.dataframe(detail_cnt, use_container_width=True)

# — (2) 총 소요시간(초) 피벗 & AgGrid
time_pivot = (
    agg
    .pivot_table(
        index=["Machine", "Unit", "Assy'"],
        columns="호기",
        values="총소요_초",
        fill_value=0
    )
    .reset_index()
)

st.subheader("Machine/Unit/Assy' 별 호기별 총 소요시간 (분)")

js_time_style = JsCode("""
function(params) {
  if (params.value == null || params.value === 0) {
    return {};
  }

  const v = params.value;

  if (v >= 500) {
    return { color: 'white', backgroundColor: '#08306b' };
  } else if (v >= 400) {
    return { color: 'white', backgroundColor: '#08519c' };
  } else if (v >= 300) {
    return { color: 'white', backgroundColor: '#2171b5' };
  } else if (v >= 200) {
    return { backgroundColor: '#6baed6' };
  } else if (v >= 100) {
    return { backgroundColor: '#c6dbef' };
  }
}
""")

gb_time = GridOptionsBuilder.from_dataframe(time_pivot)
gb_time.configure_selection("single")
for c in time_pivot.columns:
    if c not in ["Machine", "Unit", "Assy'"]:
        gb_time.configure_column(c, cellStyle=js_time_style)
grid_opts_time = gb_time.build()

grid_time = AgGrid(
    time_pivot,
    gridOptions=grid_opts_time,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    fit_columns_on_grid_load=True,
    enable_enterprise_modules=False,
    allow_unsafe_jscode=True
)

sel_time = grid_time.get("selected_rows", [])

# sel_time = grid_time.get("selected_rows", []) or []

if isinstance(sel_time, pd.DataFrame):
    sel_time = sel_time.to_dict("records")

if sel_time is None:
    sel_time = []
elif len(sel_time) > 0:
    sel2 = sel_time[0]
    m2, u2, a2 = sel2["Machine"], sel2["Unit"], sel2["Assy'"]
    detail_time = df_f[
        (df_f["Machine"] == m2) &
        (df_f["Unit"]    == u2) &
        (df_f["Assy'"]   == a2)
    ]
    with st.expander(f"[{m2} / {u2} / {a2}] 총 소요시간 상세 목록", expanded=True):
        st.dataframe(detail_time, use_container_width=True)

# — 이후 기존 호기별 Top5 분석 및 트렌드 차트 코드를 이어 붙이세요. —
