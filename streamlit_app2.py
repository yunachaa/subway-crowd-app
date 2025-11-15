import streamlit as st
import datetime
import numpy as np

# ------------------------
# 회귀 계수 정의
# ------------------------
coefficients = {
    '강남역': [-7548.7568, 1692.1847, -50.0100, -323.5538, -9.2502],
    '서울역': [-3513.2458, 819.5735, -26.8271, -80.6853, 8.9737],
    '사당역': [-117.5344, 337.1758, -12.3019, -61.4697, 9.5399],
    '홍대입구역': [-5115.8516, 1080.5163, -30.0831, 85.3852, 19.9417],
}

# ------------------------
# 함수 정의
# ------------------------
def predict_passengers(station, time_float, weekday, month):
    coef = coefficients[station]
    time_squared = time_float ** 2
    return coef[0] + coef[1]*time_float + coef[2]*time_squared + coef[3]*weekday + coef[4]*month

def get_cdi_and_level(pred, station):
    max_values = {
        '강남역': 1400,
        '서울역': 1100,
        '사당역': 950,
        '홍대입구역': 1000,
    }
    cdi = pred / max_values[station]
    if cdi >= 0.9:
        return cdi, "매우 혼잡"
    elif cdi >= 0.7:
        return cdi, "혼잡"
    elif cdi >= 0.5:
        return cdi, "약간 혼잡"
    elif cdi >= 0.3:
        return cdi, "보통"
    else:
        return cdi, "여유"

def get_recommendations(station, base_time, weekday, month):
    deltas = [-0.25, 0.33, 0.42]  # 약 -15분, +20분, +25분 정도
    result = []
    for d in deltas:
        new_time = base_time + d
        pred = predict_passengers(station, new_time, weekday, month)
        _, level = get_cdi_and_level(pred, station)
        hour = int(new_time)
        minute = int((new_time - hour)*60)
        result.append((f"{hour:02d}:{minute:02d}", level))
    return result

# ------------------------
# Streamlit UI
# ------------------------
st.set_page_config(page_title="지하철 혼잡도 분석", layout="centered")
st.title("지하철 혼잡도 분석")

col1, col2, col3 = st.columns(3)
with col1:
    station = st.selectbox("역 선택", list(coefficients.keys()))
with col2:
    date = st.date_input("날짜", datetime.date.today())
with col3:
    time_input = st.time_input("시간", datetime.time(17, 30))

if st.button("검색"):
    hour = time_input.hour
    minute = time_input.minute
    time_float = hour + minute/60
    if time_float < 6:
        time_float = 5  # 보정

    weekday = date.weekday()  # 월:0 ~ 일:6
    month = date.month

    pred = predict_passengers(station, time_float, weekday, month)
    cdi, level = get_cdi_and_level(pred, station)
    recs = get_recommendations(station, time_float, weekday, month)

    # ------------------------
    # 결과 화면
    # ------------------------
    st.markdown(f"### {station} | {hour:02d}:{minute:02d}")
    st.markdown("---")
    st.markdown(f"**현재 혼잡도** : `{level}`  ")
    st.markdown(f"예상 인원 : **{int(pred)}명**")
    st.markdown("---")
    st.markdown("### 추천 시간대")
    col1, col2, col3 = st.columns(3)
    for i, (t, l) in enumerate(recs):
        with [col1, col2, col3][i]:
            st.markdown(f"**{t}**<br/>{l}", unsafe_allow_html=True)

    if st.button("다시 하기"):
        st.experimental_rerun()

    with st.expander("📊 혼잡도 분석 설명 보기"):
        st.markdown("""
        지하철 혼잡 패턴은 단순히 시간이 지날수록 인원이 직선적으로 늘어나거나 줄어드는 구조가 아니라,
        출퇴근 시간대에 급격히 솟는 피크와 비피크 구간이 반복되는 비선형적 특성을 가집니다.

        이를 반영하기 위해, 본 시스템은 입력받은 시간·요일·월 정보와 해당 역의 패턴을 기반으로 **다항 회귀 모델**을 활용해 예상 인원을 예측합니다.

        - 독립 변수: 시간, 시간², 요일, 월
        - 종속 변수: 승차 인원 수
        - 회귀 모델: 2차 다항 회귀
        - 혼잡도 등급: CDI (Crowd Density Index)를 통해 `매우 혼잡 / 혼잡 / 약간 혼잡 / 보통 / 여유`로 변환

        또한 예측 시간 기준 ±30분 이내의 3개 추천 시간대를 제시하여, 더 여유 있는 시간대 이용을 도와드립니다.
        """)
