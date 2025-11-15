import streamlit as st
from datetime import datetime
import numpy as np

st.set_page_config(page_title="지하철 혼잡도 분석기")

st.title("지하철 혼잡도 분석")

역 = st.selectbox("역 선택", ["서울역", "강남역", "사당역", "홍대입구역"])
날짜 = st.date_input("날짜", datetime(2025, 9, 21))
시간 = st.time_input("시간", datetime.strptime("17:30", "%H:%M").time())

if st.button("검색"):
    시간_실수 = 시간.hour + 시간.minute / 60
    요일 = 날짜.weekday()
    월 = 날짜.month

    def predict(역, 시간, 요일, 월):
        a, b, c, d, e = {
            "서울역": [-3513.2, 819.5, -26.8, -80.6, 8.9],
            "강남역": [-7548.7, 1692.1, -50.0, -323.5, -9.2],
            "사당역": [-117.5, 337.1, -12.3, -61.4, 9.5],
            "홍대입구역": [-5115.8, 1080.5, -30.0, 85.3, 19.9]
        }[역]
        return a + b*시간 + c*(시간**2) + d*요일 + e*월

    예측값 = predict(역, 시간_실수, 요일, 월)

    def grade(val, max_val):
        cdi = val / max_val
        if cdi >= 0.95: return "매우혼잡"
        elif cdi >= 0.85: return "혼잡"
        elif cdi >= 0.7: return "약간혼잡"
        elif cdi >= 0.5: return "보통"
        else: return "여유"

    max_val = max([predict(역, t, 요일, 월) for t in np.arange(5, 24, 0.1)])
    혼잡등급 = grade(예측값, max_val)

    st.header(f"{역}  |  {datetime.now().strftime('%H:%M')}")
    st.subheader(f"현재 혼잡도: **{혼잡등급}**")
    st.write(f"예상 인원: {int(예측값)}명")

    st.markdown("### 추천 시간대")
    추천 = []
    for delta in [-0.83, 0.67, 0.75]:
        t = 시간_실수 + delta
        p = predict(역, t, 요일, 월)
        g = grade(p, max_val)
        h, m = int(t), int((t % 1)*60)
        추천.append((f"{h:02d}:{m:02d}", g))

    col1, col2, col3 = st.columns(3)
    for idx, col in enumerate([col1, col2, col3]):
        with col:
            st.button(f"{추천[idx][0]}\n({추천[idx][1]})")

    st.button("다시 하기")
