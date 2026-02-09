import pandas as pd
import re
import streamlit as st

import io
import re
from datetime import datetime, date, time, timedelta

import streamlit as st

def df_clean_korean(df_, threshold_length=10) :
    """
    한글 '알람 명' 컬럼을 기준으로 전처리를 수행하고, 
    지정된 길이(threshold_length) 미만의 행을 제거하는 함수입니다.
    """
    # 1. 대상 컬럼 확인 및 복사
    TARGET_COL = '알람 명'
    CLEAN_COL = '알람 명_cleaned'
    
    if TARGET_COL not in df_.columns:
        print(f"오류: 데이터프레임에 '{TARGET_COL}' 컬럼이 없습니다.")
        return df_

    df_[CLEAN_COL] = df_[TARGET_COL].astype(str).copy()

    # 2. [~~~] 괄호 안 내용 및 공백 제거
    df_[CLEAN_COL] = df_[CLEAN_COL].str.replace(r'\[F.*?\]\s*', '', regex=True)

    # 3. 선행 공백 및 후행 공백 제거 (가장 강력한 strip)
    df_[CLEAN_COL] = df_[CLEAN_COL].str.strip()
    df_[CLEAN_COL] = df_[CLEAN_COL].str.replace(r'^\s*', '', regex=True)
    df_[CLEAN_COL] = df_[CLEAN_COL].str.lower()
    
    df_filtered_ = df_[~df_[CLEAN_COL].str.contains('스페어|도어|문|Cell Tracking|만재|Door|Open|경고', case=False, na=False, regex=True)].copy()

    # 5. 길이 계산 로직 추가 (필수)
    df_filtered_['text_length'] = df_[CLEAN_COL].str.len()
    
    # 6. 길이 필터링
    df_filtered_ = df_filtered_[df_filtered_['text_length'] >= threshold_length].copy()
    
    # print(f"--- 전처리 결과 요약 ---")
    # print(f"원본 데이터 개수: {len(df_)} 행")
    # print(f"길이 {threshold_length} 미만 제거 후 남은 데이터 개수: {len(df_filtered_)} 행\n")
    
    return df_filtered_


import pandas as pd
import re
from typing import List, Dict, Any


def extract_process_lastword(equip_name: str) -> str:
    """MES 설비명에서 공정 키워드를 추출하여 반환합니다."""
    if not isinstance(equip_name, str):
        return "__fail__"
        
    s = equip_name.strip().lower()
    toks = s.split()
    
    if not s or len(toks) < 2:
        return "__fail__"

    raw_process = toks[1]
    
    # ['Electrode Supply', 'Lamination', 'D-Stacking', 'Taper', 'Inspection']
    if 'supply' in raw_process or 'electrode' in raw_process:
        return 'electrode supply'
    elif 'lam' in raw_process or 'lam' in toks[0]:
        return 'lamination'
    elif 'd-stacking' in raw_process:
        return 'd-stacking'
    elif 'taper' in raw_process:
        return 'taper'
    elif 'inspection' in raw_process:
        return 'inspection'

    return 'undecided(stk)'


def extract_line_from_text(equip_name: str) -> str:
    """설비명에서 '#숫자-숫자' 패턴을 추출하고, 뒷자리의 0을 제거"""
    if not isinstance(equip_name, str):
        return "__fail__"

    m = re.search(r"#\d+-\d+", equip_name)
    if not m:
        return "__fail__"

    line = m.group(0)      # 예: "#26-05"
    left, right = line.split("-")  # left="#26", right="05"
    # 숫자로 변환 후 다시 문자열로 바꿔 앞자리 0 제거 → "5"
    right = str(int(right))        
    
    return f"{left}-{right}"



def reduce_matches(row: pd.Series,
                   list_col: str = "매칭목록",
                   bmpd_machine_col: str = "Machine",
                   bmpd_line_col: str = "호기"):
    """
    호기 및 공정이 일치하고, Door 관련 및 너무 짧은 텍스트 알람을 제외하여
    매칭된 알람 목록을 필터링합니다.
    """
    items = row.get(list_col, []) or []
    if not items:
        return []

    target_process = str(row.get(bmpd_machine_col, "")).strip().lower()
    target_line    = str(row.get(bmpd_line_col, "")).strip()

    KEEP = {"설비명", "발생일시", "해제일시", "경과(초)", "알람 명"}

    kept = []
    for item in items:
        # 1) MES 설비명에서 공정 및 호기 추출
        process = extract_process_lastword(item.get("설비명"))
        line = extract_line_from_text(item.get("설비명"))

        if (process == target_process and line == target_line):
            
            slim = {k: item.get(k) for k in KEEP}
            kept.append(slim)
            
    return kept


import pandas as pd
import re
from typing import List, Dict, Any

# ==========================================================
# 1. 유틸리티 함수
# ==========================================================

def extract_line_from_text(equip_name: str) -> str:
    """설비명에서 '#숫자-숫자' 패턴을 추출하고, 뒷자리의 0을 제거"""
    if not isinstance(equip_name, str):
        return "__fail__"

    m = re.search(r"#\d+-\d+", equip_name)
    if not m:
        return "__fail__"

    line = m.group(0)      
    left, right = line.split("-")
    right = str(int(right))
    
    return f"{left}-{right}"

def extract_process_lastword(equip_name: str) -> str:
    """MES 설비명에서 공정 키워드를 추출하여 반환합니다."""
    # BMPD의 Machine 컬럼 (D-Stacking, Taper, Lamination 등)과 비교하기 위해 소문자 정규화된 키워드를 반환합니다.
    if not isinstance(equip_name, str): return "__fail__"
    s = equip_name.strip().lower()
    toks = s.split()
    if not s or len(toks) < 2: return 'undecided(stk)' # STK/LAMI 분류 전이므로 undecided는 STK로 가정

    raw_process = toks[1]
    
    # BMPD의 'Machine' 컬럼 값과 비교할 수 있도록 소문자로 통일
    if 'supply' in raw_process or 'electrode' in raw_process: return 'electrode supply'
    elif 'lam' in raw_process or 'lam' in toks[0]: return 'lamination'
    elif 'd-stacking' in raw_process: return 'd-stacking'
    elif 'taper' in raw_process: return 'taper'
    elif 'inspection' in raw_process: return 'inspection'
    
    return 'undecided(stk)'


# ==========================================================
# 2. 핵심 매칭 함수 (공정 매칭 조건 추가)
# ==========================================================

def collect_window_mes_to_bmpd(mes: pd.DataFrame, bmpd: pd.DataFrame, out_col: str = "매칭된_BMPD"):
    """
    MES 알람과 BMPD 조치의 호기, 날짜, 시간 윈도우, **공정**이 모두 일치하는 이력을 매칭합니다.
    """
    tol = pd.Timedelta("10min")
    # tol = pd.Timedelta("20min")
    KEEP = ["호기", "Machine", "Unit", "Assy\'", "발생시간", "조치완료", "현상", "원인", "조치"]
    
    mes_time = "발생일시"
    mes_time_end = "해제일시"
    bmpd_start_time = "발생시간"
    bmpd_end_time = "조치완료"
    mes_process_col = '__process_group'

    mes = mes.copy()
    bmpd = bmpd.copy()

    # 💡 [공정 키 생성]: BMPD Machine 컬럼을 소문자로 정규화
    bmpd['Machine_lower'] = bmpd['Machine'].astype(str).str.lower()
    
    # 💡 [호기 키 생성]: 호기 키 통일 및 생성
    mes["__line_key"] = mes["설비명"].apply(extract_line_from_text).str.replace('-', '').replace('_', '')
    # mes["__line_key"] = mes["설비명"].apply(extract_line_from_text).str.replace('#', '').str.replace('-', '').replace('_', '')
    bmpd["__line_key"] = bmpd["호기"].astype(str).str.strip().str.replace('-', '').replace('_', '')

    # 날짜 키 생성
    mes["_key"]    = range(len(mes))
    mes["__date"]  = mes[mes_time].dt.date 
    bmpd["__date"] = bmpd[bmpd_start_time].dt.date 

    # 1단계: 날짜 및 호기 키를 이용한 1차 조인
    tmp = mes.merge(bmpd, on=["__date", "__line_key"], how="left", suffixes=('_mes', '_bmpd')) 
    
    # NULL 값 제거 (KeyError 해결: '발생시간_bmpd' 대신 '발생시간' 사용)
    df_merged_non_nan_ = tmp[tmp['발생시간'].notna()].copy() 
    
    # 2단계: 필터링 마스크 생성 및 적용
    
    # 조건 1: 시간 윈도우 (T_BMPD <= T_MES <= T_BMPD + 10분)
    is_start_close_to_start = (df_merged_non_nan_[bmpd_start_time] <= df_merged_non_nan_[mes_time]) & \
                              (df_merged_non_nan_[mes_time] <= df_merged_non_nan_[bmpd_start_time] + tol) & \
                              (df_merged_non_nan_[mes_time] <= df_merged_non_nan_[bmpd_end_time])
    is_end_close_to_end = (df_merged_non_nan_[bmpd_end_time] - tol <= df_merged_non_nan_[mes_time_end]) & \
                          (df_merged_non_nan_[mes_time_end] <= df_merged_non_nan_[bmpd_end_time] + tol)

    # 조건 2: 공정 매칭
    is_process_match = (df_merged_non_nan_[mes_process_col] == df_merged_non_nan_['Machine_lower'])

    # 세 조건을 모두 만족하는 행만 선택
    df_filtered_ = df_merged_non_nan_[is_start_close_to_start & is_end_close_to_end & is_process_match].copy()
    
    # 💡 [ValueError 해결]: 매칭된 행이 없을 경우 예외 처리
    if len(df_filtered_) == 0:
        mes[out_col] = [[]] * len(mes)
        return mes.drop(columns=["_key", "__date", "__line_key", mes_process_col], errors="ignore")


    # 원하는 열만 dict 리스트로 그룹화
    take = [c for c in KEEP if c in df_filtered_.columns]
    grouped = (df_filtered_.groupby("_key")[take].apply(lambda g: g.to_dict("records")))

    # 매칭 없으면 [] 로 처리 (NaN은 빈 리스트로 변환)
    s = mes["_key"].map(grouped)
    mes[out_col] = s.apply(lambda v: v if isinstance(v, list) else [])

    # 임시 컬럼 제거 후 반환
    return mes.drop(columns=["_key", "__date", "__line_key", mes_process_col], errors="ignore")

# ==========================================================
# 3. 실행 함수 (extract_process_lastword 활용)
# ==========================================================

def run_matching_reverse(df_BMPD: pd.DataFrame, df_MES: pd.DataFrame) -> pd.DataFrame:
    # 1. 시간 변환 (해제일시 변환 포함)
    df_BMPD["발생시간"] = pd.to_datetime(df_BMPD["발생시간"], errors="coerce")
    df_BMPD["조치완료"] = pd.to_datetime(df_BMPD["조치완료"], errors="coerce")
    # df_BMPD["조치완료"] = pd.to_datetime(df_BMPD["조치완료"], errors="coerce")

    df_MES["발생일시"] = pd.to_datetime(df_MES["발생일시"], errors="coerce")
    df_MES["해제일시"] = pd.to_datetime(df_MES["해제일시"], errors="coerce")

    # 2. 공정 분류
    df_MES['__process_group'] = df_MES['설비명'].apply(extract_process_lastword)

    # 3. 매칭 수행 (공정별로 세분화하여 매칭하고 결과를 리스트에 저장)
    results = []
    for process in df_MES['__process_group'].unique():
        df_sub_mes_ = df_MES[df_MES['__process_group'] == process].copy()
        res_sub_mes_ = collect_window_mes_to_bmpd(df_sub_mes_, df_BMPD, out_col="매칭된_BMPD")
        results.append(res_sub_mes_)

    # 4. 합치기
    if not results:
        return pd.DataFrame()
    df_result_ = pd.concat(results, ignore_index=True)
    df_result_ = df_result_.drop(columns=['__process_group'], errors='ignore')
    return df_result_



def _parse_cands(cell):
    """매칭된_BMPD 셀(리스트/문자열/None)을 안전하게 [dict, ...]로 변환"""
    if cell is None:
        return []
    if isinstance(cell, str):
        try:
            cell = ast.literal_eval(cell)
        except Exception:
            return []
    if not isinstance(cell, (list, tuple)):
        cell = [cell]
    out = []
    for it in cell:
        if isinstance(it, dict):
            d = it.copy()
        elif isinstance(it, (list, tuple)) and it:
            d = {"BMPD_ID": it[0]}
            if len(it) > 1 and isinstance(it[1], dict):
                d.update(it[1])
        else:
            d = {"raw": str(it)}

        # 키 보정(있으면 그대로, 없으면 대체)
        d.setdefault("BMPD_ID", d.get("bmpd_id") or d.get("id") or d.get("row_idx") or "")
        d.setdefault("현상", d.get("현상") or d.get("symptom") or "")
        d.setdefault("원인", d.get("원인") or d.get("cause") or "")
        d.setdefault("조치", d.get("조치") or d.get("action") or "")
        d.setdefault("발생시간", d.get("조치") or d.get("action") or "")
        d.setdefault("조치완료", d.get("조치") or d.get("action") or "")
        # d.setdefault("Δt(분)", d.get("delta_min") or d.get("dt_min") or d.get("Δt") or "")
        d.setdefault("점수", d.get("score") or d.get("bm25") or d.get("점수") or "")
        out.append(d)

    return out


def show_alarm_catalog_and_detail(df_all: pd.DataFrame):
    # 필수 컬럼 체크(없는 건 빈 컬럼으로 만들어서 화면만 보이도록)
    need_cols = ["알람 명","설비명","설비 ID","발생일시","해제일시","경과(초)","매칭된_BMPD"]
    df = df_all.copy()
    for c in need_cols:
        if c not in df.columns:
            df[c] = pd.NA

    # 타입 정리
    if "발생일시" in df.columns:
        df["발생일시"] = pd.to_datetime(df["발생일시"], errors="coerce")
    if "해제일시" in df.columns:
        df["해제일시"] = pd.to_datetime(df["해제일시"], errors="coerce")

    st.subheader("알람명별 발생 빈도")
    freq = (
        df.groupby("알람 명", dropna=False)
          .size()
          .reset_index(name="발생 횟수")
          .sort_values("발생 횟수", ascending=False)
    )

    bmpd_count = (
        df.groupby("알람 명")["매칭된_BMPD"]
        .apply(lambda x: sum([len(i) if isinstance(i, list) else 0 for i in x]))
        .reset_index(name="매칭된 BMPD 수")
    )

    freq = freq.merge(bmpd_count, on="알람 명", how="left")

    if freq.empty:
        st.info("표시할 알람 데이터가 없습니다.")
        return

    col_top, col_tbl = st.columns([1, 2])
    with col_top:
        top_n = st.slider("상위 N", 5, max(5, min(50, len(freq))), min(20, len(freq)), 5)
    with col_tbl:
        st.dataframe(freq.head(top_n), use_container_width=True, hide_index=True)

    # 선택 박스(카탈로그 → 상세)
    alarm_sel = st.selectbox("확인할 알람명을 선택", options=freq["알람 명"].tolist())
    st.divider()

    st.subheader(f"알람명: {alarm_sel}")
    df_alarm = df[df["알람 명"] == alarm_sel].copy().sort_values("발생일시")

    left, right = st.columns([1, 2], gap="large")

    # 좌측 요약 패널
    with left:
        st.markdown("#### 요약")
        st.metric("총 발생 횟수", f"{len(df_alarm):,}")
        if "경과(초)" in df_alarm.columns and not df_alarm["경과(초)"].isna().all():
            st.metric("평균 경과(초)", f"{pd.to_numeric(df_alarm['경과(초)'], errors='coerce').mean():.1f}")
            st.metric("최장 경과(초)", f"{pd.to_numeric(df_alarm['경과(초)'], errors='coerce').max():.0f}")

        st.markdown("##### 설비 분포")
        eqp = (
            df_alarm.groupby(["설비명","설비 ID"], dropna=False)
                    .size().reset_index(name="건수")
                    .sort_values("건수", ascending=False)
        )
        st.dataframe(eqp.head(20), use_container_width=True, hide_index=True)

    # 우측 사례 리스트(각 행 + 매칭된 BMPD 후보들)
    with right:
        st.markdown("#### 사례 목록")
        # 간단 필터(설비명)
        eqp_list = ["(전체)"] + sorted(df_alarm["설비명"].dropna().astype(str).unique().tolist())
        eqp_sel = st.selectbox("설비명 필터", eqp_list, index=0)

        bmpd_filter = st.checkbox("매칭된 BMPD가 1개 이상인 것만 보기", value=False)
        df_show = df_alarm if eqp_sel == "(전체)" else df_alarm[df_alarm["설비명"].astype(str) == eqp_sel]

        if bmpd_filter:
            df_show = df_show[df_show["매칭된_BMPD"].astype(bool)]

        for i, row in df_show.reset_index(drop=True).iterrows():
            title = f"[{row.get('설비명','')}] {row.get('발생일시','')} → {row.get('해제일시','')}, {row.get('경과(초)','')}초"
            with st.expander(title, expanded=False):
                st.write("**기본 정보**")
                st.write({
                    "설비명": row.get("설비명",""),
                    "설비 ID": row.get("설비 ID",""),
                    "발생일시": row.get("발생일시",""),
                    "해제일시": row.get("해제일시",""),
                    "경과(초)": row.get("경과(초)",""),
                    "설비상태": row.get("설비상태",""),
                    "알람코드": row.get("알람코드",""),
                    "알람 명": row.get("알람 명",""),
                })

                cands = _parse_cands(row.get("매칭된_BMPD"))
                if not cands:
                    st.info("매칭된 BMPD 없음")
                else:
                    for j, d in enumerate(cands, start=1):
                        st.markdown(f"**매칭 후보 #{j} — {d.get('BMPD_ID','')}**")
                        st.write({
                            "호기": d.get("호기",""),
                            "Machine": d.get("Machine",""),
                            "Assy'": d.get("Assy'",""),
                            "현상": d.get("현상",""),
                            "원인": d.get("원인",""),
                            "조치": d.get("조치",""),
                            "발생시간": d.get("발생시간",""),
                            "조치완료": d.get("조치완료",""),
                            # "Δt(분)": d.get("Δt(분)",""),
                            # "점수": d.get("점수",""),
                        })
                        st.markdown("---")


def read_excel_safely(file, sheet_name=None):
    """
    - sheet_name 지정 없으면 첫 번째 시트 로딩
    - 파일이 None이면 빈 DF 반환
    """
    if file is None:
        return pd.DataFrame(), None
    xls = pd.ExcelFile(file)
    sheets = xls.sheet_names
    if sheet_name is None:
        sheet_name = sheets[0]
    df = pd.read_excel(file, sheet_name=sheet_name)
    return df, sheets



def merge_uploaded_excels(uploaded_files):
   """
   Streamlit에서 여러 Excel/CSV 파일이 업로드된 경우
   동일한 형식(컬럼 구조)이라고 가정하고 하나의 DataFrame으로 병합
   """
   dfs = []
   for f in uploaded_files:
       # 파일 확장자 판별
       name = f.name.lower()
       try:
           if name.endswith(".csv"):
               df = pd.read_csv(f, encoding="utf-8", errors="ignore")
           elif name.endswith((".xls", ".xlsx")):
               df = pd.read_excel(f)
           else:
               print(f"⚠️ 지원하지 않는 파일 형식: {f.name}")
               continue
           # 컬럼 공백 제거
           df.columns = df.columns.str.strip()
           # 원본 파일명 보존 (옵션)
           df["__source_file"] = f.name
           dfs.append(df)
       except Exception as e:
           print(f"❌ {f.name} 읽기 실패: {e}")
   if not dfs:
       print("❌ 병합할 데이터가 없습니다.")
       return pd.DataFrame()
   # 동일한 컬럼 구조로 병합
   merged_df = pd.concat(dfs, ignore_index=True)
   # dtype 자동 정리
   merged_df = merged_df.convert_dtypes()
#    print(f"✅ 총 {len(uploaded_files)}개 파일 병합 완료, 행 수: {len(merged_df)}")
   return merged_df


import ast
import pandas as pd
import streamlit as st
from datetime import timedelta

def show_alarm_catalog_and_detail_time_series(df_all: pd.DataFrame, df_bmpd: pd.DataFrame | None = None):
    # 필수 컬럼 체크(없는 건 빈 컬럼으로 만들어서 화면만 보이도록)
    need_cols = ["알람 명","설비명","설비 ID","발생일시","해제일시","경과(초)","매칭된_BMPD"]
    df = df_all.copy()
    for c in need_cols:
        if c not in df.columns:
            df[c] = pd.NA

    # 타입 정리
    df["발생일시"] = pd.to_datetime(df["발생일시"], errors="coerce")
    df["해제일시"] = pd.to_datetime(df["해제일시"], errors="coerce")

    # BMPD도 들어오면 시간 타입 정리
    if df_bmpd is not None and len(df_bmpd) > 0:
        if "발생시간" in df_bmpd.columns:
            df_bmpd = df_bmpd.copy()
            df_bmpd["발생시간"] = pd.to_datetime(df_bmpd["발생시간"], errors="coerce")
        if "조치완료" in df_bmpd.columns:
            df_bmpd["조치완료"] = pd.to_datetime(df_bmpd["조치완료"], errors="coerce")

    st.subheader("알람명별 발생 빈도")
    freq = (
        df.groupby("알람 명", dropna=False)
          .size()
          .reset_index(name="발생 횟수")
          .sort_values("발생 횟수", ascending=False)
    )

    bmpd_count = (
        df.groupby("알람 명")["매칭된_BMPD"]
        .apply(lambda x: sum([len(i) if isinstance(i, list) else 0 for i in x]))
        .reset_index(name="매칭된 BMPD 수")
    )
    freq = freq.merge(bmpd_count, on="알람 명", how="left")

    if freq.empty:
        st.info("표시할 알람 데이터가 없습니다.")
        return

    col_top, col_tbl = st.columns([1, 2])
    with col_top:
        top_n = st.slider("상위 N", 5, max(5, min(50, len(freq))), min(20, len(freq)), 5)
    with col_tbl:
        st.dataframe(freq.head(top_n), use_container_width=True, hide_index=True)

    # 선택 박스(카탈로그 → 상세)
    alarm_sel = st.selectbox("확인할 알람명을 선택", options=freq["알람 명"].tolist())
    st.divider()

    st.subheader(f"알람명: {alarm_sel}")
    df_alarm = df[df["알람 명"] == alarm_sel].copy().sort_values("발생일시")

    left, right = st.columns([1, 2], gap="large")

    # # 좌측 요약 패널
    # with left:
    #     st.markdown("#### 요약")
    #     st.metric("총 발생 횟수", f"{len(df_alarm):,}")
    #     if "경과(초)" in df_alarm.columns and not df_alarm["경과(초)"].isna().all():
    #         st.metric("평균 경과(초)", f"{pd.to_numeric(df_alarm['경과(초)'], errors='coerce').mean():.1f}")
    #         st.metric("최장 경과(초)", f"{pd.to_numeric(df_alarm['경과(초)'], errors='coerce').max():.0f}")

    #     st.markdown("##### 설비 분포")
    #     eqp = (
    #         df_alarm.groupby(["설비명","설비 ID"], dropna=False)
    #                 .size().reset_index(name="건수")
    #                 .sort_values("건수", ascending=False)
    #     )
    #     st.dataframe(eqp.head(20), use_container_width=True, hide_index=True)

    # ----------------------------
    # 내부 유틸(기존 _parse_cands 그대로 사용 가능)
    # ----------------------------
    def _parse_cands(cell):
        if cell is None:
            return []
        if isinstance(cell, str):
            try:
                cell = ast.literal_eval(cell)
            except Exception:
                return []
        if not isinstance(cell, (list, tuple)):
            cell = [cell]
        out = []
        for it in cell:
            if isinstance(it, dict):
                d = it.copy()
            else:
                d = {"raw": str(it)}
            # 키 보정
            d.setdefault("BMPD_ID", d.get("bmpd_id") or d.get("id") or d.get("row_idx") or "")
            out.append(d)
        return out

    # ----------------------------
    # 윈도우 출력 함수들(핵심)
    # ----------------------------
    def _extract_line_key_from_mes_eqp(eqp_name: str) -> str:
        # 이미 하림님 코드에 extract_line_from_text가 있으니 그걸 쓰는 게 제일 좋음
        # 여기선 안전하게 try로 감쌈
        try:
            return extract_line_from_text(eqp_name)  # "#26-5" 형태 기대
        except Exception:
            return "__fail__"

    def _linekey_norm(s: str) -> str:
        if not isinstance(s, str):
            return "__fail__"
        return s.strip().replace("-", "").replace("_", "").replace("#", "")

    def _mes_window(df_src: pd.DataFrame, line_key: str, t0: pd.Timestamp, minutes=20):
        if pd.isna(t0):
            return pd.DataFrame()
        start = t0 - timedelta(minutes=minutes)
        end = t0 + timedelta(minutes=minutes)

        tmp = df_src.copy()
        tmp["__line_key"] = tmp["설비명"].apply(_extract_line_key_from_mes_eqp).apply(_linekey_norm)
        lk = _linekey_norm(line_key)

        m = (tmp["__line_key"] == lk) & (tmp["발생일시"] >= start) & (tmp["발생일시"] <= end)
        cols = [c for c in ["발생일시","해제일시","경과(초)","알람 명","설비명","설비 ID","매칭된_BMPD"] if c in tmp.columns]
        return tmp.loc[m, cols].sort_values("발생일시")

    def _bmpd_window(df_b: pd.DataFrame, line_key: str, t0: pd.Timestamp, minutes=15):
        if df_b is None or len(df_b) == 0 or pd.isna(t0):
            st.write("BMPD 데이터가 없거나, 기준 시간이 유효하지 않습니다.")
            return pd.DataFrame()
        if "호기" not in df_b.columns or "발생시간" not in df_b.columns:
            st.write("BMPD 데이터에 '호기' 또는 '발생시간' 컬럼이 없습니다.") 
            return pd.DataFrame()
        
        start = t0 - timedelta(minutes=minutes)
        end = t0 + timedelta(minutes=minutes)

        tmp = df_b.copy()
        tmp["__line_key"] = tmp["호기"].astype(str).apply(_linekey_norm)
        lk = _linekey_norm(line_key)

        m = (tmp["__line_key"] == lk) & (tmp["발생시간"] >= start) & (tmp["발생시간"] <= end)
        cols = [c for c in ["호기","Machine","Unit","Assy'","발생시간","조치완료","현상","원인","조치"] if c in tmp.columns]
        return tmp.loc[m, cols].sort_values("발생시간")

    def _pick_bmpd_t0_nearest_to_mes(cands: list[dict], t_mes: pd.Timestamp):
        # 후보들 중 '발생시간'이 t_mes에 가장 가까운 것을 BMPD 기준 t0로 선택
        best_t = pd.NaT
        best_d = None
        best_diff = None

        for d in cands:
            t = pd.to_datetime(d.get("발생시간"), errors="coerce")
            if pd.isna(t) or pd.isna(t_mes):
                continue
            diff = abs((t - t_mes).total_seconds())
            if best_diff is None or diff < best_diff:
                best_diff = diff
                best_t = t
                best_d = d
        return best_t, best_d

    # 우측 사례 리스트(각 행 + 매칭된 BMPD 후보들)
    # with right:
    st.markdown("#### 사례 목록")
    eqp_list = ["(전체)"] + sorted(df_alarm["설비명"].dropna().astype(str).unique().tolist())
    eqp_sel = st.selectbox("설비명 필터", eqp_list, index=0)

    bmpd_filter = st.checkbox("매칭된 BMPD가 1개 이상인 것만 보기", value=False)
    df_show = df_alarm if eqp_sel == "(전체)" else df_alarm[df_alarm["설비명"].astype(str) == eqp_sel]

    if bmpd_filter:
        df_show = df_show[df_show["매칭된_BMPD"].astype(bool)]

    for i, row in df_show.reset_index(drop=True).iterrows():
        title = f"[{row.get('설비명','')}] {row.get('발생일시','')} → {row.get('해제일시','')}, {row.get('경과(초)','')}초"
        with st.expander(title, expanded=False):
            # 기본 정보
            st.write("**기본 정보**")
            st.write({
                "설비명": row.get("설비명",""),
                "설비 ID": row.get("설비 ID",""),
                "발생일시": row.get("발생일시",""),
                "해제일시": row.get("해제일시",""),
                "경과(초)": row.get("경과(초)",""),
                "알람 명": row.get("알람 명",""),
            })

            # 매칭 후보 표시
            cands = _parse_cands(row.get("매칭된_BMPD"))
            if not cands:
                st.info("매칭된 BMPD 없음")
                continue

            # ----------------------------
            # ✅ 여기부터 "윈도우 보기" (MES±15 / BMPD±15)
            # ----------------------------
            st.markdown("### 🕒 MES - BMPD 흐름 확인 (±20분)")

            t_mes = pd.to_datetime(row.get("발생일시"), errors="coerce")
            line_key = _extract_line_key_from_mes_eqp(row.get("설비명", ""))
            if line_key == "__fail__":
                st.warning("설비명에서 라인(#xx-yy) 추출 실패 → 호기 필터 정확도가 떨어질 수 있습니다.")

            t_bmpd, picked = _pick_bmpd_t0_nearest_to_mes(cands, t_mes)

            colA, colB = st.columns(2, gap="large")

            with colA:
                st.markdown("#### 🟦 MES")
                mes_ctx = _mes_window(df, line_key=line_key, t0=t_mes, minutes=20)
                if mes_ctx.empty:
                    st.info("해당 윈도우에 MES 알람이 없습니다.")
                else:
                    st.dataframe(mes_ctx, use_container_width=True)

            with colB:
                st.markdown("#### 🟩 BMPD")
                if df_bmpd is None:
                    st.info("df_bmpd가 전달되지 않아 BMPD 윈도우를 만들 수 없습니다.")
                elif pd.isna(t_bmpd):
                    st.info("매칭 후보에서 BMPD 발생시간을 읽지 못해 BMPD 기준 윈도우를 만들 수 없습니다.")
                else:
                    bmpd_ctx = _bmpd_window(df_bmpd, line_key=line_key, t0=t_bmpd, minutes=20)
                    if bmpd_ctx.empty:
                        st.info("해당 윈도우에 BMPD 이벤트가 없습니다.")
                    else:
                        st.dataframe(bmpd_ctx, use_container_width=True)

            st.divider()

            # ----------------------------
            # 그 다음에 기존대로 기본정보/후보를 출력
            # # ----------------------------
            # st.write("**기본 정보**")
            # st.write({
            #     "설비명": row.get("설비명",""),
            #     "설비 ID": row.get("설비 ID",""),
            #     "발생일시": row.get("발생일시",""),
            #     "해제일시": row.get("해제일시",""),
            #     "경과(초)": row.get("경과(초)",""),
            #     "알람 명": row.get("알람 명",""),
            # })

            # st.markdown("#### 매칭 후보")
            # for j, d in enumerate(cands, start=1):
            #     st.markdown(f"**매칭 후보 #{j} — {d.get('BMPD_ID','')}**")
            #     st.write({
            #         "호기": d.get("호기",""),
            #         "Machine": d.get("Machine",""),
            #         "Assy'": d.get("Assy'",""),
            #         "현상": d.get("현상",""),
            #         "원인": d.get("원인",""),
            #         "조치": d.get("조치",""),
            #         "발생시간": d.get("발생시간",""),
            #         "조치완료": d.get("조치완료",""),
            #     })
            #     st.markdown("---")