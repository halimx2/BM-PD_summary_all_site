import re
from datetime import datetime
import pandas as pd

# 채팅 라인 정규표현식
chat_line_pattern = re.compile(
    r"^((?:\d{4}\.\s*\d{1,2}\.\s*\d{1,2}\.)|(?:\d{4}년\s*\d{1,2}월\s*\d{1,2}일))"
    r"\s*(오전|오후)\s*(\d{1,2}:\d{2}),?\s*(.+?)\s*[:：]\s*(.+)$"
)
# 알림/입장 통보 패턴
notification_pattern = re.compile(r"^\d{4}년?\.? .*?\d{1,2}월.*?:$")

# 리포트 시작 패턴
report_pattern = re.compile(r"부동&작업\s*공유")

# 내부 알림성 날짜-시간 패턴 (메시지 내부)
skip_inner_pattern = re.compile(
    r"^(?:\d{4}\.\s*\d{1,2}\.\s*\d{1,2}\.)\s*(?:오전|오후)\s*\d{1,2}:\d{2}:."
)

def convert_to_24h(time_str, period):
    """오전/오후 + HH:MM -> 24시간 HH:MM"""
    hour, minute = map(int, time_str.split(':'))
    if period == '오후' and hour != 12:
        hour += 12
    if period == '오전' and hour == 12:
        hour = 0
    return f"{hour:02}:{minute:02}"


def parse_chat_lines(lines):
    """
    리스트 형태의 채팅 텍스트(한 줄씩)에서 메시지 dict 리스트 생성
    각 dict: {'date': date, 'sender': str, 'time': 'HH:MM', 'message': str}
    """
    results = []
    current_date = None
    current_sender = None
    current_time = None
    current_message = ""

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if re.match(r'^\d{4}년', line):
            continue
        if notification_pattern.match(line):
            continue

        m = chat_line_pattern.match(line)
        if m:
            # 이전 메시지 저장
            if current_message:
                results.append({
                    'date': current_date,
                    'sender': current_sender,
                    'time': current_time,
                    'message': current_message.strip()
                })
            date_str, period, time_str, sender, message = m.groups()
            # 날짜 파싱
            if '년' in date_str:
                current_date = datetime.strptime(date_str, "%Y년 %m월 %d일").date()
            else:
                current_date = datetime.strptime(date_str, "%Y. %m. %d.").date()
            current_sender = sender.strip()
            current_time = convert_to_24h(time_str, period)
            current_message = message.strip()
        elif current_message:
            current_message += f"\n{line}"

    # 마지막 메시지
    if current_message:
        results.append({
            'date': current_date,
            'sender': current_sender,
            'time': current_time,
            'message': current_message.strip()
        })
    return results


def parse_chat_file(filepath):
    """파일 경로로부터 채팅 메시지 파싱"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return parse_chat_lines(lines)


def parse_chat_text(text):
    """텍스트 블록으로부터 채팅 메시지 파싱"""
    lines = text.splitlines()
    return parse_chat_lines(lines)


import re
from datetime import datetime
import pandas as pd

# 리포트 시작 패턴
report_pattern = re.compile(r"\[?부동&작업\s*공유\]?")
# 메시지 내부 스킵 패턴 (불필요한 타임스탬프)
skip_inner_pattern = re.compile(
    r"^(?:\d{4}\.\s*\d{1,2}\.\s*\d{1,2}\.)\s*(?:오전|오후)\s*\d{1,2}:\d{2}:."
)
# 오전/오후 + HH:MM → 24시 HH:MM
def convert_to_24h(time_str: str, period: str) -> str:
    h, m = map(int, time_str.split(':'))
    if period == '오후' and h != 12: h += 12
    if period == '오전' and h == 12: h = 0
    return f"{h:02}:{m:02}"

def extract_report_data(messages):
    """
    messages: list of dicts with keys ['date','sender','time','message']
    returns: DataFrame with columns:
      ['날짜','종류','0. Site','1. 호기','2-1. Machine','2-2. Unit',
       "2-3. Assy'",'3-1. 발생시간','3-2. 조치완료',
       '4. 작업자','5. 현상','6. 원인','7. 조치']
    """
    # 1) 컬럼 정의 (순서 고정)
    cols = [
        "종류",
        "0. Site",
        "1. 호기",
        "2-1. Machine",
        "2-2. Unit",
        "2-3. Assy'",
        "3-1. 발생시간",
        "3-2. 조치완료",
        "4. 작업자",
        "5. 현상",
        "6. 원인",
        "7. 조치",
    ]
    time_val_pattern = re.compile(r"(오전|오후)\s*(\d{1,2}:\d{2})")

    records = []
    for msg in messages:
        text = msg['message']
        # 리포트 블록이 아니면 건너뛰기
        if not report_pattern.search(text):
            continue

        # 빈값 초기화
        data = {c: "" for c in cols}
        # 각 줄 파싱
        for raw in text.splitlines():
            line = raw.strip()
            if not line or skip_inner_pattern.match(line) or ':' not in line:
                continue
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            # 컬럼 순서에 없는 키는 무시
            if key not in data:
                continue
            # 시간 필드 변환
            if key in ("3-1. 발생시간", "3-2. 조치완료"):
                m = time_val_pattern.search(val)
                if m:
                    period, tstr = m.groups()
                    val = convert_to_24h(tstr, period)
            data[key] = val

        # 날짜 필드 추가
        data['날짜'] = msg['date']
        records.append(data)

    # DataFrame 생성 (날짜 컬럼을 앞에 두고 나머지 cols 순서 유지)
    df = pd.DataFrame(records, columns=['날짜'] + cols)
    return df

