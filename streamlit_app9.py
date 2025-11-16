import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import calendar

# ------------------------
# 페이지 설정
st.set_page_config(page_title="지하철 혼잡도 분석", layout="wide")

# ------------------------
# CSS 스타일
st.markdown("""
    <style>
    .input-box {
        background-color: #ffe0f0;
        padding: 20px;
        border: 2px solid #cccccc;
        border-radius: 12px;
    }
    .label {
        background-color: #fff6b7;
        padding: 5px 10px;
        border-radius: 5px;
        display: inline-block;
        margin-bottom: 5px;
        font-weight: bold;
    }
    .highlight {
        border: 3px solid red;
        padding: 10px;
        border-radius: 10px;
        background-color: #ffe6e6;
        font-weight: bold;
    }
    .time-box {
        border: 2px solid #999999;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
        text-align: center;
    }
    .header-box {
        display: flex;
        justify-content: space-between;
        font-weight: bold;
        font-size: 20px;
        border: 2px solid #666;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .bottom-box {
        border: 2px dashed #aaa;
        padding: 10px;
        border-radius: 10px;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------
# 제목
st.markdown("<h1 style='text-align:center;'>지하철 혼잡도 분석</h1>", unsafe_allow_html=True)

# ------------------------
# 입력 박스 UI
with st.container():
    with st.form("input_form"):
        st.markdown("<div class='input-box'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        # 역 선택
        with col1:
            st.markdown("<div class='label'>역 선택</div>", unsafe_allow_html=True)
            station = st.selectbox("", ["강남", "서울역", "사당", "홍대입구"], index=1)

        # 날짜 선택
        with col2:
            st.markdown("<div class='label'>날짜 선택</div>", unsafe_allow_html=True)
            year = st.selectbox("연도", [2025], index=0)
            month = st.selectbox("월", list(range(1, 13)), index=8)
            day = st.selectbox("일", list(range(1, calendar.monthrange(year, month)[1] + 1)), index=20)

        # 시간 선택
        with col3:
            st.markdown("<div class='label'>시간 선택</div>", unsafe_allow_html=True)
            hour = st.selectbox("시", list(range(0, 24)), index=17)
            minute = st.selectbox("분", list(range(0, 60)), index=30)

        submitted = st.form_submit_button("검색")
        st.markdown("</div>", unsafe_allow_html=True)


# ------------------------
#  예측 모델 (회귀식)
def predict_passenger(station, hour, minute, weekday, month):
    time_float = hour + minute / 60
    time_sq = time_float ** 2

    # 강남
    if station == "강남":
        y = -7548.7568 + 1692.1847 * time_float - 50.0100 * time_sq - 323.5538 * weekday - 9.2502 * month
        max_val = 14353.4

    # 서울역
    elif station == "서울역":
        y = -3513.2458 + 819.5735 * time_float - 26.8271 * time_sq - 80.6853 * weekday + 8.9737 * month
        max_val = 10099.0

    # 사당
    elif station == "사당":
        y = -117.5344 + 337.1758 * time_float - 12.3019 * time_sq - 61.4697 * weekday + 9.5399 * month
        max_val = 5620.2

    # 홍대입구
    elif station == "홍대입구":
        y = -5115.8516 + 1080.5163 * time_float - 30.0831 * time_sq + 85.3852 * weekday + 19.9417 * month
        max_val = 9476.4

    else:
        y = 0
        max_val = 1

    return max(y, 0), max_val


# ------------------------
# 혼잡도 등급
def get_congestion_grade(cdi):
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


# ------------------------
# 결과 출력
if submitted:

    selected_date = datetime(year, month, day)
    weekday = selected_date.weekday()

    passenger, max_val = predict_passenger(station, hour, minute, weekday, month)
    cdi = passenger / max_val
    grade = get_congestion_grade(cdi)

    # 헤더
    st.markdown(
        f"<div class='header-box'><div>{station}</div><div>{hour:02d}:{minute:02d}</div></div>",
        unsafe_allow_html=True
    )

    # 현재 혼잡도
    st.subheader("현재 혼잡도")
    levels = ["매우혼잡", "혼잡", "약간혼잡", "보통", "여유"]

    for lv in levels:
        if lv == grade:
            st.markdown(f"<div class='highlight'>{lv}</div>", unsafe_allow_html=True)
        else:
            st.write(lv)

    st.write(f"예상 인원 : {int(passenger)}명")
    st.write(f"CDI : {cdi:.2f}")

    # 추천 시간대
    st.subheader("추천 시간대")
    st.markdown("<div class='bottom-box'>", unsafe_allow_html=True)

    base = hour * 60 + minute
    recommend = [base - 10, base + 10, base + 15]

    for t in recommend:
        if t < 0:
            t = 0
        if t > 1439:
            t = 1439
        h, m = divmod(t, 60)
        p, _ = predict_passenger(station, h, m, weekday, month)
        c = p / max_val
        g = get_congestion_grade(c)

        st.markdown(f"<div class='time-box'>{h:02d}:{m:02d}<br>{g} (CDI {c:.2f})</div>",
                    unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.button("다시 하기")
