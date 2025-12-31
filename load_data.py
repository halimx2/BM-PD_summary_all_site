import io
import requests
import pandas as pd
import streamlit as st
from options import KIND_OPTIONS, SITE_OPTIONS, PROCESS_OPTIONS, UNIT_OPTIONS

import os
from dotenv import load_dotenv
import re

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# load_dotenv()   # .env 읽어서 환경변수 등록

SHEET_ID  = st.secrets["SHEET_ID"]
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json"


import io
import os
import re
import requests
import pandas as pd
import streamlit as st
from datetime import date, timedelta
from dotenv import load_dotenv
from openpyxl import load_workbook
from options import KIND_OPTIONS, SITE_OPTIONS, PROCESS_OPTIONS, UNIT_OPTIONS

# 환경변수 로드
load_dotenv()
SHEET_ID  = os.getenv("SHEET_ID")
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json"

def load_sheet_data_google():
    resp = requests.get(SHEET_URL)
    if resp.status_code != 200:
        return None, f"❌ 데이터 요청 실패: {resp.status_code}"

    # JSONP 제거 및 JSON 파싱
    json_str = resp.text[47:-2]
    import json
    data_json = json.loads(json_str)
    
    # 1. 모든 행 가져오기 (헤더 포함을 위해 0번부터 혹은 제목행 인덱스 확인)
    rows = data_json['table']['rows']

    # 2. 2차원 리스트화 (데이터 정제)
    values = []
    for r in rows:
        row_data = []
        for c in r.get('c', []):
            if c is None:
                row_data.append('')
            else:
                val = c.get('v')
                # 숫자가 'v'에 있고 포맷된 문자열이 'f'에 있는 경우 처리
                row_data.append(str(val) if val is not None else '')
        values.append(row_data)

    if not values:
        return pd.DataFrame(), "데이터가 없습니다."

    # 3. 유동적 헤더 추출 (첫 번째 행을 컬럼명으로 사용)
    # values[0]이 'Machine', 'Unit' 등이 있는 제목줄인지 확인하세요.
    raw_headers = [str(h).strip() for h in values[0]]
    
    # 4. 데이터프레임 생성 (데이터는 1번 행부터)
    df_ = pd.DataFrame(values[1:], columns=raw_headers)

    # [검증] 사진에 있는 주요 컬럼들이 있는지 확인하고 중복 제거
    subset_cols = ['발생시간', '조치완료', '작업자', '현상']
    
    # 실제로 시트에 존재하는 컬럼만 필터링 (KeyError 방지)
    existing_subset = [c for c in subset_cols if c in df_.columns]
    
    if existing_subset:
        df_ = df_.drop_duplicates(subset=existing_subset, ignore_index=True)
        
    return df_


# 데이터 로드 및 전처리 함수
@st.cache_data(ttl=300)
def load_sheet_data() -> tuple[pd.DataFrame|None, str|None]:
    df = load_sheet_data_google()
    # 그 후 중복 제거 실행
    subset_cols = ['발생시간', '조치완료', '작업자', '현상']
    df = df.drop_duplicates(subset=subset_cols, ignore_index=True)


    # 한국어 날짜 파싱
    RE = re.compile(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일\s*(오전|오후)\s*(\d{1,2}):(\d{2})")
    def parse_korean_dt(s: str) -> pd.Timestamp:
        m = RE.match(str(s));
        if not m: return pd.NaT
        y, mo, d, ampm, hr, mi = m.groups()
        y, mo, d, h, mi = int(y), int(mo), int(d), int(hr), int(mi)
        if ampm == '오후' and h < 12: h += 12
        if ampm == '오전' and h == 12: h = 0
        return pd.Timestamp(y, mo, d, h, mi)

    df[['발생시간','조치완료']] = df[['발생시간','조치완료']].applymap(parse_korean_dt)

    # 초기 조치시간 계산(분)
    df['조치 진행 시간(분)'] = ((df['조치완료'] - df['발생시간'])
                               .dt.total_seconds().div(60).round().astype('Int64'))

    # 음수 보정: 이전 로직 (300 이하 스와핑, 1200 이상 다음날)
    neg = df['조치 진행 시간(분)'] < 0
    mask1 = neg & (df['조치 진행 시간(분)'].abs() >= 1200)
    df.loc[mask1, '조치완료'] += timedelta(days=1)
    mask2 = neg & (df['조치 진행 시간(분)'].abs() <= 300)
    df.loc[mask2, ['발생시간','조치완료']] = df.loc[mask2, ['조치완료','발생시간']].values

    # 재계산
    df['조치 진행 시간(분)'] = ((df['조치완료'] - df['발생시간'])
                               .dt.total_seconds().div(60).round().astype('Int64'))

    # 신규 보정: 1400 초과 경우 날짜만 발생일로 교체
    mask3 = df['조치 진행 시간(분)'] > 1400
    df.loc[mask3, '조치완료'] = df.loc[mask3].apply(
        lambda r: r['조치완료'].replace(
            year=r['발생시간'].year,
            month=r['발생시간'].month,
            day=r['발생시간'].day
        ), axis=1
    )

    # 재계산 최종
    df['조치 진행 시간(분)'] = ((df['조치완료'] - df['발생시간'])
                               .dt.total_seconds().div(60).round().astype('Int64'))

    # 현상/원인/조치 필터
    # (1) 필터
    tmp = df[['현상','원인','조치']].fillna('').astype(str).applymap(bool)
    df = df[tmp.sum(axis=1) >= 2].reset_index(drop=True)

    eng = df[['현상','원인','조치']].applymap(
    lambda x: False 
              if pd.isna(x) or str(x).strip() == "" 
              else bool(re.fullmatch(r"[A-Za-z\s]+", str(x).strip()))
)

    # 순수 영어로만 이루어진 행만 삭제합니다. (Tilde ~ 사용)
    df = df[~eng.any(axis=1)].reset_index(drop=True)

    # 1) gibberish(말 안 되는) 판단 함수
    def is_gibberish(text: str) -> bool:
        txt = str(text).strip()
        # 빈값
        if not txt or re.fullmatch(r'[\d\W]+', txt) or re.fullmatch(r'[ㄱ-ㅎㅏ-ㅣ]+', txt) or len(txt) < 2:
            return True
        return False

    mask = df.apply(
        lambda row: any(is_gibberish(row[c]) for c in ['현상','원인','조치']),
        axis=1
    )
    df_clean = df[~mask].reset_index(drop=True)


    # 컬럼 순서 정리
    ordered = ['종류','Site','호기','Machine','Unit',"Assy'",
               '발생시간','조치완료','조치 진행 시간(분)',
               '작업자','현상','원인','조치']
    return df[ordered], None


df_ = load_sheet_data()