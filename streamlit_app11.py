import streamlit as st
import datetime
import pandas as pd

# 역별 회귀계수
regression_coefficients = {
    "강남역": [-7548.7568, 1692.1847, -50.0100, -323.5538, -9.2502],
    "서울역": [-3513.2458, 819.5735, -26.8271, -80.6853, 8.9737],
    "사당역": [-117.5344, 337.1758, -12.3019, -61.4697, 9.5399],
    "홍대입구역": [-5115.8516, 1080.5163, -30.0831, 85.3852, 19.9417]
}

# 상위 10% 기준값
station_cdi_threshold = {
    "강남역": 8206,
    "서울역": 5522,
    "사당역": 2945,
    "홍대입구역": 3434
}

# 혼잡도 등급 계산 함수
def get_cdi_grade(cdi):
    if cdi >= 0.75:
        return "매우혼잡"
    elif cdi >= 0.60:
        return "혼잡"
    elif cdi >= 0.45:
        return "약간혼잡"
    elif cdi >= 0.30:
        return "보통"
    else:
        return "여유"

# 예측 함수
def predict_traffic(station, hour, minute, weekday, month):
    time = hour + minute / 60
    if time < 5:
        time = 5  # 새벽은 5시로 보정
    time_sq = time ** 2
    a, b, c, d, e = regression_coefficients[station]
    pred = a + b*time + c*time_sq + d*weekday + e*month
    pred = max(0, round(pred))  # 음수 방지
    cdi = pred / station_cdi_threshold[station]
    grade = get_cdi_grade(cdi)
    return pred, cdi, grade

# 추천 시간대 생성
def recommend_times(station, hour, minute, weekday, month):
    base_time = hour + minute / 60
    candidates = [base_time + i*0.05 for i in range(-6, 7)]  # ±30분, 5분 단위
    results = []
    for t in candidates:
        if t < 0 or t > 24:
            continue
        h, m = divmod(t * 60, 60)
        pred, cdi, grade = predict_traffic(station, int(h), int(m), weekday, month)
        results.append((f"{int(h):02d}:{int(m):02d}", grade, cdi, pred))
    results.sort(key=lambda x: x[2])  # CDI 기준 정렬
    return results[:3]

# 🌸 Streamlit UI 시작
st.markdown("<h1 style='background-color:pink; padding: 10px; text-align: center;'>지하철 혼잡도 분석</h1>", unsafe_allow_html=True)

with st.form("입력폼"):
    st.markdown("<div style='border: 2px solid pink; padding: 15px;'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div style='background-color:lightyellow;'>역 선택</div>", unsafe_allow_html=True)
        station = st.selectbox("", list(regression_coefficients.keys()))
    with col2:
        st.markdown("<div style='background-color:lightyellow;'>날짜 선택</div>", unsafe_allow_html=True)
        date = st.date_input("", value=datetime.date(2025, 9, 21))
    with col3:
        st.markdown("<div style='background-color:lightyellow;'>시간 선택</div>", unsafe_allow_html=True)
        hour = st.selectbox("시", list(range(0, 24)))
        minute = st.selectbox("분", list(range(0, 60)))

    submitted = st.form_submit_button("검색")
    st.markdown("</div>", unsafe_allow_html=True)

if submitted:
    weekday = date.weekday()
    month = date.month

    pred, cdi, grade = predict_traffic(station, hour, minute, weekday, month)

    # 출력
    colL, colR = st.columns(2)
    colL.markdown(f"<div style='border:2px solid black; padding:10px; font-size:20px;'>🚉 {station}</div>", unsafe_allow_html=True)
    colR.markdown(f"<div style='border:2px solid black; padding:10px; font-size:20px;'>🕓 현재 시간: {hour:02d}:{minute:02d}</div>", unsafe_allow_html=True)

    # 혼잡도 등급 표시
    st.markdown("<h3>현재 혼잡도</h3>", unsafe_allow_html=True)
    grades = ["매우혼잡", "혼잡", "약간혼잡", "보통", "여유"]
    colors = {"매우혼잡": "red", "혼잡": "orange", "약간혼잡": "yellow", "보통": "lightblue", "여유": "lightgreen"}
    styled_grades = [f"<span style='border:2px solid {colors[g]}; padding:5px;'>{g}</span>" if g == grade else g for g in grades]
    st.markdown(" / ".join(styled_grades), unsafe_allow_html=True)
    st.markdown(f"<div style='margin-top:10px;'>예상 인원: <b>{pred}명</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div>CDI: <b>{cdi:.3f}</b></div>", unsafe_allow_html=True)

    # CDI 기준 안내
    st.markdown("""
    <div style='margin-top:20px; padding:10px; border:2px dashed gray;'>
    <b>CDI 기준 안내</b><br>
    ≥ 0.75 : 매우혼잡<br>
    0.60 ~ 0.74 : 혼잡<br>
    0.45 ~ 0.59 : 약간혼잡<br>
    0.30 ~ 0.44 : 보통<br>
    < 0.30 : 여유
    </div>
    """, unsafe_allow_html=True)

    # 추천 시간대
    st.markdown("<h3 style='margin-top:30px;'>추천 시간대</h3>", unsafe_allow_html=True)
    top3 = recommend_times(station, hour, minute, weekday, month)
    for t, g, cdi_val, pred_val in top3:
        st.markdown(f"<div style='border:2px solid gray; padding:10px; margin-bottom:5px;'>{t} ({g}) - {pred_val}명, CDI: {cdi_val:.3f}</div>", unsafe_allow_html=True)

    # 다시 하기 버튼
    st.markdown("<div style='text-align:right; margin-top:30px;'><button onclick='window.location.reload()'>🔁 다시 하기</button></div>", unsafe_allow_html=True)
