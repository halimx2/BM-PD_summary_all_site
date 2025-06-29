import io
import requests
import pandas as pd
import streamlit as st
from options import KIND_OPTIONS, SITE_OPTIONS, PROCESS_OPTIONS, UNIT_OPTIONS

import os
from dotenv import load_dotenv
import re

# load_dotenv()   # .env 읽어서 환경변수 등록

# SHEET_ID  = os.getenv("SHEET_ID")
SHEET_ID  = st.secrets["SHEET_ID"]
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json"


@st.cache_data(ttl=300)
def load_sheet_data() -> tuple[pd.DataFrame|None, str|None]:
    resp = requests.get(SHEET_URL)
    if resp.status_code != 200:
        return None, f"❌ 데이터 요청 실패: {resp.status_code}"

    json_str = resp.text[47:-2]
    raw = pd.read_json(io.StringIO(json_str), typ='series')
    rows = raw['table']['rows'][2:]
    values = [[(c.get('v') if isinstance(c, dict) and 'v' in c else '') for c in r.get('c', [])] for r in rows]
    cols = ['종류','Site','호기','Machine','Unit',"Assy'",'발생시간','조치완료시간','작업자','현상','원인','조치']
    df = (pd.DataFrame(values, columns=['Time Stamp']+cols)[cols]
          .drop_duplicates(subset=['발생시간','조치완료시간','작업자','현상'], ignore_index=True))

    # 날짜 파싱
    RE = re.compile(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일\s*(오전|오후)\s*(\d{1,2}):(\d{2})")
    def parse_korean_dt(s: str) -> pd.Timestamp:
        m = RE.match(str(s))
        if not m:
            return pd.NaT
        year, mon, day, ampm, hr, mi = m.groups()
        y, mo, d = map(int, (year, mon, day))
        h, mi = int(hr), int(mi)
        if ampm=='오후' and h < 12:
            h += 12
        if ampm=='오전' and h == 12:
            h = 0
        return pd.Timestamp(y, mo, d, h, mi)

    df[['발생시간','조치완료시간']] = df[['발생시간','조치완료시간']].applymap(parse_korean_dt)

    # 기본 조치 진행 시간 계산
    df['조치 진행 시간(분)'] = ((df['조치완료시간'] - df['발생시간'])
                               .dt.total_seconds().div(60).round().astype('Int64'))

    # 이상치 보정: 조치 진행 시간이 음수인 경우
    neg_mask = df['조치 진행 시간(분)'] < 0
    # 1) 절대값 ≥ 1200: 조치완료시간을 다음날로
    mask1 = neg_mask & (df['조치 진행 시간(분)'].abs() >= 1200)
    df.loc[mask1, '조치완료시간'] = df.loc[mask1, '조치완료시간'] + timedelta(days=1)
    # 2) 절대값 ≤ 300: 발생시간과 조치완료시간 스와핑
    mask2 = neg_mask & (df['조치 진행 시간(분)'].abs() <= 300)
    df.loc[mask2, ['발생시간','조치완료시간']] = df.loc[mask2, ['조치완료시간','발생시간']].values

    # 보정 후 재계산
    df['조치 진행 시간(분)'] = ((df['조치완료시간'] - df['발생시간'])
                               .dt.total_seconds().div(60).round().astype('Int64'))

    # 현상/원인/조치 필터 (빈값 2개 이상 제거)
    tmp = df[['현상','원인','조치']].fillna('').astype(str).applymap(bool)
    df = df[tmp.sum(axis=1) >= 2].reset_index(drop=True)
    # 완전 영어만인 행 제거
    eng = df[['현상','원인','조치']].applymap(lambda x: bool(re.fullmatch(r"[A-Za-z\s]+", x.strip())))
    df = df[~eng.any(axis=1)].reset_index(drop=True)

    # 컬럼 순서
    ordered = ['종류','Site','호기','Machine','Unit',"Assy'",
               '발생시간','조치완료시간','조치 진행 시간(분)',
               '작업자','현상','원인','조치']
    return df[ordered], None


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

# 데이터 로드 및 전처리 함수
@st.cache_data(ttl=300)
def load_sheet_data() -> tuple[pd.DataFrame|None, str|None]:
    resp = requests.get(SHEET_URL)
    if resp.status_code != 200:
        return None, f"❌ 데이터 요청 실패: {resp.status_code}"

    # JSONP 제거 및 JSON 파싱
    json_str = resp.text[47:-2]
    raw = pd.read_json(io.StringIO(json_str), typ='series')
    rows = raw['table']['rows'][2:]

    # 2차원 리스트화
    values = [[(c.get('v') if isinstance(c, dict) and 'v' in c else '')
               for c in r.get('c', [])] for r in rows]

    cols = ['종류','Site','호기','Machine','Unit',"Assy'",
            '발생시간','조치완료시간','작업자','현상','원인','조치']
    df = (pd.DataFrame(values, columns=['Time Stamp'] + cols)[cols]
          .drop_duplicates(subset=['발생시간','조치완료시간','작업자','현상'],
                            ignore_index=True))

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

    df[['발생시간','조치완료시간']] = df[['발생시간','조치완료시간']].applymap(parse_korean_dt)

    # 초기 조치시간 계산(분)
    df['조치 진행 시간(분)'] = ((df['조치완료시간'] - df['발생시간'])
                               .dt.total_seconds().div(60).round().astype('Int64'))

    # 음수 보정: 이전 로직 (300 이하 스와핑, 1200 이상 다음날)
    neg = df['조치 진행 시간(분)'] < 0
    mask1 = neg & (df['조치 진행 시간(분)'].abs() >= 1200)
    df.loc[mask1, '조치완료시간'] += timedelta(days=1)
    mask2 = neg & (df['조치 진행 시간(분)'].abs() <= 300)
    df.loc[mask2, ['발생시간','조치완료시간']] = df.loc[mask2, ['조치완료시간','발생시간']].values

    # 재계산
    df['조치 진행 시간(분)'] = ((df['조치완료시간'] - df['발생시간'])
                               .dt.total_seconds().div(60).round().astype('Int64'))

    # 신규 보정: 1400 초과 경우 날짜만 발생일로 교체
    mask3 = df['조치 진행 시간(분)'] > 1400
    df.loc[mask3, '조치완료시간'] = df.loc[mask3].apply(
        lambda r: r['조치완료시간'].replace(
            year=r['발생시간'].year,
            month=r['발생시간'].month,
            day=r['발생시간'].day
        ), axis=1
    )

    # 재계산 최종
    df['조치 진행 시간(분)'] = ((df['조치완료시간'] - df['발생시간'])
                               .dt.total_seconds().div(60).round().astype('Int64'))

    # 현상/원인/조치 필터
    tmp = df[['현상','원인','조치']].fillna('').astype(str).applymap(bool)
    df = df[tmp.sum(axis=1) >= 2].reset_index(drop=True)
    eng = df[['현상','원인','조치']].applymap(
        lambda x: bool(re.fullmatch(r"[A-Za-z\s]+", x.strip()))
    )
    df = df[~eng.any(axis=1)].reset_index(drop=True)

    # 컬럼 순서 정리
    ordered = ['종류','Site','호기','Machine','Unit',"Assy'",
               '발생시간','조치완료시간','조치 진행 시간(분)',
               '작업자','현상','원인','조치']
    return df[ordered], None
