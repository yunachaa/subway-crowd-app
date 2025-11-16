import streamlit as st
import datetime
import numpy as np
import pandas as pd

# -----------------------------
# 혼잡도 계산 함수 정의
# -----------------------------
def calculate_expected_passengers(station, hour_float, weekday, month):
    coeffs = {
        "강남역": [-7548.7568, 1692.1847, -50.0100, -323.5538, -9.2502],
        "서울역": [-3513.2458, 819.5735, -26.8271, -80.6853, 8.9737],
        "사당역": [-117.5344, 337.1758, -12.3019, -61.4697, 9.5399],
        "홍대입구역": [-5115.8516, 1080.5163, -30.0831, 85.3852, 19.9417],
    }
    
    if station not in coeffs:
        return None

    b0, b1, b2, b3, b4 = coeffs[station]
    passengers = b0 + b1 * hour_float + b2 * hour_float ** 2 + b3 * weekday + b4 * month
    return max(0, int(passengers))  # 음수 방지 처리

# -----------------------------
# 혼잡도 등급 계산 함수 정의
# -----------------------------
def get_cdi(passenger, max_passenger):
    if max_passenger == 0:
        return 0
    return passenger / max_passenger

def get_congestion_level(cdi):
    if cdi >= 0.8:
        return "매우혼잡"
    elif cdi >= 0.6:
        return "혼잡"
    elif cdi >= 0.4:
        return "약간혼잡"
    elif cdi >= 0.2:
        return "보통"
    else:
        return "여유"

# -----------------------------
# 추천 시간대 계산 함수 정의
# -----------------------------
def get_top_3_recommendations(station, hour_float, weekday, month):
    candidates = []
    times = np.arange(hour_float - 0.5, hour_float + 0.5 + 1e-6, 5/60)  # 5분 간격
    for t in times:
        p = calculate_expected_passengers(station, t, weekday, month)
        candidates.append((t, p))
    
    max_p = max([x[1] for x in candidates])
    results = []
    for t, p in candidates:
        cdi = get_cdi(p, max_p)
        level = get_congestion_level(cdi)
        results.append((t, p, level))
    
    results = sorted(results, key=lambda x: x[1])
    top3 = results[:3]
    top3.sort(key=lambda x: x[0])
    return top3

# -----------------------------
# Streamlit UI 구성
# -----------------------------
st.set_page_config(page_title="지하철 혼잡도 분석", layout="centered")

with st.container():
    st.markdown("<h1 style='text-align: center; color: black;'>지하철 혼잡도 분석</h1>", unsafe_allow_html=True)

    st.markdown("<div style='border: 3px solid black; padding: 20px; background-color: white;'>", unsafe_allow_html=True)

    st.markdown("<span style='background-color: #ffffcc; padding: 5px;'>역 선택</span>", unsafe_allow_html=True)
    station = st.selectbox("", ["강남역", "서울역", "사당역", "홍대입구역"], index=1, label_visibility='collapsed')

    st.markdown("<span style='background-color: #ffffcc; padding: 5px;'>날짜</span>", unsafe_allow_html=True)
    date = st.date_input("", datetime.date(2025, 9, 21), label_visibility='collapsed')

    st.markdown("<span style='background-color: #ffffcc; padding: 5px;'>시간</span>", unsafe_allow_html=True)
    hour = st.number_input("시", min_value=5, max_value=23, value=17)
    minute = st.number_input("분", min_value=0, max_value=59, value=30)

    search = st.button("검색")
    st.markdown("</div>", unsafe_allow_html=True)

if search:
    hour_float = hour + minute / 60
    weekday = date.weekday()  # 월=0 ~ 일=6
    month = date.month

    now_passenger = calculate_expected_passengers(station, hour_float, weekday, month)
    max_passenger = calculate_expected_passengers(station, 8.5 if station == '사당역' else 18.5, weekday, month)
    now_cdi = get_cdi(now_passenger, max_passenger)
    now_level = get_congestion_level(now_cdi)

    top3 = get_top_3_recommendations(station, hour_float, weekday, month)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"<div style='border: 2px solid black; text-align: center; font-weight: bold;'>{station}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='border: 2px solid black; text-align: center; font-weight: bold;'>{datetime.datetime.now().strftime('%H:%M')}</div>", unsafe_allow_html=True)

    # 혼잡도 표시
    color_map = {
        "매우혼잡": "#ff6666",
        "혼잡": "#ff9999",
        "약간혼잡": "#ffd966",
        "보통": "#b6d7a8",
        "여유": "#a4c2f4"
    }
    congestion_levels = ["매우혼잡", "혼잡", "약간혼잡", "보통", "여유"]
    color_html = ""
    for level in congestion_levels:
        style = f"border:2px solid black; padding:3px; margin-right:4px;"
        if level == now_level:
            style += f" background-color:{color_map[level]}; font-weight:bold;"
        color_html += f"<span style='{style}'>{level}</span>"

    st.markdown(f"<p style='margin-top:10px;'>현재 혼잡도: {color_html}</p>", unsafe_allow_html=True)
    st.markdown(f"<p>예상 인원: <strong>{now_passenger}</strong>명</p>", unsafe_allow_html=True)

    # 추천 시간대
    st.subheader("추천 시간대")
    labels = ["시간 전", "시간 후", "시간 후"]
    cols = st.columns(3)
    for i in range(3):
        t, p, level = top3[i]
        h = int(t)
        m = int(round((t - h) * 60))
        time_str = f"{h:02d}:{m:02d}"
        with cols[i]:
            st.markdown(f"<div style='border:2px solid black; text-align:center; padding:5px; font-size:20px;'>{time_str}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;'>{level}</div>")

    st.button("다시 하기")