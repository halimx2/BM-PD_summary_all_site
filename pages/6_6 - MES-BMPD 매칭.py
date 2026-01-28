import io
import re
import pandas as pd
import streamlit as st
from datetime import datetime, date, time, timedelta

from utils import KIND_OPTIONS, SITE_OPTIONS, PROCESS_OPTIONS, UNIT_OPTIONS, load_sheet_data

from bmpd_to_mes import df_clean_korean, run_matching_reverse, show_alarm_catalog_and_detail, read_excel_safely, merge_uploaded_excels

import pandas as pd
import streamlit as st

st.set_page_config(page_title="BMPD ↔ MES 매칭", layout="wide")
st.title("📊 BMPD ↔ MES 매칭")

st.subheader("1️⃣ BMPD 데이터 불러오기")
try:
    from utils import load_sheet_data
    df_bmpd, error = load_sheet_data()
    if error:
        st.error(error)
        df_bmpd = pd.DataFrame()
    else:
        st.success(f"BMPD 불러오기 완료: {len(df_bmpd):,}행")
        st.dataframe(df_bmpd.head(5), use_container_width=True)
except Exception as e:
    st.error(f"BMPD 로딩 오류: {e}")
    df_bmpd = pd.DataFrame()

st.subheader("2️⃣ MES 알람 데이터 업로드")

with st.expander("📥 MES 파일 업로드", expanded=True):
    up_mes = st.file_uploader("MES 엑셀 파일 (.xlsx)", type=["xlsx"], key="lami_uploader", accept_multiple_files=True)
    # df_mes, sheet_mes = read_excel_safely(up_mes)
    df_mes = merge_uploaded_excels(up_mes)
    if up_mes is not None:
        # 여러 시트가 있으면 선택 제공
        # if sheet_mes and len(sheet_mes) > 1:
        #     sheet_mes_sel = st.selectbox("Lami 시트 선택", sheet_mes, key="sheet_mes_sel")
        #     df_mes = pd.read_excel(up_mes, sheet_name=sheet_mes_sel)
        #     st.caption(f"선택된 시트: {sheet_mes_sel}")
        st.success(f"Lami MES 로딩 완료: {len(df_mes):,}행")
        st.dataframe(df_mes.head(5), use_container_width=True)
    else:
        st.info("Lami 파일을 업로드해 주세요.")


st.divider()
st.markdown("### ✅ 현재 상태 요약")

bmpd_ok = len(df_bmpd) > 0
mes_ok = up_mes is not None and len(df_mes) > 0

st.write(
    f"- BMPD: {'✅ 로드됨' if bmpd_ok else '❌ 미로드'}"
    f"\n- MES: {'✅ 업로드됨' if mes_ok else '❌ 미업로드'}"
)

if len(df_bmpd) == 0 or len(df_mes) == 0 :
    st.warning("BMPD, MES 파일을 모두 업로드해야 매칭이 가능합니다.")
    final_matched_mes_data = pd.DataFrame()  # 빈 데이터프레임으로 초기화
else:
    df_mes = df_clean_korean(df_mes)
    final_matched_mes_data = run_matching_reverse(
        df_BMPD=df_bmpd,
        df_MES=df_mes,
    )

# '매칭된_BMPD' 컬럼의 리스트 길이가 0보다 큰 행, 즉 매칭이 성공한 행만 선택
if "매칭된_BMPD" in final_matched_mes_data.columns:
    df_matched_only_ = final_matched_mes_data[final_matched_mes_data['매칭된_BMPD'].str.len() > 0].copy()
else:
    df_matched_only_ = pd.DataFrame()

# 아래쪽 코드(예: show_alarm_catalog_and_detail)도 조건문으로 감싸기
if len(df_bmpd) > 0 and len(df_mes) > 0 :
    # show_alarm_catalog_and_detail(df_matched_only_)
    show_alarm_catalog_and_detail(final_matched_mes_data)

else:
    st.info("모든 파일이 업로드되어야 알람 상세 데이터를 볼 수 있습니다.")
