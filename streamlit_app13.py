import streamlit as st
import pandas as pd
from datetime import datetime

# 예측 모델 함수 (간단히 고정된 회귀식 사용 예시)
def predict(station, hour, weekday, month):
    if station == "강남역":
        return -7548.7568 + 1692.1847*hour - 50.01*(hour**2) - 323.5538*weekday - 9.2502*month
    elif station == "서울역":
        return -3513.2458 + 819.5735*hour - 26.8271*(hour**2) - 80.6853*weekday + 8.9737*month
    elif station == "사당역":
        return -117.5344 + 337.1758*hour - 12.3019*(hour**2) - 61.4697*weekday + 9.5399*month
    elif station == "홍대입구역":
        return -5115.8516 + 1080.5163*hour - 30.0831*(hour**2) + 85.3852*weekday + 19.9417*month
    else:
        return 0

# 최대값 (상위 10%) 기준 수동 입력
MAX_VALUES = {
    "강남역": 9180,
    "서울역": 7870,
    "사당역": 6025,
    "홍대입구역": 8572
}

# 혼잡도 CDI 기준표
cdi_levels = [
    (0.75, "매우혼잡", "red"),
    (0.6, "혼잡", "orange"),
    (0.45, "약간혼잡", "yellow"),
    (0.3, "보통", "green"),
    (0.0, "여유", "blue")
]

def compute_cdi(station, predicted):
    max_val = MAX_VALUES[station]
    cdi = predicted / max_val
    for threshold, label, color in cdi_levels:
        if cdi >= threshold:
            return round(cdi, 2), label, color
    return 0.0, "여유", "blue"

def recommend_times_filtered(station, base_time, weekday, month, current_cdi):
    times = [base_time + offset for offset in [-0.25, 0.25, 0.5]]
    valid_times = []
    for t in times:
        t = round(t, 2)
        pred = predict(station, t, weekday, month)
        cdi, level, color = compute_cdi(station, pred)
        if cdi < current_cdi:
            valid_times.append((t, level, cdi, int(pred), color))
    return valid_times

# --- UI START ---
st.set_page_config(page_title="지하철 혼잡도 분석")

with st.container():
    st.markdown("<div style='background-color:#ffc0cb; padding:20px; border-radius:10px;'>"
                "<h1 style='text-align:center; color:black;'>지하철 혼잡도 분석</h1>"
                "</div>", unsafe_allow_html=True)

# 사용자 입력
stations = ["강남역", "서울역", "사당역", "홍대입구역"]
cols = st.columns([1, 1, 1, 1])
station = cols[0].selectbox("역 선택", stations, index=1)
year = cols[1].selectbox("연도", [2024, 2025], index=1)
month = cols[2].selectbox("월", list(range(1, 13)), index=8)
day = cols[3].selectbox("일", list(range(1, 32)), index=20)

col1, col2 = st.columns(2)
hour = col1.selectbox("시간(시)", list(range(0, 24)), index=17)
minute = col2.selectbox("시간(분)", list(range(0, 60)), index=30)

submit = st.button("검색")

if submit:
    input_time = hour + (minute / 60)
    dt = datetime(year, month, day)
    weekday = dt.weekday()  # 0: 월요일
    predicted = predict(station, input_time, weekday, month)
    cdi, level, color = compute_cdi(station, predicted)

    now_string = f"{hour:02d}:{minute:02d}"

    st.markdown(f"<div style='display:flex; justify-content:space-between; padding:10px; border:2px solid black;'>"
                f"<h3>{station}</h3><h3>현재 시간: {now_string}</h3>"
                "</div>", unsafe_allow_html=True)

    st.subheader("현재 혼잡도")
    tags = ""
    for _, tag_label, tag_color in reversed(cdi_levels):
        style = f"color:white; background-color:{tag_color}; padding:5px 10px; margin-right:5px; border-radius:5px;"
        if tag_label == level:
            style += " border:3px solid black;"
        tags += f"<span style='{style}'>{tag_label}</span>"
    st.markdown(tags, unsafe_allow_html=True)

    st.markdown(f"<p style='font-size:18px;'>예상 인원: <b>{int(predicted)}명</b></p>")
    st.markdown(f"<p>CDI (혼잡도 지수): <b>{cdi}</b></p>")

    st.subheader("추천 시간대")
    recommendations = recommend_times_filtered(station, input_time, weekday, month, cdi)

    if recommendations:
        for t, label, rcdi, pred, color in recommendations:
            display_time = f"{int(t):02d}:{int(round((t % 1) * 60)):02d}"
            st.markdown(f"<div style='border:2px solid {color}; padding:10px; margin-bottom:10px;'>"
                        f"<b>{display_time}</b><br>혼잡도: {label} (CDI: {rcdi})<br>예상 인원: {pred}명"
                        "</div>", unsafe_allow_html=True)
    else:
        st.info("현재 시간보다 혼잡도가 낮은 추천 시간대가 없습니다.")

    st.markdown("""
    <hr>
    <h5>혼잡도 등급 기준표 (CDI)</h5>
    <ul>
        <li>0.75 이상: 매우혼잡</li>
        <li>0.60 이상: 혼잡</li>
        <li>0.45 이상: 약간혼잡</li>
        <li>0.30 이상: 보통</li>
        <li>0.30 미만: 여유</li>
    </ul>
    <br>
    <div style='text-align:right;'>
        <button onclick="window.location.reload()" style='padding:10px 15px;'>다시 하기</button>
    </div>
    """, unsafe_allow_html=True)
