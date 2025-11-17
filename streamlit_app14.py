import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(layout="centered")
st.markdown("<h1 style='text-align: center; background-color: pink; padding: 10px; border-radius: 10px;'>지하철 혼잡도 분석</h1>", unsafe_allow_html=True)

역목록 = ['강남', '서울역', '사당', '홍대입구']
혼잡도_기준 = {
    '강남': 7382,
    '서울역': 3283,
    '사당': 3001,
    '홍대입구': 6419
}

# 입력창
with st.form("input_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div style='background-color:lightyellow;padding:5px;'>역 선택</div>", unsafe_allow_html=True)
        selected_station = st.selectbox("", 역목록, index=1)
    with col2:
        st.markdown("<div style='background-color:lightyellow;padding:5px;'>날짜 선택</div>", unsafe_allow_html=True)
        date = st.date_input("", value=pd.to_datetime("2025-09-21"))
    with col3:
        st.markdown("<div style='background-color:lightyellow;padding:5px;'>시간 선택</div>", unsafe_allow_html=True)
        hour = st.number_input("시", min_value=0, max_value=23, value=17, step=1)
        minute = st.number_input("분", min_value=0, max_value=59, value=30, step=1)
    
    submitted = st.form_submit_button("검색")

if submitted:
    time_decimal = hour + minute / 60
    time_decimal = max(time_decimal, 5)  # 5시 이전 시간 보정
    weekday = date.weekday()  # 월=0
    month = date.month

    # 회귀식 정의
    def predict(station):
        if station == '강남':
            return -7548.7568 + 1692.1847*time_decimal - 50.0100*time_decimal**2 - 323.5538*weekday - 9.2502*month
        elif station == '서울역':
            return -3513.2458 + 819.5735*time_decimal - 26.8271*time_decimal**2 - 80.6853*weekday + 8.9737*month
        elif station == '사당':
            return -117.5344 + 337.1758*time_decimal - 12.3019*time_decimal**2 - 61.4697*weekday + 9.5399*month
        elif station == '홍대입구':
            return -5115.8516 + 1080.5163*time_decimal - 30.0831*time_decimal**2 + 85.3852*weekday + 19.9417*month

    pred = predict(selected_station)
    pred = max(0, int(pred))  # 음수 방지

    max_value = 혼잡도_기준[selected_station]
    CDI = round(pred / max_value, 2)

    # 혼잡도 등급
    def get_level(cdi):
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

    level = get_level(CDI)

    # 현재 정보 박스
    st.markdown(f"""
    <div style='display:flex; justify-content: space-between; border: 2px solid black; padding: 10px; margin-bottom: 10px;'>
        <div><b>{selected_station}</b></div>
        <div><b>{hour:02}:{minute:02}</b></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 현재 혼잡도")

    levels = ["매우혼잡", "혼잡", "약간혼잡", "보통", "여유"]
    level_display = ""
    for l in levels:
        if l == level:
            level_display += f"<span style='border:2px solid red; padding:4px; margin-right:10px;'>{l}</span>"
        else:
            level_display += f"<span style='padding:4px; margin-right:10px;'>{l}</span>"
    st.markdown(level_display, unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:18px;'>예상 인원: <b>{pred}명</b></p><p>CDI (혼잡도 지수): <b>{CDI}</b></p>", unsafe_allow_html=True)

    # CDI 기준표
    st.markdown("""
    <div style='border: 1px solid gray; padding: 10px; margin-top: 10px;'>
    <b>CDI 기준표:</b><br>
    0.75 이상: 매우혼잡<br>
    0.6~0.75: 혼잡<br>
    0.45~0.6: 약간혼잡<br>
    0.3~0.45: 보통<br>
    0.3 미만: 여유
    </div>
    """, unsafe_allow_html=True)

    # 추천 시간대 (±30분, 5분 간격)
    candidate_times = [time_decimal + i/60 for i in range(-30, 31, 5) if 0 <= time_decimal + i/60 <= 23.99]
    recommendations = []
    for t in candidate_times:
        if t == time_decimal:
            continue
        if selected_station == '강남':
            p = -7548.7568 + 1692.1847*t - 50.0100*t**2 - 323.5538*weekday - 9.2502*month
        elif selected_station == '서울역':
            p = -3513.2458 + 819.5735*t - 26.8271*t**2 - 80.6853*weekday + 8.9737*month
        elif selected_station == '사당':
            p = -117.5344 + 337.1758*t - 12.3019*t**2 - 61.4697*weekday + 9.5399*month
        elif selected_station == '홍대입구':
            p = -5115.8516 + 1080.5163*t - 30.0831*t**2 + 85.3852*weekday + 19.9417*month
        p = max(0, int(p))
        cdi = round(p / max_value, 2)
        if cdi < CDI:
            recommendations.append((t, cdi, p))

    recommendations = sorted(recommendations, key=lambda x: x[1])[:3]

    st.markdown("### 추천 시간대")
    for r in recommendations:
        h = int(r[0])
        m = int(round((r[0] - h) * 60))
        lvl = get_level(r[1])
        st.markdown(f"<div style='border:2px solid black;padding:8px;width:180px;margin:5px 0;'>⏱️ {h:02}:{m:02} - {lvl}<br>예상 인원: {r[2]}명, CDI: {r[1]}</div>", unsafe_allow_html=True)

    # 다시 하기 버튼
    if st.button("다시 하기"):
        st.experimental_rerun()
