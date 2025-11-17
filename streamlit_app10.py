import streamlit as st
import pandas as pd
import numpy as np
import datetime

# ---------------------- 회귀식 함수 ----------------------

def predict_passengers(station, hour, minute, weekday, month):
    t = hour + minute / 60
    t = max(t, 5)  # 새벽 시간 보정

    if station == '강남':
        y = -7548.7568 + 1692.1847*t - 50.0100*t**2 - 323.5538*weekday - 9.2502*month
    elif station == '서울역':
        y = -3513.2458 + 819.5735*t - 26.8271*t**2 - 80.6853*weekday + 8.9737*month
    elif station == '사당':
        y = -117.5344 + 337.1758*t - 12.3019*t**2 - 61.4697*weekday + 9.5399*month
    elif station == '홍대입구':
        y = -5115.8516 + 1080.5163*t - 30.0831*t**2 + 85.3852*weekday + 19.9417*month
    else:
        return 0
    return max(0, y)

# ---------------------- CDI 계산 ----------------------

CDI_max_dict = {
    '강남': 9805,
    '서울역': 4248,
    '사당': 3524,
    '홍대입구': 6821,
}

def get_CDI(station, predicted):
    cdi = predicted / CDI_max_dict[station]
    return round(cdi, 2)

def get_CDI_grade(cdi):
    if cdi >= 0.9:
        return "매우혼잡", "🔴"
    elif cdi >= 0.7:
        return "혼잡", "🟠"
    elif cdi >= 0.5:
        return "약간혼잡", "🟡"
    elif cdi >= 0.3:
        return "보통", "🟢"
    else:
        return "여유", "🔵"

# ---------------------- Streamlit 시작 ----------------------

st.set_page_config(page_title="지하철 혼잡도 분석", layout="centered")

# ---------------------- 입력창 ----------------------

with st.container():
    st.markdown("<div style='border:2px solid black; background-color:#ffe4e1; padding:15px'>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>지하철 혼잡도 분석</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div style='background-color:#fffacd; padding:5px'>역 선택</div>", unsafe_allow_html=True)
        station = st.selectbox("", ['강남', '서울역', '사당', '홍대입구'])

    with col2:
        st.markdown("<div style='background-color:#fffacd; padding:5px'>날짜 선택</div>", unsafe_allow_html=True)
        date = st.date_input("", value=datetime.date(2025, 9, 21))

    with col3:
        st.markdown("<div style='background-color:#fffacd; padding:5px'>시간 선택</div>", unsafe_allow_html=True)
        hour = st.number_input("시", min_value=0, max_value=23, value=17)
        minute = st.number_input("분", min_value=0, max_value=59, value=30)

    submitted = st.button("검색")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- 결과 출력 ----------------------

if submitted:
    weekday = date.weekday()
    month = date.month

    pred = predict_passengers(station, hour, minute, weekday, month)
    cdi = get_CDI(station, pred)
    grade, icon = get_CDI_grade(cdi)

    # 상단 정보
    st.markdown(f"""
    <div style='display: flex; justify-content: space-between; border:2px solid #000; padding:10px'>
        <div><b>{station}</b></div>
        <div><b>현재시간: {hour:02d}:{minute:02d}</b></div>
    </div>
    """, unsafe_allow_html=True)

    # 현재 혼잡도
    st.markdown("<h3>현재 혼잡도</h3>", unsafe_allow_html=True)
    st.markdown(f"현재 상태: <span style='color:red; font-weight:bold'>{grade}</span> ({icon})", unsafe_allow_html=True)
    st.markdown(f"예상 인원: {int(pred):,}명 / CDI: {cdi}")

    # 혼잡도 범례
    st.markdown("""
    <div style='border:1px solid #ccc; padding:10px; margin-top:10px'>
    <b>CDI 기준표</b><br>
    🔴 매우혼잡: 0.90 이상<br>
    🟠 혼잡: 0.70 ~ 0.89<br>
    🟡 약간혼잡: 0.50 ~ 0.69<br>
    🟢 보통: 0.30 ~ 0.49<br>
    🔵 여유: 0.00 ~ 0.29
    </div>
    """, unsafe_allow_html=True)

    # 추천 시간대 생성
    candidates = []
    for delta in [-30, -15, 15, 30, 45]:
        new_minute = minute + delta
        new_hour = hour
        if new_minute < 0:
            new_hour -= 1
            new_minute += 60
        elif new_minute >= 60:
            new_hour += 1
            new_minute -= 60

        t = max(new_hour + new_minute / 60, 5)
        p = predict_passengers(station, new_hour, new_minute, weekday, month)
        c = get_CDI(station, p)
        g, _ = get_CDI_grade(c)
        candidates.append((f"{new_hour:02d}:{new_minute:02d}", g, c))

    # 상위 3개 여유 시간 추천 (CDI 기준 오름차순)
    best = sorted(candidates, key=lambda x: x[2])[:3]

    st.markdown("<h3>추천 시간대</h3>", unsafe_allow_html=True)
    for time_str, g, c in best:
        st.markdown(f"""
        <div style='border:2px solid #aaa; padding:10px; margin:5px'>
        ⏰ {time_str}<br>➡️ {g} (CDI: {c})
        </div>
        """, unsafe_allow_html=True)

    # 다시 하기
    st.markdown("<div style='text-align:right'><button onclick='window.location.reload()'>다시 하기</button></div>", unsafe_allow_html=True)
