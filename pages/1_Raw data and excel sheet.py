import io
import pandas as pd
import streamlit as st
from datetime import date
import openpyxl

# from options import KIND_OPTIONS, SITE_OPTIONS, PROCESS_OPTIONS, UNIT_OPTIONS
# from load_data import load_sheet_data

from utils import KIND_OPTIONS, SITE_OPTIONS, PROCESS_OPTIONS, UNIT_OPTIONS
from utils import load_sheet_data

# — Streamlit UI
st.set_page_config(page_title="부동내역 필터링", layout="wide")
st.title("📋 부동내역 필터링 및 다운로드")

# 데이터 로드
df, error = load_sheet_data()
if error:
    st.error(error)
    st.stop()

# '발생일' 컬럼 추가
df['발생일'] = df['발생시간'].dt.date

# 결측치 제거 후 최대/최소 발생일 계산
valid_dates = df['발생일'].dropna()
day_min, day_max = valid_dates.min(), valid_dates.max()

filter_col, table_col = st.columns([1, 3])
with filter_col:
    # 초기화 버튼
    if st.button("초기화"):
        for key, default in {
            'kind_filter': '-',
            'site_filter': '-',
            'machine_num_filter': '-',
            'machine_filter': '-',
            'unit_filter': '-',
            'assy_filter': '-',
            'date_range': (day_min, day_max)
        }.items():
            st.session_state[key] = default

    # 필터 위젯 설정
    kind = st.selectbox('종류', ['-'] + [k for k in KIND_OPTIONS if k != '-'], key='kind_filter')
    site = st.selectbox('Site', ['-'] + list(SITE_OPTIONS.keys()), key='site_filter')
    호기_choices = SITE_OPTIONS.get(site, []) if site != '-' else []
    machine_num = st.selectbox('호기', ['-'] + [c for c in 호기_choices if c != '-'], key='machine_num_filter')
    machine = st.selectbox('Machine', ['-'] + [m for m in PROCESS_OPTIONS.keys() if m != '-'], key='machine_filter')
    unit_opts = PROCESS_OPTIONS.get(machine, []) if machine != '-' else []
    unit = st.selectbox('Unit', ['-'] + [u for u in unit_opts if u != '-'], key='unit_filter')
    assy_opts = UNIT_OPTIONS.get(unit, []) if unit != '-' else []
    assy = st.selectbox("Assy'", ['-'] + [a for a in assy_opts if a != '-'], key='assy_filter')

    # 발생일 범위 선택
    start_date, end_date = st.date_input(
        '발생일 범위 선택',
        value=st.session_state.get('date_range', (day_min, day_max)),
        min_value=day_min,
        max_value=day_max,
        key='date_range',
        help='시작일과 종료일을 선택하세요'
    )

    # 필터링 적용
    tmp = df[(df['발생일'] >= start_date) & (df['발생일'] <= end_date)].copy()
    if kind        != '-': tmp = tmp[tmp['종류']   == kind]
    if site        != '-': tmp = tmp[tmp['Site']    == site]
    if machine_num != '-': tmp = tmp[tmp['호기']    == machine_num]
    if machine     != '-': tmp = tmp[tmp['Machine'] == machine]
    if unit        != '-': tmp = tmp[tmp['Unit']    == unit]
    if assy        != '-': tmp = tmp[tmp["Assy'"]  == assy]

    filtered = tmp.reset_index(drop=True)

with table_col:
    st.success(f"✅ {len(filtered)}개 행 표시")
    display_cols = [
        '발생일','발생시간','조치완료시간','조치 진행 시간(분)',
        '종류','Site','호기','Machine','Unit',"Assy'",
        '작업자','현상','원인','조치'
    ]
    disp = filtered[display_cols].reset_index(drop=True)
    disp.index = [''] * len(disp)

    # 데이터프레임 표시
    st.dataframe(disp, use_container_width=True)

    # raw 데이터 다운로드 함수
    def to_excel_bytes(df: pd.DataFrame) -> bytes:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='raw_data')
        return buf.getvalue()

    # raw 데이터 다운로드 버튼
    st.download_button(
        key='download_raw',
        label='📥 raw 데이터 엑셀 다운로드',
        data=to_excel_bytes(filtered),
        file_name='filtered_trouble_sheet.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    # 템플릿에 적용된 엑셀 다운로드 함수
    def to_excel_template(df: pd.DataFrame) -> bytes:
        from openpyxl import load_workbook
        buf = io.BytesIO()
        wb = load_workbook('template.xlsx')
        sheet_name = wb.sheetnames[0]
        ws = wb[sheet_name]
        ws.delete_rows(1, ws.max_row)
        ws.append(list(df.columns))
        for row in df.itertuples(index=False):
            ws.append(list(row))
        wb.save(buf)
        return buf.getvalue()

    # 템플릿 적용 다운로드 버튼
    st.download_button(
        key='download_template',
        label='📥 템플릿에 적용된 엑셀 다운로드',
        data=to_excel_template(filtered),
        file_name='filled_template.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
