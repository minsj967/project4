import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="환경 모니터링 대시보드",
    page_icon="🌡️",
    layout="wide"
)

# 제목
st.title("🌡️ 환경 모니터링 대시보드")

# 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=['csv'])

if uploaded_file is not None:
    # 데이터 로드
    try:
        df = pd.read_csv(uploaded_file)
        
        # 타임스탬프 컬럼 처리
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d-%m-%Y %H:%M')
        
        # 데이터 기본 정보 표시
        st.subheader("📊 데이터 개요")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 데이터 수", len(df))
        with col2:
            st.metric("측정 기간", f"{df['Timestamp'].dt.date.min()} ~ {df['Timestamp'].dt.date.max()}")
        with col3:
            avg_temp = df['Temperature (°C)'].mean()
            st.metric("평균 온도", f"{avg_temp:.1f}°C")
        with col4:
            avg_humidity = df['Humidity (%)'].mean()
            st.metric("평균 습도", f"{avg_humidity:.1f}%")
        
        # 사이드바 필터
        st.sidebar.header("📋 필터 옵션")
        
        # 날짜 범위 선택
        if 'Timestamp' in df.columns:
            date_range = st.sidebar.date_input(
                "날짜 범위 선택",
                value=(df['Timestamp'].dt.date.min(), df['Timestamp'].dt.date.max()),
                min_value=df['Timestamp'].dt.date.min(),
                max_value=df['Timestamp'].dt.date.max()
            )
        
        # 환기 상태 필터
        if 'Ventilation Status' in df.columns:
            ventilation_filter = st.sidebar.multiselect(
                "환기 상태",
                options=df['Ventilation Status'].unique(),
                default=df['Ventilation Status'].unique()
            )
            df = df[df['Ventilation Status'].isin(ventilation_filter)]
        
        # 메인 차트들
        st.subheader("📈 시간별 측정값 변화")
        
        # 온도와 습도 차트
        col1, col2 = st.columns(2)
        
        with col1:
            fig_temp = px.line(df, x='Timestamp', y='Temperature (°C)', 
                              title='온도 변화', color_discrete_sequence=['#FF6B6B'])
            fig_temp.update_layout(height=400)
            st.plotly_chart(fig_temp, use_container_width=True)
        
        with col2:
            fig_humidity = px.line(df, x='Timestamp', y='Humidity (%)', 
                                  title='습도 변화', color_discrete_sequence=['#4ECDC4'])
            fig_humidity.update_layout(height=400)
            st.plotly_chart(fig_humidity, use_container_width=True)
        
        # 대기질 지표
        st.subheader("🌫️ 대기질 지표")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_co2 = px.line(df, x='Timestamp', y='CO2 (ppm)', 
                             title='CO2 농도', color_discrete_sequence=['#45B7D1'])
            fig_co2.update_layout(height=400)
            st.plotly_chart(fig_co2, use_container_width=True)
        
        with col2:
            fig_pm = go.Figure()
            fig_pm.add_trace(go.Scatter(x=df['Timestamp'], y=df['PM2.5 (μg/m³)'], 
                                       mode='lines', name='PM2.5', line=dict(color='#96CEB4')))
            fig_pm.add_trace(go.Scatter(x=df['Timestamp'], y=df['PM10 (μg/m³)'], 
                                       mode='lines', name='PM10', line=dict(color='#FFEAA7')))
            fig_pm.update_layout(title='미세먼지 농도', height=400)
            st.plotly_chart(fig_pm, use_container_width=True)
        
        # 기타 지표
        st.subheader("🔬 기타 환경 지표")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig_tvoc = px.line(df, x='Timestamp', y='TVOC (ppb)', 
                              title='TVOC 농도', color_discrete_sequence=['#DDA0DD'])
            fig_tvoc.update_layout(height=350)
            st.plotly_chart(fig_tvoc, use_container_width=True)
        
        with col2:
            fig_co = px.line(df, x='Timestamp', y='CO (ppm)', 
                            title='CO 농도', color_discrete_sequence=['#F39C12'])
            fig_co.update_layout(height=350)
            st.plotly_chart(fig_co, use_container_width=True)
        
        with col3:
            fig_light = px.line(df, x='Timestamp', y='Light Intensity (lux)', 
                               title='조도', color_discrete_sequence=['#FFD93D'])
            fig_light.update_layout(height=350)
            st.plotly_chart(fig_light, use_container_width=True)
        
        # 거주자 정보
        st.subheader("👥 거주자 정보")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_occupancy = px.line(df, x='Timestamp', y='Occupancy Count', 
                                   title='거주자 수', color_discrete_sequence=['#E74C3C'])
            fig_occupancy.update_layout(height=400)
            st.plotly_chart(fig_occupancy, use_container_width=True)
        
        with col2:
            # 움직임 감지 히트맵
            df['Hour'] = df['Timestamp'].dt.hour
            motion_data = df.groupby('Hour')['Motion Detected'].sum().reset_index()
            fig_motion = px.bar(motion_data, x='Hour', y='Motion Detected', 
                               title='시간별 움직임 감지 횟수', color_discrete_sequence=['#9B59B6'])
            fig_motion.update_layout(height=400)
            st.plotly_chart(fig_motion, use_container_width=True)
        
        # 환기 상태 분석
        if 'Ventilation Status' in df.columns:
            st.subheader("🌪️ 환기 상태 분석")
            
            col1, col2 = st.columns(2)
            
            with col1:
                ventilation_counts = df['Ventilation Status'].value_counts()
                fig_vent_pie = px.pie(values=ventilation_counts.values, 
                                     names=ventilation_counts.index, 
                                     title='환기 상태 분포')
                st.plotly_chart(fig_vent_pie, use_container_width=True)
            
            with col2:
                # 환기 상태별 평균 온도
                avg_by_vent = df.groupby('Ventilation Status').agg({
                    'Temperature (°C)': 'mean',
                    'Humidity (%)': 'mean',
                    'CO2 (ppm)': 'mean'
                }).round(2)
                st.write("**환기 상태별 평균값**")
                st.dataframe(avg_by_vent)
        
        # 상관관계 분석
        st.subheader("🔗 상관관계 분석")
        
        numeric_cols = ['Temperature (°C)', 'Humidity (%)', 'CO2 (ppm)', 
                       'PM2.5 (μg/m³)', 'PM10 (μg/m³)', 'TVOC (ppb)', 
                       'CO (ppm)', 'Light Intensity (lux)', 'Occupancy Count']
        
        correlation_matrix = df[numeric_cols].corr()
        fig_corr = px.imshow(correlation_matrix, 
                            title='환경 지표 간 상관관계',
                            aspect="auto",
                            color_continuous_scale='RdBu_r')
        fig_corr.update_layout(height=600)
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # 데이터 테이블
        st.subheader("📋 원본 데이터")
        st.dataframe(df, use_container_width=True)
        
        # 요약 통계
        st.subheader("📊 요약 통계")
        st.write(df.describe())
        
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {str(e)}")
        st.info("CSV 파일의 형식을 확인해주세요. 컬럼명이 올바른지 확인해보세요.")

else:
    st.info("👆 CSV 파일을 업로드해주세요.")
    st.write("**예상 CSV 형식:**")
    st.code("""
    Timestamp,Temperature (°C),Humidity (%),CO2 (ppm),PM2.5 (μg/m³),PM10 (μg/m³),TVOC (ppb),CO (ppm),Light Intensity (lux),Motion Detected,Occupancy Count,Ventilation Status
    18-02-2024 8:00,21.75,63.11,989.74,31.17,89.66,226.83,2.84,646.86,0,4,Open
    ...
    """)
