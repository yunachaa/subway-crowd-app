import streamlit as st
import pandas as pd
import datetime
import math

# ------------------- 회귀식 계수 --------------------
coefficients = {
    "강남":  [-7548.7568, 1692.1847, -50.0100, -323.5538, -9.2502],
    "서울역": [-3513.2458, 819.5735, -26.8271, -80.6853, 8.9737],
    "사당":   [-117.5344, 337.1758, -12.3019, -61.4697, 9.5399],
    "홍대입구": [-5115.8516, 1080.5163, -30.0831, 85.3852, 19.9417],
}

# ------------------- CDI 최대값 (상위 5개 평균 기반) --------------------
cdi_max_values = {
    "강남": 14353.4,
    "서울역": 10099.0,
    "사당": 5620.2,
    "홍대입구": 9476.4
}

# ------------------- 혼잡도 등급 --------------------
def get_congestion_level(cdi):
    if cdi >= 0.9:
        return "매우혼잡"
    elif cdi >= 0.7:
        return "혼잡"
    elif cdi >= 0.5:
        return "약간혼잡"
    elif cdi >= 0.3:
        return "보통"
    else:
        return "여유"

# ------------------- 예측 함수 --------------------
def predict_passenger(station, hour, minute, weekday, month):
    if hour < 5:
        hour = 5
        minute = 0
    t = hour + (minute / 60)
    a, b, c, d, e = coefficients[station]
    result = a + b*t + c*(t**2) + d*weekday + e*month
    return max(result, 0)  # 음수 방지

# ------------------- 추천 시간대 생성 --------------------
def recommend_times(station, input_hour, input_minute, weekday, month):
    base_time = input_hour + input_minute / 60
    candidates = []
    for i in range(-6, 7):  # ±30분 범위
        t = base_time + i * 5 / 60
        h = int(t)
        m = int(round((t - h) * 60))
        if h < 0 or h >= 24:
            continue
        pred = predict_passenger(station, h, m, weekday, month)
        cdi = pred / cdi_max_values[station]
        level = get_congestion_level(cdi)
        candidates.append((h, m, pred, cdi, level))
    
    candidates.sort(key=lambda x: x[3])  # CDI 낮은 순
    return candidates[:3]

# ------------------- Streamlit UI --------------------
st.markdown("<h1 style='text-align: center; color: white; background-color: pink; padding: 10px; border-radius: 10px;'>지하철 혼잡도 분석</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**역 선택**")
    station = st.selectbox("", ["강남", "서울역", "사당", "홍대입구"])

with col2:
    st.markdown("**날짜 선택**")
    date = st.date_input("", datetime.date(2025, 9, 21))

with col3:
    st.markdown("**시간 선택**")
    time = st.time_input("", datetime.time(17, 30))

if st.button("검색"):
    hour = time.hour
    minute = time.minute
    weekday = date.weekday()  # 월=0 ~ 일=6
    month = date.month

    # 예측
    pred = predict_passenger(station, hour, minute, weekday, month)
    cdi = pred / cdi_max_values[station]
    level = get_congestion_level(cdi)

    # 추천
    recommendations = recommend_times(station, hour, minute, weekday, month)

    # 결과 화면
    st.markdown(f"<div style='border:2px solid black; padding:10px'><h3>{station}</h3></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='border:2px solid black; padding:10px'><h4>현재 시간: {hour:02}:{minute:02}</h4></div>", unsafe_allow_html=True)

    st.markdown(f"### 🚦 현재 혼잡도: <span style='color:red'>{level}</span>", unsafe_allow_html=True)
    st.markdown(f"예상 인원: **{int(pred):,}명**")
    st.markdown(f"CDI (혼잡도 지수): `{cdi:.3f}`")

    st.markdown("---")
    st.markdown("### ⏰ 추천 시간대 (혼잡도 낮은 순)")

    for h, m, p, ci, lv in recommendations:
        st.markdown(f"- {h:02}:{m:02} → `{lv}` / {int(p):,}명 / CDI: `{ci:.3f}`")

    st.markdown("---")
    st.markdown("### ℹ️ 혼잡도 등급 기준")
    st.markdown("""
    - 매우혼잡: CDI ≥ 0.9  
    - 혼잡: 0.7 ≤ CDI < 0.9  
    - 약간혼잡: 0.5 ≤ CDI < 0.7  
    - 보통: 0.3 ≤ CDI < 0.5  
    - 여유: CDI < 0.3  
    """)

    st.markdown("<br><br><a href='https://gptonline.ai/ko/' target='_blank'>🔗 GPT ONLINE 바로가기</a>", unsafe_allow_html=True)
