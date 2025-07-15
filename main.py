import streamlit as st
import pandas as pd
import plotly.express as px

# CSV 불러오기
DATA_PATH = "your_data.csv"  # GitHub에 올릴 때 여기에 맞게 파일명 수정하세요
df = pd.read_csv(DATA_PATH)

# 컬럼 정리
df.columns = df.columns.str.strip()
df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')

st.set_page_config(page_title="실내 공기질 분석 대시보드", layout="wide")
st.title("🌿 환기 및 에너지 소비 패턴에 따른 실내 공기질 분석")

# 사이드바 필터
st.sidebar.header("필터 선택")
selected_status = st.sidebar.multiselect(
    "환기 상태 선택", options=df['Ventilation Status'].dropna().unique(), default=df['Ventilation Status'].dropna().unique()
)

df_filtered = df[df['Ventilation Status'].isin(selected_status)]

# 시각화 1: CO2 농도 변화 (시간 vs CO2)
st.subheader("📈 CO₂ 농도 변화")
fig_co2 = px.line(df_filtered, x="Timestamp", y="CO2 (ppm)", color="Ventilation Status", title="CO₂ 농도 변화")
st.plotly_chart(fig_co2, use_container_width=True)

# 시각화 2: 미세먼지 (PM2.5) vs 환기
st.subheader("🌫️ PM2.5 농도 비교 (환기 상태별)")
fig_pm = px.box(df_filtered, x="Ventilation Status", y="PM2.5 (?g/m?)", points="all", color="Ventilation Status")
st.plotly_chart(fig_pm, use_container_width=True)

# 시각화 3: 인원 수와 CO₂ 상관
st.subheader("👥 인원 수 vs CO₂")
fig_scatter = px.scatter(
    df_filtered,
    x="Occupancy Count",
    y="CO2 (ppm)",
    color="Ventilation Status",
    trendline="ols",
    title="인원 수와 CO₂ 농도 관계"
)
st.plotly_chart(fig_scatter, use_container_width=True)

# 시각화 4: 온도와 건강지표 설명 (간접 지표 예시)
st.markdown("### 🌡️ 온도와 습도 분포")
fig_temp = px.histogram(df_filtered, x="Temperature (?C)", nbins=30, title="온도 분포")
fig_hum = px.histogram(df_filtered, x="Humidity (%)", nbins=30, title="습도 분포")
st.plotly_chart(fig_temp, use_container_width=True)
st.plotly_chart(fig_hum, use_container_width=True)

# 분석 요약
st.markdown("---")
st.markdown("✅ **요약**: 환기 상태가 열악할수록 CO₂와 PM2.5 농도가 높아지는 경향이 있습니다. 인원 수가 많을수록 CO₂ 농도도 상승합니다. 따라서, 에너지 소비를 최소화하되 효율적인 환기 방식의 도입이 공기질과 건강에 도움이 됩니다.")
