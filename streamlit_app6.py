import streamlit as st
import datetime
from congestion_model import calculate_prediction, calculate_cdi, get_congestion_level, get_recommendations

st.set_page_config(layout="wide")

# --- 제목 영역 ---
st.markdown("<div style='background-color: #ffb6c1; padding: 20px; border-radius: 10px; text-align: center;'>"
            "<h1 style='color: black;'>지하철 혼잡도 분석</h1></div>", unsafe_allow_html=True)

# --- 입력 폼 구성 ---
with st.form("user_input_form"):
    st.markdown("### 🚇 역 선택")
    station = st.selectbox("역을 선택하세요", ["강남", "서울역", "사당", "홍대입구"])

    st.markdown("### 📅 날짜 선택")
    col1, col2, col3 = st.columns(3)
    with col1:
        year = st.selectbox("연도", [2023, 2024, 2025], index=2)
    with col2:
        month = st.selectbox("월", list(range(1, 13)), index=8)
    with col3:
        day = st.selectbox("일", list(range(1, 32)), index=20)

    st.markdown("### ⏰ 시간 선택")
    col4, col5 = st.columns(2)
    with col4:
        hour = st.selectbox("시", list(range(0, 24)), index=17)
    with col5:
        minute = st.selectbox("분", list(range(0, 60)), index=30)

    submitted = st.form_submit_button("🔍 검색")

# --- 결과 출력 ---
if submitted:
    input_time = hour + minute / 60
    date = datetime.date(year, month, day)
    weekday = date.weekday()

    # 새벽시간 보정
    if input_time < 5:
        input_time = 5

    # 예측 값 계산
    pred = calculate_prediction(station, input_time, weekday, month)
    cdi = calculate_cdi(station, pred)
    level = get_congestion_level(cdi)

    # --- 결과 헤더 ---
    colL, colR = st.columns([1, 1])
    with colL:
        st.markdown(f"<div style='border: 2px solid black; padding: 10px; border-radius: 5px;'>"
                    f"<h3>🚉 역: {station}</h3></div>", unsafe_allow_html=True)
    with colR:
        now_time = datetime.datetime.now().strftime("%H:%M")
        st.markdown(f"<div style='border: 2px solid black; padding: 10px; border-radius: 5px;'>"
                    f"<h3>⏱️ 현재시간: {now_time}</h3></div>", unsafe_allow_html=True)

    st.markdown("---")

    # --- 현재 혼잡도 ---
    congestion_colors = {
        "매우 혼잡": "red",
        "혼잡": "orange",
        "약간 혼잡": "gold",
        "보통": "green",
        "여유": "blue"
    }

    color = congestion_colors.get(level, "gray")
    st.markdown(f"<h3>🎯 현재 혼잡도: <span style='color:{color}'>{level}</span> (CDI: {cdi})</h3>", unsafe_allow_html=True)
    st.markdown("예상 인원: **{}명**".format(pred))

    st.markdown("#### 🔹 등급 기준")
    st.markdown("""
    <div style="border:1px solid #ccc; padding:10px; border-radius:10px;">
        <ul>
            <li><span style='color:red;'>매우 혼잡</span>: CDI ≥ 0.8</li>
            <li><span style='color:orange;'>혼잡</span>: 0.6 ≤ CDI < 0.8</li>
            <li><span style='color:gold;'>약간 혼잡</span>: 0.4 ≤ CDI < 0.6</li>
            <li><span style='color:green;'>보통</span>: 0.2 ≤ CDI < 0.4</li>
            <li><span style='color:blue;'>여유</span>: CDI < 0.2</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # --- 추천 시간대 ---
    st.markdown("## 🕒 추천 시간대")

    recs = get_recommendations(station, hour + minute / 60, weekday, month)
    for t, p, d, l in recs:
        h = int(t)
        m = int((t - h) * 60)
        color = congestion_colors.get(l, "gray")
        st.markdown(f"<div style='border:2px solid {color}; padding:10px; margin:5px; border-radius:10px;'>"
                    f"<h4>{h:02d}:{m:02d} → <span style='color:{color}'>{l}</span></h4>"
                    f"예상 인원: {p}명 / CDI: {d}</div>", unsafe_allow_html=True)

    # --- 다시하기 버튼 ---
    st.markdown("<div style='text-align: right;'>"
                "<button onClick='window.location.reload();'>🔁 다시 하기</button></div>", unsafe_allow_html=True)
