import pandas as pd
import re
import ast
import streamlit as st
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any, Optional


# ==========================================================
# 0) 공통 상수 / 유틸
# ==========================================================

TARGET_COL = "알람 명"
CLEAN_COL  = "알람 명_cleaned"


# ==========================================================
# 1) 전처리: 알람명 정리 + 제외 키워드 + 길이 필터
# ==========================================================

def df_clean_korean(df_: pd.DataFrame, threshold_length: int = 10) -> pd.DataFrame:
    """
    '알람 명' 컬럼 전처리:
    - [F....] 패턴 제거
    - 양끝 공백 제거, 소문자화
    - Door/스페어 등 제외
    - 텍스트 길이(threshold_length) 미만 제거
    """
    if TARGET_COL not in df_.columns:
        print(f"오류: 데이터프레임에 '{TARGET_COL}' 컬럼이 없습니다.")
        return df_

    df = df_.copy()
    df[CLEAN_COL] = df[TARGET_COL].astype(str)

    # [F....] 제거 (요구하신 패턴 유지)
    df[CLEAN_COL] = df[CLEAN_COL].str.replace(r"\[F.*?\]\s*", "", regex=True)

    # strip + lower
    df[CLEAN_COL] = df[CLEAN_COL].str.strip().str.lower()

    # 제외 키워드
    exclude_pat = r"스페어|도어|문|cell tracking|만재|door|open|경고"
    df = df[~df[CLEAN_COL].str.contains(exclude_pat, case=False, na=False, regex=True)].copy()

    # 길이 계산은 필터된 df 기준으로
    df["text_length"] = df[CLEAN_COL].str.len()

    # 길이 필터
    df = df[df["text_length"] >= threshold_length].copy()

    print("--- 전처리 결과 요약 ---")
    print(f"원본 데이터 개수: {len(df_)} 행")
    print(f"길이 {threshold_length} 미만 제거 후 남은 데이터 개수: {len(df)} 행\n")

    return df


# ==========================================================
# 2) MES 설비명에서 공정/호기 키 추출
# ==========================================================

def extract_process_lastword(equip_name: str) -> str:
    """
    MES 설비명에서 공정 키워드를 추출하여
    BMPD Machine(소문자)와 비교 가능한 형태로 반환
    """
    if not isinstance(equip_name, str):
        return "__fail__"

    s = equip_name.strip().lower()
    toks = s.split()

    # STK/LAMI 분류 전이면 STK로 가정하겠다는 기존 의도 유지
    if not s or len(toks) < 2:
        return "undecided(stk)"

    raw_process = toks[1]

    if "supply" in raw_process or "electrode" in raw_process:
        return "electrode supply"
    elif "lam" in raw_process or "lam" in toks[0]:
        return "lamination"
    elif "d-stacking" in raw_process:
        return "d-stacking"
    elif "taper" in raw_process:
        return "taper"
    elif "inspection" in raw_process:
        return "inspection"

    return "undecided(stk)"


def extract_line_from_text(equip_name: str) -> str:
    """
    설비명에서 '#숫자-숫자' 패턴을 추출하고,
    뒷자리 0 제거 (예: '#26-05' -> '#26-5')
    """
    if not isinstance(equip_name, str):
        return "__fail__"

    m = re.search(r"#\d+-\d+", equip_name)
    if not m:
        return "__fail__"

    line = m.group(0)   # "#26-05"
    left, right = line.split("-")
    try:
        right = str(int(right))  # "05" -> "5"
    except Exception:
        return "__fail__"

    return f"{left}-{right}"


def normalize_line_key_from_mes(equip_name: Any) -> str:
    """
    MES 설비명 -> __line_key 생성 (숫자만 남김)
    예: '#26-5' -> '265'
    """
    line = extract_line_from_text(str(equip_name))
    if line == "__fail__":
        return "__fail__"
    # '#', '-', '_' 제거 (문자열 처리 str.replace로 통일)
    s = str(line).replace("#", "").replace("-", "").replace("_", "")
    return s.strip()


def normalize_line_key_from_bmpd(line: Any) -> str:
    """
    BMPD 호기 -> __line_key 생성 (숫자만 남김)
    예: '#26-5' 또는 '26-5' -> '265'
    """
    s = str(line).strip()
    s = s.replace("#", "").replace("-", "").replace("_", "")
    return s


# ==========================================================
# 3) 핵심 매칭 로직
# ==========================================================

def collect_window_mes_to_bmpd(
    mes: pd.DataFrame,
    bmpd: pd.DataFrame,
    out_col: str = "매칭된_BMPD",
    tol: str = "10min",
) -> pd.DataFrame:
    """
    MES 알람과 BMPD 조치를 호기/날짜/시간윈도우/공정이 모두 일치하는 이력으로 매칭.

    요구사항 반영:
    - 공정: MES __process_group == BMPD Machine_lower
    - 호기: __line_key 동일
    - 날짜: 발생일시 date == 발생시간 date
    - 시간윈도우:
        (1) BMPD 발생시간 <= MES 발생일시 <= BMPD 발생시간+tol
        (2) MES 발생일시 <= BMPD 조치완료 (이상한 케이스 방지)
        (3) BMPD 조치완료-tol <= MES 해제일시 <= BMPD 조치완료+tol
    """
    tol_td = pd.Timedelta(tol)

    mes_time        = "발생일시"
    mes_time_end    = "해제일시"
    bmpd_start_time = "발생시간"

    # ✅ 여기 핵심: BMPD 종료시간 컬럼명 통일
    # 여러분 데이터에서는 '조치완료'로 읽고 있었으니 이걸 공식으로 통일
    bmpd_end_time   = "조치완료"

    mes_process_col = "__process_group"

    KEEP = ["호기", "Machine", "Unit", "Assy'", "발생시간", "조치완료", "현상", "원인", "조치"]

    mes = mes.copy()
    bmpd = bmpd.copy()

    # 타입 보정
    mes[mes_time]     = pd.to_datetime(mes.get(mes_time), errors="coerce")
    mes[mes_time_end] = pd.to_datetime(mes.get(mes_time_end), errors="coerce")

    bmpd[bmpd_start_time] = pd.to_datetime(bmpd.get(bmpd_start_time), errors="coerce")
    bmpd[bmpd_end_time]   = pd.to_datetime(bmpd.get(bmpd_end_time), errors="coerce")

    # 공정 키
    if "Machine" not in bmpd.columns:
        bmpd["Machine"] = pd.NA
    bmpd["Machine_lower"] = bmpd["Machine"].astype(str).str.lower()

    # 호기 키
    if "설비명" not in mes.columns:
        mes["설비명"] = pd.NA
    if "호기" not in bmpd.columns:
        bmpd["호기"] = pd.NA

    mes["__line_key"]  = mes["설비명"].apply(normalize_line_key_from_mes)
    bmpd["__line_key"] = bmpd["호기"].apply(normalize_line_key_from_bmpd)

    # 날짜 키 + row key
    mes["_key"]    = range(len(mes))
    mes["__date"]  = mes[mes_time].dt.date
    bmpd["__date"] = bmpd[bmpd_start_time].dt.date

    # 1차 조인(날짜+호기)
    tmp = mes.merge(
        bmpd,
        on=["__date", "__line_key"],
        how="left",
        suffixes=("_mes", "_bmpd"),
    )

    # BMPD 발생시간 없는건 제외
    tmp = tmp[tmp[bmpd_start_time].notna()].copy()
    if tmp.empty:
        mes[out_col] = [[]] * len(mes)
        return mes.drop(columns=["_key", "__date", "__line_key"], errors="ignore")

    # 필터링 조건
    is_start_close_to_start = (
        (tmp[bmpd_start_time] <= tmp[mes_time]) &
        (tmp[mes_time] <= tmp[bmpd_start_time] + tol_td) &
        (tmp[mes_time] <= tmp[bmpd_end_time])
    )

    is_end_close_to_end = (
        (tmp[bmpd_end_time] - tol_td <= tmp[mes_time_end]) &
        (tmp[mes_time_end] <= tmp[bmpd_end_time] + tol_td)
    )

    # 공정 매칭
    if mes_process_col not in tmp.columns:
        tmp[mes_process_col] = "undecided(stk)"
    is_process_match = (tmp[mes_process_col].astype(str) == tmp["Machine_lower"].astype(str))

    df_filtered = tmp[is_start_close_to_start & is_end_close_to_end & is_process_match].copy()

    if df_filtered.empty:
        mes[out_col] = [[]] * len(mes)
        return mes.drop(columns=["_key", "__date", "__line_key"], errors="ignore")

    take = [c for c in KEEP if c in df_filtered.columns]
    grouped = df_filtered.groupby("_key")[take].apply(lambda g: g.to_dict("records"))

    s = mes["_key"].map(grouped)
    mes[out_col] = s.apply(lambda v: v if isinstance(v, list) else [])

    return mes.drop(columns=["_key", "__date", "__line_key"], errors="ignore")


def run_matching_reverse(df_BMPD: pd.DataFrame, df_MES: pd.DataFrame) -> pd.DataFrame:
    """
    MES에 __process_group 생성 후, 공정별로 분리 매칭하여 결과 concat
    """
    df_BMPD = df_BMPD.copy()
    df_MES  = df_MES.copy()

    # 시간 컬럼 통일
    if "발생시간" in df_BMPD.columns:
        df_BMPD["발생시간"] = pd.to_datetime(df_BMPD["발생시간"], errors="coerce")

    # ✅ BMPD 종료시간은 '조치완료'로 통일
    if "조치완료" in df_BMPD.columns:
        df_BMPD["조치완료"] = pd.to_datetime(df_BMPD["조치완료"], errors="coerce")
    elif "조치완료시간" in df_BMPD.columns:
        df_BMPD["조치완료"] = pd.to_datetime(df_BMPD["조치완료시간"], errors="coerce")
    else:
        df_BMPD["조치완료"] = pd.NaT

    if "발생일시" in df_MES.columns:
        df_MES["발생일시"] = pd.to_datetime(df_MES["발생일시"], errors="coerce")
    if "해제일시" in df_MES.columns:
        df_MES["해제일시"] = pd.to_datetime(df_MES["해제일시"], errors="coerce")

    # 공정 분류
    if "설비명" not in df_MES.columns:
        df_MES["설비명"] = pd.NA
    df_MES["__process_group"] = df_MES["설비명"].apply(extract_process_lastword)

    results = []
    for process in df_MES["__process_group"].dropna().unique():
        df_sub = df_MES[df_MES["__process_group"] == process].copy()
        res_sub = collect_window_mes_to_bmpd(df_sub, df_BMPD, out_col="매칭된_BMPD", tol="10min")
        results.append(res_sub)

    if not results:
        return pd.DataFrame()

    out = pd.concat(results, ignore_index=True)
    out = out.drop(columns=["__process_group"], errors="ignore")
    return out


# ==========================================================
# 4) Streamlit 표시용: 매칭 후보 파싱 + UI
# ==========================================================

def _parse_cands(cell: Any) -> List[Dict[str, Any]]:
    """
    매칭된_BMPD 셀(리스트/문자열/None)을 안전하게 [dict, ...]로 변환
    """
    if cell is None or (isinstance(cell, float) and pd.isna(cell)):
        return []

    if isinstance(cell, str):
        try:
            cell = ast.literal_eval(cell)
        except Exception:
            return []

    if not isinstance(cell, (list, tuple)):
        cell = [cell]

    out: List[Dict[str, Any]] = []
    for it in cell:
        if isinstance(it, dict):
            d = it.copy()
        else:
            d = {"raw": str(it)}

        # 키 보정 (있는 키는 유지)
        d.setdefault("BMPD_ID", d.get("bmpd_id") or d.get("id") or d.get("row_idx") or "")
        d.setdefault("현상", d.get("현상") or d.get("symptom") or "")
        d.setdefault("원인", d.get("원인") or d.get("cause") or "")
        d.setdefault("조치", d.get("조치") or d.get("action") or "")

        # 시간키는 시간키에서만 가져오도록 (이전 버그 수정)
        d.setdefault("발생시간", d.get("발생시간") or d.get("start_time") or "")
        d.setdefault("조치완료시간", d.get("조치완료시간") or d.get("조치완료") or d.get("end_time") or "")

        out.append(d)

    return out


def show_alarm_catalog_and_detail(df_all: pd.DataFrame):
    need_cols = ["알람 명", "설비명", "설비 ID", "발생일시", "해제일시", "경과(초)", "매칭된_BMPD"]
    df = df_all.copy()
    for c in need_cols:
        if c not in df.columns:
            df[c] = pd.NA

    df["발생일시"] = pd.to_datetime(df["발생일시"], errors="coerce")
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
          .apply(lambda x: sum((len(i) if isinstance(i, list) else 0) for i in x))
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

    alarm_sel = st.selectbox("확인할 알람명을 선택", options=freq["알람 명"].tolist())
    st.divider()

    st.subheader(f"알람명: {alarm_sel}")
    df_alarm = df[df["알람 명"] == alarm_sel].copy().sort_values("발생일시")

    left, right = st.columns([1, 2], gap="large")

    with left:
        st.markdown("#### 요약")
        st.metric("총 발생 횟수", f"{len(df_alarm):,}")

        if "경과(초)" in df_alarm.columns and not df_alarm["경과(초)"].isna().all():
            dur = pd.to_numeric(df_alarm["경과(초)"], errors="coerce")
            st.metric("평균 경과(초)", f"{dur.mean():.1f}")
            st.metric("최장 경과(초)", f"{dur.max():.0f}")

        st.markdown("##### 설비 분포")
        eqp = (
            df_alarm.groupby(["설비명", "설비 ID"], dropna=False)
                   .size().reset_index(name="건수")
                   .sort_values("건수", ascending=False)
        )
        st.dataframe(eqp.head(20), use_container_width=True, hide_index=True)

    with right:
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
                st.write("**기본 정보**")
                st.write({
                    "설비명": row.get("설비명", ""),
                    "설비 ID": row.get("설비 ID", ""),
                    "발생일시": row.get("발생일시", ""),
                    "해제일시": row.get("해제일시", ""),
                    "경과(초)": row.get("경과(초)", ""),
                    "설비상태": row.get("설비상태", ""),
                    "알람코드": row.get("알람코드", ""),
                    "알람 명": row.get("알람 명", ""),
                })

                cands = _parse_cands(row.get("매칭된_BMPD"))
                if not cands:
                    st.info("매칭된 BMPD 없음")
                else:
                    for j, d in enumerate(cands, start=1):
                        st.markdown(f"**매칭 후보 #{j} — {d.get('BMPD_ID','')}**")
                        st.write({
                            "호기": d.get("호기", ""),
                            "Machine": d.get("Machine", ""),
                            "Assy'": d.get("Assy'", ""),
                            "현상": d.get("현상", ""),
                            "원인": d.get("원인", ""),
                            "조치": d.get("조치", ""),
                            "발생시간": d.get("발생시간", ""),
                            "조치완료시간": d.get("조치완료시간", ""),
                        })
                        st.markdown("---")


# ==========================================================
# 5) 업로드 유틸
# ==========================================================

def read_excel_safely(file, sheet_name: Optional[str] = None):
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


def merge_uploaded_excels(uploaded_files) -> pd.DataFrame:
    """
    Streamlit에서 여러 Excel/CSV 파일이 업로드된 경우 병합
    """
    dfs = []
    for f in uploaded_files:
        name = f.name.lower()
        try:
            if name.endswith(".csv"):
                # pandas 버전 호환을 위해 encoding_errors 사용
                df = pd.read_csv(f, encoding="utf-8", encoding_errors="ignore")
            elif name.endswith((".xls", ".xlsx")):
                df = pd.read_excel(f)
            else:
                print(f"⚠️ 지원하지 않는 파일 형식: {f.name}")
                continue

            df.columns = df.columns.str.strip()
            df["__source_file"] = f.name
            dfs.append(df)

        except Exception as e:
            print(f"❌ {f.name} 읽기 실패: {e}")

    if not dfs:
        print("❌ 병합할 데이터가 없습니다.")
        return pd.DataFrame()

    merged_df = pd.concat(dfs, ignore_index=True).convert_dtypes()
    print(f"✅ 총 {len(uploaded_files)}개 파일 병합 완료, 행 수: {len(merged_df)}")
    return merged_df
