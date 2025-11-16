import streamlit as st
import pandas as pd
import datetime
import numpy as np

# 혼잡도 계산 함수
def calculate_passenger_count(station, hour, minute, weekday, month):
    time = hour + minute / 60

    # 새벽 시간 보정: 0~5시는 모두 5시로 처리
    if time < 5:
        time = 5

    time_squared = time ** 2
    weekday = int(weekday)
    month = int(month)

    if station == "강남역":
        y = -7548.7568 + 1692.1847 * time - 50.0100 * time_squared - 323.5538 * weekday - 9.2502 * month
        max_val = 6923
    elif station == "서울역":
        y = -3513.2458 + 819.5735 * time - 26.8271 * time_squared - 80.6853 * weekday + 8.9737 * month
        max_val = 3287
    elif station == "사당역":
        y = -117.5344 + 337.1758 * time - 12.3019 * time_squared - 61.4697 * weekday + 9.5399 * month
        max_val = 1938
    elif station == "홍대입구역":
        y = -5115.8516 + 1080.5163 * time - 30.0831 * time_squared + 85.3852 * weekday + 19.9417 * month
        max_val = 4486
    else:
        return 0, 0

    y = max(0, round(y))  # 음수 방지
    cdi = y / max_val
    return y, cdi

# 혼잡도 등급화
def get_crowd_level(cdi):
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

# Streamlit 페이지 구성
st.markdown("<h1 style='text-align:center; border: 3px solid black; padding: 10px;'>지하철 혼잡도 분석</h1>", unsafe_allow_html=True)

with st.form("input_form"):
    col1, col2 = st.columns([1, 4])

    with col1:
        st.markdown("**<span style='background-color:#ffffcc;'>역 선택</span>**", unsafe_allow_html=True)
    with col2:
        station = st.selectbox("", ["강남역", "서울역", "사당역", "홍대입구역"], index=1)

    with col1:
        st.markdown("**<span style='background-color:#ffffcc;'>날짜</span>**", unsafe_allow_html=True)
    with col2:
        date = st.date_input("", datetime.date(2025, 9, 21))

    with col1:
        st.markdown("**<span style='background-color:#ffffcc;'>시간</span>**", unsafe_allow_html=True)
    with col2:
        hour = st.number_input("시", min_value=0, max_value=23, value=17, step=1)
        minute = st.number_input("분", min_value=0, max_value=59, value=30, step=1)

    submitted = st.form_submit_button("검색")

if submitted:
    weekday = date.weekday()
    month = date.month
    passenger, cdi = calculate_passenger_count(station, hour, minute, weekday, month)
    level = get_crowd_level(cdi)
    now_time = datetime.datetime.now().strftime("%H:%M")

    # 출력 상단: 역 이름 + 현재 시간
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div style='border: 2px solid black; padding: 10px; text-align:center; font-weight:bold'>{station}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='border: 2px solid black; padding: 10px; text-align:center; font-weight:bold'>{now_time}</div>", unsafe_allow_html=True)

    # 현재 혼잡도 표시
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<span style='font-weight:bold;'>현재 혼잡도:</span> "
                f"<span style='border: 2px solid black; background-color:{'#ff9999' if level=='매우혼잡' else 'white'}; padding: 5px;'>{level}</span> "
                f"<span style='border:1px solid black; padding:5px;'>혼잡</span> "
                f"<span style='border:1px solid black; padding:5px;'>약간혼잡</span> "
                f"<span style='border:1px solid black; padding:5px;'>보통</span> "
                f"<span style='border:1px solid black; padding:5px;'>여유</span>", unsafe_allow_html=True)

    st.markdown(f"<br>예상 인원: <b>{passenger:,}명</b>", unsafe_allow_html=True)

    # 추천 시간대
    st.markdown("<h3 style='margin-top:40px;'>추천 시간대</h3>", unsafe_allow_html=True)
    base_time = hour + minute / 60

    candidates = []
    for offset in range(-30, 31, 5):
        t = base_time + offset / 60
        t = max(5, min(t, 23.99))  # 시간 범위 제한
        h = int(t)
        m = int(round((t - h) * 60))
        pred, cdi_cand = calculate_passenger_count(station, h, m, weekday, month)
        lvl = get_crowd_level(cdi_cand)
        candidates.append((f"{h:02d}:{m:02d}", lvl, cdi_cand))

    # 혼잡도 낮은 3개 시간 추천
    candidates.sort(key=lambda x: x[2])
    top3 = candidates[:3]

    col1, col2, col3 = st.columns(3)
    for i, (t, lvl, cdi_val) in enumerate(top3):
        with [col1, col2, col3][i]:
            st.markdown(f"<div style='border:2px solid black; text-align:center; font-size:20px; padding:10px'>{t}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center'>{lvl} (CDI: {cdi_val:.2f})</div>", unsafe_allow_html=True)

    # 혼잡도 기준 설명 박스
    st.markdown("""
    <br>
    <div style='border:1px solid black; padding:10px;'>
    <b>혼잡도 구간 기준 (CDI):</b><br>
    매우혼잡: ≥ 0.8<br>
    혼잡: 0.6 ~ 0.8<br>
    약간혼잡: 0.4 ~ 0.6<br>
    보통: 0.2 ~ 0.4<br>
    여유: < 0.2
    </div>
    """, unsafe_allow_html=True)

    # 다시 하기 버튼
    st.markdown("<br><div style='text-align:right;'><button onclick='window.location.reload()'>다시 하기</button></div>", unsafe_allow_html=True)
