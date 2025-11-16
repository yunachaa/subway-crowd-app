import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import calendar

# ------------------------
# ✅ 스타일 설정
st.set_page_config(page_title="지하철 혼잡도 분석", layout="wide")

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
# ✅ 제목 및 입력 UI

st.markdown("<h1 style='text-align:center;'>지하철 혼잡도 분석</h1>", unsafe_allow_html=True)
with st.container():
    with st.form("input_form"):
        st.markdown("<div class='input-box'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("<div class='label'>역 선택</div>", unsafe_allow_html=True)
            station = st.selectbox("", ["강남", "서울역", "사당", "홍대입구"], index=1)

        with col2:
            st.markdown("<div class='label'>날짜 선택</div>", unsafe_allow_html=True)
            year = st.selectbox("연도", [2025], index=0)
            month = st.selectbox("월", list(range(1, 13)), index=8)
            day = st.selectbox("일", list(range(1, calendar.monthrange(year, month)[1]+1)), index=20)

        with col3:
            st.markdown("<div class='label'>시간 선택</div>", unsafe_allow_html=True)
            hour = st.selectbox("시", list(range(0, 24)), index=17)
            minute = st.selectbox("분", list(range(0, 60)), index=30)

        submitted = st.form_submit_button("검색")
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------
# ✅ 회귀식 정의
def predict_passenger(station, hour, minute, weekday, month):
    time_float = hour + (minute / 60)
    time_sq = time_float ** 2

    if station == "강남":
        y = -7548.7568 + 1692.1847 * time_float - 50.0100 * time_sq - 323.5538 * weekday - 9.2502 * month
        max_val = 14353.4
    elif station == "서울역":
        y = -3513.2458 + 819.5735 * time_float - 26.8271 * ti*_*
