import io
import re
import pandas as pd
import streamlit as st
from datetime import datetime, date, time, timedelta

from utils import KIND_OPTIONS, SITE_OPTIONS, PROCESS_OPTIONS, UNIT_OPTIONS, load_sheet_data

# --- 페이지 설정
st.set_page_config(page_title="주/야간 인수인계 사항", layout="wide")
st.title("주/야간 인수인계 정리")

# --- 공통 함수
def detect_cols(df):
    """실제 컬럼명을 자동 매핑"""
    cols = {c: c for c in df.columns}
    name_map = {}

    def pick(patterns, fallback=None):
        for p in patterns:
            for c in df.columns:
                if re.search(p, c, re.IGNORECASE):
                    return c
        return fallback

    name_map["site"] = pick([r"\bsite\b", "사이트"])
    name_map["kind"] = pick(["종류", "Type"])
    name_map["ho"]   = pick(["호기", "Line|Tool|Eqp"])
    name_map["machine"] = pick(["^Machine$","머신","장비"])
    name_map["unit"]    = pick(["^Unit$","유닛"])
    name_map["assy"]    = pick([r"Assy", r"Assy'","어셈"])
    name_map["operator"]= pick(["작업자","담당자"])
    name_map["symptom"] = pick(["현상"])
    name_map["cause"]   = pick(["원인"])
    name_map["action"]  = pick(["조치"])
    name_map["occur_dt"]= pick(["발생시간","발생 일시","발생 일자","발생일"])
    name_map["done_dt"] = pick(["조치완료", "조치완료","완료시간","종료시간"])

    missing = [k for k,v in name_map.items() if v is None and k in ("site","occur_dt")]
    if missing:
        raise ValueError(f"필수 컬럼을 찾지 못했습니다: {missing} / 실제 컬럼: {list(df.columns)}")
    return name_map

def to_datetime_safe(s):
    return pd.to_datetime(s, errors="coerce")

def get_shift_range(d: date, shift: str):
    """주간: d 08:00 ~ d 20:00, 야간: d 20:00 ~ d+1 08:00, 종일: d 00:00 ~ d 23:59:59"""
    if shift == "주간":
        start = datetime.combine(d, time(8,0,0))
        end   = datetime.combine(d, time(20,0,0))
    elif shift == "야간":
        start = datetime.combine(d, time(20,0,0))
        end   = datetime.combine(d + timedelta(days=1), time(8,0,0))
    else:  # 종일
        start = datetime.combine(d, time(0,0,0))
        end   = datetime.combine(d, time(23,59,59))
    return start, end

# --- 줄글 요약 함수 (교체)
def _fmt_dt(dt):
    if pd.isna(dt):
        return "—"
    return pd.to_datetime(dt).strftime("%H:%M")  # 시:분만

def _fmt_dur(start, end):
    if pd.isna(start):
        return "00:00"
    if pd.isna(end):
        end = pd.Timestamp.now()
    delta = pd.to_datetime(end) - pd.to_datetime(start)
    mins = int(delta.total_seconds() // 60)
    h, m = divmod(mins, 60)
    return f"{h:02d}:{m:02d}"

def build_text_summary(df, nm):
    """
    [#호기]
    HH:MM ~ HH:MM (HH:MM)
    Machine / Unit / Assy'
    - 현상: ...
    - 원인: ...
    - 조치: ...
    - 후속 조치 필요사항:
    """
    import pandas as pd
    import re
    from datetime import datetime

    def _is_datetime_like(val) -> bool:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return False
        # 명시적 datetime/timestamp
        if isinstance(val, (pd.Timestamp, datetime)):
            return True
        s = str(val).strip()
        # 'NaT' 같은 값은 날짜 아님
        if s.lower() in ("nat", "none", ""):
            return False
        # yyyy-mm-dd ... hh:mm (초 유무 무관) 패턴 탐지
        if re.search(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}", s) and re.search(r"\b\d{1,2}:\d{2}(:\d{2})?\b", s):
            return True
        # hh:mm(:ss)만 들어온 경우도 날짜류로 간주하지 않음 → 조치 텍스트일 수도 있으니 False
        return False

    ho_col    = nm.get("ho")
    occ_col   = nm.get("occur_dt")
    done_col  = nm.get("done_dt")
    mac_col   = nm.get("machine")
    unit_col  = nm.get("unit")
    assy_col  = nm.get("assy")
    sym_col   = nm.get("symptom")
    cause_col = nm.get("cause")
    act_col   = nm.get("action")

    # --- 액션 컬럼 교정: done_dt로 잘못 매핑되거나 시간/완료 키워드가 들어가면 '조치' 컬럼을 재탐색
    if (not act_col) or (act_col == done_col) or re.search(r"(완료|종료|end|time)", str(act_col), re.IGNORECASE):
        exact = [c for c in df.columns if re.fullmatch(r"\s*조치\s*", str(c))]
        if exact:
            act_col = exact[0]

    # 결측 대비
    for c in [mac_col, unit_col, assy_col, sym_col, cause_col, act_col]:
        if c and c not in df.columns:
            df[c] = ""

    # 발생시간 기준 정렬
    if occ_col in df.columns:
        df = df.sort_values(by=occ_col, kind="stable")

    lines = []
    for ho, g in df.groupby(ho_col, dropna=False):
        ho_name = str(ho).strip() if pd.notna(ho) and str(ho).strip() else "미지정"
        lines.append(f"[{ho_name}호기]")
        for _, r in g.iterrows():
            start = r.get(occ_col, pd.NaT)
            end   = r.get(done_col, pd.NaT)

            start_s = _fmt_dt(start)
            end_s   = _fmt_dt(end) if pd.notna(end) else "진행중"
            dur_s   = _fmt_dur(start, end)

            machine = str(r.get(mac_col, "") or "").strip()
            unit    = str(r.get(unit_col, "") or "").strip()
            assy    = str(r.get(assy_col, "") or "").strip()
            symptom = str(r.get(sym_col, "") or "").strip()
            cause   = str(r.get(cause_col, "") or "").strip()

            # --- 조치 문자열 안전 처리: datetime류로 보이면 출력하지 않음
            action_val = r.get(act_col, "")
            action = "" if _is_datetime_like(action_val) else str(action_val or "").strip()

            header = f"{start_s} ~ {end_s} ({dur_s})"
            equip  = " / ".join([x for x in [machine, unit, assy] if x])

            lines.append(header)
            if equip:
                lines.append(equip)
            lines.append(f"- 현상: {symptom}")
            lines.append(f"- 원인: {cause}")
            lines.append(f"- 조치: {action}")
            lines.append("- 후속 조치 필요사항: ")
            lines.append("")          # 이력 간 구분 공백

    return "\n".join(lines).strip()



def build_handover_excel(df, nm):
    """엑셀 인수인계서(체크리스트 포함) 바이너리를 반환"""
    # 보고서 컬럼 표준화
    cols_out = [
        "발생시간","조치완료","Site","종류","호기","Machine","Unit","Assy'","작업자","현상","원인","조치","금일 필요 추가 조치 사항"
    ]
    def pick(colkey, default=""):
        c = nm.get(colkey)
        return df[c] if c in df.columns else default

    out = pd.DataFrame({
        "발생시간": to_datetime_safe(df[nm["occur_dt"]]),
        "조치완료": to_datetime_safe(df[nm["done_dt"]]) if nm.get("done_dt") else pd.NaT,
        "Site": df[nm["site"]] if nm.get("site") in df.columns else "",
        "종류": df[nm["kind"]] if nm.get("kind") in df.columns else "",
        "호기": df[nm["ho"]] if nm.get("ho") in df.columns else "",
        "Machine": df[nm["machine"]] if nm.get("machine") in df.columns else "",
        "Unit": df[nm["unit"]] if nm.get("unit") in df.columns else "",
        "Assy'": df[nm["assy"]] if nm.get("assy") in df.columns else "",
        "작업자": df[nm["operator"]] if nm.get("operator") in df.columns else "",
        "현상": df[nm["symptom"]] if nm.get("symptom") in df.columns else "",
        "원인": df[nm["cause"]] if nm.get("cause") in df.columns else "",
        "조치": df[nm["action"]] if nm.get("action") in df.columns else "",
        "금일 필요 추가 조치 사항": ""
    })

    # 엑셀 작성
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter", datetime_format="yyyy-mm-dd HH:MM:ss") as xw:
        out.to_excel(xw, index=False, sheet_name="체크리스트")
        ws = xw.sheets["체크리스트"]
        # 가독성: 헤더 bold + 자동열폭
        workbook = xw.book
        header_fmt = workbook.add_format({"bold": True, "text_wrap": True, "valign": "vcenter", "border":1})
        cell_fmt   = workbook.add_format({"text_wrap": True, "valign": "top", "border":1})
        for col_num, value in enumerate(out.columns.values):
            ws.write(0, col_num, value, header_fmt)
            ws.set_column(col_num, col_num, 20, cell_fmt)

        # 조건부서식: 조치완료이 비어있으면 행 음영
        last_row = len(out) + 1
        done_col_index = out.columns.get_loc("조치완료")
        ws.conditional_format(1, 0, last_row, len(out.columns)-1, {
            "type":"formula",
            "criteria": f'ISBLANK(INDIRECT(ADDRESS(ROW(),{done_col_index+1})))',
            "format": workbook.add_format({"bg_color":"#FFEEEE"})
        })
    buf.seek(0)
    return buf


# --- UI 1) 사이트 선택 + 데이터 로드
selected_site = st.selectbox("🔍 사이트", SITE_OPTIONS, index=0)

df, error = load_sheet_data()
if error:
    st.error(error); st.stop()

# 사이트 컬럼 탐지 및 필터
try:
    colmap_tmp = detect_cols(df)
except Exception as e:
    st.error(str(e)); st.stop()

site_col = colmap_tmp.get("site")
df_site = df[df[site_col] == selected_site].copy() if site_col in df.columns else df.copy()
if df_site.empty:
    st.warning(f"‘{selected_site}’ 데이터가 없습니다."); st.stop()

# 시간 컬럼 형변환
occur_col = colmap_tmp.get("occur_dt")
done_col  = colmap_tmp.get("done_dt")
df_site[occur_col] = to_datetime_safe(df_site[occur_col])
if done_col:
    df_site[done_col] = to_datetime_safe(df_site[done_col])

# --- UI 2) 날짜/교대 선택
c1, c2, c3 = st.columns([1,1,2])
with c1:
    target_date = st.date_input("📅 기준 날짜(하루)", value=date.today())
with c2:
    shift = st.radio("교대", ["주간","야간","종일"], index=0, horizontal=True)

start_dt, end_dt = get_shift_range(target_date, shift)
st.info(f"조회 구간: {start_dt} ~ {end_dt}")

# --- 필터링 (발생시간 기준)
mask = (df_site[occur_col] >= start_dt) & (df_site[occur_col] < end_dt)
df_range = df_site.loc[mask].copy().reset_index(drop=True)

st.markdown(f"**주간/야간 데이터: {len(df_range)}건**")
st.dataframe(df_range, use_container_width=True)

# --- 엑셀 인수인계서 (체크리스트) 생성/다운로드
if not df_range.empty:
    try:
        xls_buf = build_handover_excel(df_range, colmap_tmp)
        st.download_button(
            label="⬇️ 인수인계 사항 (엑셀) 다운로드",
            data=xls_buf.getvalue(),
            file_name=f"인수인계서_{selected_site}_{target_date}_{shift}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"엑셀 생성 실패: {e}")

# --- 호기별 줄글 요약 (텍스트만)
st.subheader("호기별 발생 이력 요약 (text)")
if df_range.empty:
    st.write("해당 구간 데이터가 없습니다.")
else:
    text_summary = build_text_summary(df_range, colmap_tmp)
    st.text_area("줄글 요약", value=text_summary, height=320)
    st.caption("위 내용을 그대로 복사(Ctrl/Cmd + C)하여 회의자료/채팅에 붙여넣으세요.")

