# streamlit 앱 구성 - 최종 회귀식 반영
import streamlit as st
import datetime
import numpy as np
from datetime import datetime as dt

# 최종 회귀 계수 (시간^2은 사당만 제외)
coefficients = {
    '서울역':      {'절편': 254.34, '시간': -0.01, '시간^2': -0.30,  '요일': -9.78,  '월': 1.15},
    '강남':        {'절편': 362.50, '시간': 0.01,  '시간^2': 0.29,   '요일': -12.16, '월': -3.24},
    '홍대입구':    {'절편': 859.58, '시간': -0.04, '시간^2': -1.06,  '요일': 56.08,  '월': 0.27},
    '사당':        {'절편': 510.15, '시간': -13.06,'시간^2': 0.00,   '요일': -24.36, '월': 2.12}
}

# CDI 등급 기준
def get_cdi_grade(cdi):
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

# 혼잡도 예측 함수
def predict_passengers(station, hour, minute, weekday, month):
    시간 = hour + minute / 60.0
    if 시간 < 5: 시간 = 5  # 새벽시간 보정
    시간2 = 시간 ** 2 if station != '사당' else 0
    c = coefficients[station]
    y = c['절편'] + c['시간'] * 시간 + c['시간^2'] * 시간2 + c['요일'] * weekday + c['월'] * month
    return max(0, y)

# 최대값 정의 (정규화 기준)
max_values = {'서울역': 2306, '강남': 3472, '홍대입구': 3434, '사당': 1599}

# Streamlit 시작
st.set_page_config(page_title="지하철 혼잡도 분석", layout="centered")
st.markdown("""
    <div style='background-color:pink;padding:10px;border-radius:10px;text-align:center;'>
        <h1 style='color:black;'>지하철 혼잡도 분석</h1>
    </div>
""", unsafe_allow_html=True)

# 입력창 박스 스타일 시작
with st.form("입력창"):
    st.markdown("<div style='background-color:#fff0c2;padding:15px;border:2px solid black;'>", unsafe_allow_html=True)
    역명 = st.selectbox("역 선택", ["서울역", "강남", "홍대입구", "사당"])
    날짜 = st.date_input("날짜 선택", value=datetime.date(2025, 9, 21))
    시간 = st.time_input("시간 선택", value=datetime.time(17, 30))
    제출 = st.form_submit_button("검색")
    st.markdown("</div>", unsafe_allow_html=True)

# 결과
if 제출:
    시 = 시간.hour
    분 = 시간.minute
    요일 = 날짜.weekday()  # 월=0~일=6
    월 = 날짜.month

    현재예측 = predict_passengers(역명, 시, 분, 요일, 월)
    최대 = max_values[역명]
    CDI = 현재예측 / 최대
    등급 = get_cdi_grade(CDI)

    # 추천 시간대 (±30분, 5분 간격)
    후보 = []
    for diff in range(-30, 35, 5):
        후보시간 = dt(2025, 1, 1, 시, 분) + datetime.timedelta(minutes=diff)
        h, m = 후보시간.hour, 후보시간.minute
        pred = predict_passengers(역명, h, m, 요일, 월)
        cdi = pred / 최대
        후보.append((h, m, pred, cdi))

    후보.sort(key=lambda x: x[3])  # CDI 기준 정렬
    추천3 = 후보[:3]

    # 출력 레이아웃
    st.markdown("""
        <div style='display:flex;justify-content:space-between;'>
            <div style='border:2px solid black;padding:10px;'>📍 역명: <b>{}</b></div>
            <div style='border:2px solid black;padding:10px;'>🕒 현재시간: <b>{:02d}:{:02d}</b></div>
        </div>
    """.format(역명, 시, 분), unsafe_allow_html=True)

    st.markdown(f"""
        ### 🚦 현재 혼잡도: <span style='color:red;font-weight:bold'>{등급}</span><br>
        예측 인원: <b>{int(현재예측):,}명</b><br>
        CDI: <b>{CDI:.3f}</b>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("✅ 추천 시간대")
    for h, m, pred, cdi in 추천3:
        st.markdown(f"<div style='border:2px solid black;padding:10px;margin-bottom:10px;'>
            <b>{h:02d}:{m:02d}</b> → <b>{get_cdi_grade(cdi)}</b> (예상 {int(pred):,}명, CDI: {cdi:.3f})</div>", unsafe_allow_html=True)

    # CDI 범위 안내
    st.markdown("""
        <div style='border:1px solid gray;padding:10px;margin-top:20px;'>
            <b>CDI 등급 기준 안내</b><br>
            매우혼잡: ≥ 0.9<br>
            혼잡: 0.7 ~ 0.9<br>
            약간혼잡: 0.5 ~ 0.7<br>
            보통: 0.3 ~ 0.5<br>
            여유: < 0.3
        </div>
    """, unsafe_allow_html=True)

    # 다시하기 버튼
    if st.button("🔁 다시 하기"):
        st.experimental_rerun()
