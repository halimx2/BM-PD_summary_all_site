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

# 3) ‘site’ 컬럼 자동 감지
cols = df.columns.tolist()
if "site" in cols:
    site_col = "site"
else:
    candidates = [c for c in cols if "사이트" in c or "Site" in c or "SITE" in c]
    if candidates:
        site_col = candidates[0]
        st.warning(f"‘{site_col}’ 컬럼을 사이트 식별용으로 자동 설정했습니다.")
    else:
        st.error(f"사이트 컬럼을 찾을 수 없습니다.\n→ 현재 컬럼 목록: {cols}")
        st.stop()

# 4) 선택된 사이트로 필터링
df_site = df[df[site_col] == selected_site].reset_index(drop=True)

# ───────────── BM25 검색 기능 추가 ─────────────
import io
import pandas as pd
import streamlit as st
from janome.tokenizer import Tokenizer
from rank_bm25 import BM25Okapi

# — (이전 로직: 사이트 선택, df_site 준비) —
import io
import pandas as pd
import streamlit as st
from janome.tokenizer import Tokenizer
from rank_bm25 import BM25Okapi

# — (이전 로직: 사이트 선택, df_site 준비) —

SEARCH_COLS = ["Machine", "Unit", "Assy'", "현상", "원인", "조치"]

@st.cache_data
def make_corpus(df: pd.DataFrame, cols: list[str]) -> list[str]:
    return df[cols].fillna("").astype(str).agg(" ".join, axis=1).tolist()

@st.cache_resource
def build_bm25(corpus: list[str]) -> BM25Okapi:
    tokenizer = Tokenizer()
    tokenized = [
        [t.surface for t in tokenizer.tokenize(doc)]
        for doc in corpus
    ]
    return BM25Okapi(tokenized)

@st.cache_resource
def build_tokenized_corpus(corpus: list[str]) -> list[list[str]]:
    tokenizer = Tokenizer()
    return [
        [t.surface for t in tokenizer.tokenize(doc)]
        for doc in corpus
    ]

# 1) 문서 준비
docs = make_corpus(df_site, SEARCH_COLS)

# 2) BM25 모델 및 토큰화된 코퍼스 생성
bm25 = build_bm25(docs)
tokenized_corpus = build_tokenized_corpus(docs)

# 3) 검색 UI
st.markdown("---")
st.subheader("통합 텍스트 검색")
top_k = st.slider("결과 개수", 1, 100, 5)

query = st.text_input("🔎 검색어 입력")
use_simple = st.checkbox("✅ 키워드 포함 여부로 검색 (단순 필터)", value=False)

if query:
    tokenizer = Tokenizer()
    q_tokens = [t.surface for t in tokenizer.tokenize(query)]
    
    if use_simple:
        # 모든 토큰이 문서에 포함된 행만 골라냄
        matched_idx = [
            i for i, tokens in enumerate(tokenized_corpus)
            if all(q in tokens for q in q_tokens)
        ][:top_k]
        scores = [None] * len(matched_idx)  # 점수 대신 None or 생략 가능
    else:
        # BM25 점수 기반 상위 top_k
        scores_all = bm25.get_scores(q_tokens)
        ranked = sorted(enumerate(scores_all), key=lambda x: x[1], reverse=True)
        matched_idx, scores = zip(*ranked[:top_k])

    # 4) 결과 DataFrame (원본 전 컬럼 + Score)
    result_df = df_site.iloc[list(matched_idx)].copy().reset_index(drop=True)
    result_df["Score"] = scores
    st.table(result_df)

    # 다운로드 버튼 (생략 가능)
    csv_data = result_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 CSV 다운로드", data=csv_data,
                       file_name="search_results.csv", mime="text/csv")
