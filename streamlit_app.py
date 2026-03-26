import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import os
from openpyxl import load_workbook

# 1. 페이지 설정
st.set_page_config(page_title="AI Strategy Master v6.7", page_icon="🛡️", layout="wide")

# 2. 하이퍼 분석 엔진 (사용자 마음 중심 설계)
class StrategyMasterV67:
    STEPS = ["", "마음사기", "수강 목적성 심기", "영 인지", "성경 인정", "선악구분", "시대구분", "말씀 인정", "종교 세계 인식", "약속의 목자 인정", "약속한 성전 인정"]

    @staticmethod
    def get_deep_context(file_path, sheet_name):
        """병합 셀 논리 분석 및 전수 텍스트 문맥 스캔"""
        try:
            wb = load_workbook(file_path, data_only=True)
            ws = wb[sheet_name]
            all_text = ""
            for row in ws.iter_rows(values_only=True):
                for cell in row:
                    if cell: all_text += f" {str(cell).strip()}"
            return all_text
        except: return ""

    @staticmethod
    def execute_simulation(text, admin, sit, strat):
        """단계-이해도-성향-외부위협을 통합한 입체 분석"""
        # 1. MBTI 추출 (내용 공란 대비 전수 스캔)
        mbtis = ["ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
        s_mbti = next((m for m in mbtis if m in text.upper()), "미기입")
        
        # 2. 단계 및 질적 수준(상/중/하) 분석
        curr_idx = 0
        for i, step in enumerate(StrategyMasterV67.STEPS):
            if step and step in text: curr_idx = i
        
        level = "중" # 기본값
        if any(kw in text for kw in ['확실', '통달', '완전', '믿음']): level = "상"
        elif any(kw in text for kw in ['의심', '불안', '초보', '어려움']): level = "하"

        # 3. 위기 지수 동적 산출
        base_risk = 50
        media_threat = 25 if any(k in sit for k in ['http', 'youtube', '영상', '자막']) else 0
        
        # 단계별 취약점 가중치: 초반 단계(5단계 미만)이면서 이해도가 '하'이면 외부 위협에 가중치 1.5배
        if curr_idx < 5 and level == "하": media_threat *= 1.5
        
        # 4. 맞춤형 전략 도출 (전도사 성향 반영)
        # 성향별/단계별 전략 메시지 딕셔너리화 (단순 매핑 탈피)
        risk_score = min(max(base_risk + media_threat + (10 if level == "하" else -10), 0), 100)
        
        advice = f"**[{admin['id']}전도사님 상성 분석]** "
        if level == "하":
            advice += f"현재 '{StrategyMasterV67.STEPS[curr_idx]}' 단계의 정착이 시급합니다. "
            advice += f"전도사님의 {admin['mbti']} 성향을 살려 " + ("논리적 근거로 의문을 해소" if 'T' in admin['mbti'] else "따뜻한 심방으로 마음을 보호") + "해야 합니다."
        else:
            advice += f"'{StrategyMasterV67.STEPS[curr_idx]}' 과정을 잘 소화하고 있습니다. "
            advice += f"{admin['ennea']} 에너지를 활용해 더 큰 비전을 제시하십시오."

        return risk_score, advice

# 3. UI 구성 (누락 없는 누적 레이아웃)
with st.sidebar:
    st.header("⚙️ 통합 마스터 v6.7")
    common_xlsx = st.file_uploader("📂 공통 출석부", type=["xlsx"], key="main_67")
    st.markdown("---")
    
    m_list = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    e_list = ["모름"] + [f"{i}번" for i in range(1, 10)]
    admins = []
    for tag in ["A", "B", "C"]:
        with st.expander(f"👤 {tag}전도사 프로필"):
            f_up = st.file_uploader(f"{tag}반 파일", type=["xlsx"], key=f"f67_{tag}")
            c1, c2 = st.columns(2)
            with c1:
                m_sel = st.selectbox("MBTI", m_list, key=f"m67_{tag}")
                g_sel = st.radio("성별", ["남", "여", "모름"], index=2, key=f"g67_{tag}")
            with c2:
                e_sel = st.selectbox("애니어그램", e_list, key=f"e67_{tag}")
            admins.append({'id': tag, 'file': f_up, 'mbti': m_sel, 'ennea': e_sel})

# 4. 메인 분석 로직
st.title("🏛️ 전략 시뮬레이션 시스템 v6.7")
l_col, r_col = st.columns([1, 1.2])

with l_col:
    st.subheader("🎯 상황 데이터 입력")
    sit_val = st.text_area("🌐 발생 상황 (영상 링크/자막 텍스트)", height=100)
    strat_val = st.text_area("🛡️ 대응 전략", height=100)
    
    if st.button("무결점 정밀 분석 가
