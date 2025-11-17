import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(layout="wide")

# -----------------------------
# 회귀 계수 정의
# -----------------------------
coeffs = {
    '강남역': {
        'const': -7548.7568,
        'time': 1692.1847,
        'time2': -50.0100,
        'day': -323.5538,
        'month': -9.2502,
        'threshold': 5974
    },
    '서울역': {
        'const': -3513.2458,
        'time': 819.5735,
        'time2': -26.8271,
        'day': -80.6853,
        'month': 8.9737,
        'threshold': 2660
    },
    '사당역': {
        'const': -117.5344,
        'time': 337.1758,
        'time2': -12.3019,
        'day': -61.4697,
        'month': 9.5399,
        'threshold': 2164
    },
    '홍대입구역': {
        'const': -5115.8516,
        'time': 1080.5163,
        'time2': -30.0831,
        'day': 85.3852,
        'month': 19.9417,
        'threshold': 4951
    }
}

# -----------------------------
# 혼잡도 등급 정의
# -----------------------------
def get_cdi_level(cdi):
    if cdi >= 0.75:
        return "매우혼잡"
    elif cdi >= 0.6:
        return "혼잡"
    elif cdi >= 0.45:
        return "약간혼잡"
    elif cdi >= 0.3:
        return "보통"
    else:
        return "여유"

def get_color(level):
    return {
        "매우혼잡": "red",
        "혼잡": "orange",
        "약간혼잡": "yellow",
        "보통": "lightgreen",
        "여유": "lightblue"
    }.get(level, "white")

# -----------------------------
# 예측 함수
# -----------------------------
def predict(station, time, weekday, month):
    c = coeffs[station]
    y = (c['const'] +
         c['time'] * time +
         c['time2'] * (time**2) +
         c['day'] * weekday +
         c['month'] * month)
    return max(0, round(y))  # 음수 제거

# -----------------------------
# CDI 계산
# -----------------------------
def compute_cdi(station, predicted):
    threshold = coeffs[station]['threshold']
    cdi = predicted / threshold
    return round(cdi, 2), get_cdi_level(cdi)

# -----------------------------
# 추천 시간대 계산
# -----------------------------
def recommend_times(station, base_time, weekday, month):
    times = [base_time + offset for offset in [-0.25, 0.25, 0.5]]
    valid_times = []
    for t in times:
        t = round(t, 2)
        pred = predict(station, t, weekday, month)
        cdi, level = compute_cdi(station, pred)
        valid_times.append((t, level, cdi))
    return valid_times

# -----------------------------
# UI 구성
# -----------------------------

with st.container():
    st.markdown("""
    <div style="background-color:pink; padding: 20px; border-radius: 10px; border:2px solid black">
        <h1 style="color:black; text-align:center;">지하철 혼잡도 분석</h1>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div style="background-color:lightyellow; padding:5px; font-weight:bold;">역 선택</div>', unsafe_allow_html=True)
        station = st.selectbox("", list(coeffs.keys()), index=1)

    with col2:
        st.markdown('<div style="background-color:lightyellow; padding:5px; font-weight:bold;">날짜 선택</div>', unsafe_allow_html=True)
        date = st.date_input("", datetime(2025, 9, 21))

    with col3:
        st.markdown('<div style="background-color:lightyellow; padding:5px; font-weight:bold;">시 선택</div>', unsafe_allow_html=True)
        hour = st.number_input("시", min_value=0, max_value=23, value=17)

    with col4:
        st.markdown('<div style="background-color:lightyellow; padding:5px; font-weight:bold;">분 선택</div>', unsafe_allow_html=True)
        minute = st.number_input("분", min_value=0, max_value=59, value=30)

    submitted = st.button("검색")

# -----------------------------
# 검색 결과 출력
# -----------------------------
if submitted:
    # 시간 처리
    input_time = hour + (minute / 60)
    if input_time < 5:
        input_time = 5.0

    weekday = date.weekday()
    month = date.month

    pred = predict(station, input_time, weekday, month)
    cdi, level = compute_cdi(station, pred)

    # 결과 박스
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown(f"""
        <div style="border:2px solid black; padding:10px; font-size:20px;">
        🚇 <b>{station}</b>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        now = datetime.now().strftime("%H:%M")
        st.markdown(f"""
        <div style="border:2px solid black; padding:10px; font-size:20px;">
        ⏰ 현재 시간: <b>{now}</b>
        </div>
        """, unsafe_allow_html=True)

    # 혼잡도 결과
    st.markdown("## 현재 혼잡도")
    st.markdown(f"""
    <div style="border:2px solid {get_color(level)}; padding:15px; font-size:18px;">
        ✅ 혼잡도 단계: <b style="color:{get_color(level)};">{level}</b>  
        <br/>🔢 혼잡도 지수 (CDI): <b>{cdi}</b>  
        <br/>👥 예상 인원 수: <b>{pred:,}명</b>
    </div>
    """, unsafe_allow_html=True)

    # 추천 시간대
    st.markdown("## 추천 시간대")

    recs = recommend_times(station, input_time, weekday, month)
    for t, lv, cdi_score in recs:
        mins = int((t % 1) * 60)
        h = int(t)
        time_str = f"{h:02d}:{mins:02d}"
        st.markdown(f"""
        <div style="border:2px solid {get_color(lv)}; padding:10px; margin:5px;">
            🕒 <b>{time_str}</b>  
            <br/>혼잡도: <b style="color:{get_color(lv)};">{lv}</b>  
            <br/>CDI: {cdi_score}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 다시 하기")
    st.button("다시 하기")
