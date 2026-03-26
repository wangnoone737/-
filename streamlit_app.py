import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import os
from openpyxl import load_workbook

# 1. 페이지 설정
st.set_page_config(page_title="AI Strategy Master v6.0", page_icon="⚖️", layout="wide")

# 2. 분석 엔진 (병합 구조 + 전도사 상성 분석)
class StrategyEngine:
    STAGE_MAP = {i: name for i, name in enumerate(["", "마음사기", "수강 목적성 심기", "영 인지", "성경 인정", "선악구분", "시대구분", "말씀 인정", "종교 세계 인식", "약속의 목자 인정", "약속한 성전 인정"])}

    @staticmethod
    def parse_sheet_structure(file_path, sheet_name):
        """사용자 논리(병합 셀 및 열 위계)에 따른 정밀 데이터 추출"""
        wb = load_workbook(file_path, data_only=True)
        ws = wb[sheet_name]
        extracted = {}
        
        # 100행까지 스캔 (속도와 정밀도 타협)
        for row in range(1, min(ws.max_row + 1, 100)):
            for col in range(1, ws.max_column + 1, 2): # 홀수 열(항목) 위주 스캔
                item = ws.cell(row=row, column=col).value
                content = ws.cell(row=row, column=col+1).value
                if item and content:
                    extracted[str(item).strip()] = str(content).strip()
        return extracted

    @staticmethod
    def analyze_matching(student_data, admin_info, situation, strategy):
        # 1. 수강생 맥락 통합
        context = " ".join([f"{k}:{v}" for k, v in student_data.items()])
        
        # 2. 수강생 MBTI 및 단계 추출
        s_mbti = ""
        for m in ["ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]:
            if m in context.upper(): s_mbti = m; break
        
        step_match = re.search(r'(\d+)', context)
        step_num = int(step_match.group(1)) if step_match else 0
        
        # 3. 데이터 결손 체크
        missing = []
        if not s_mbti: missing.append("수강생 MBTI")
        if step_num == 0: missing.append("수강 단계")
        if not any(kw in context for kw in ['고민', '상황', '환경']): missing.append("상세 배경")

        # 4. 위기 지수 계산 (전도사 상성 포함)
        yt_risk = 15 if any(kw in situation for kw in ["youtube.com", "youtu.be"]) else 0
        ctx_risk = 10 if any(kw in context for kw in ['의심', '불안', '인터넷', '핍박']) else -5
        
        # 상성 분석 (전도사 MBTI vs 수강생 MBTI)
        match_bonus = 0
        if s_mbti and admin_info['mbti'] != "모름":
            # 예: 관리자와 수강생의 성향(T/F)이 같으면 소통 보너스
            if s_mbti[2] == admin_info['mbti'][2]: match_bonus += 5
        
        # 전략 보너스
        strat_bonus = 0
        if s_mbti:
            if 'T' in s_mbti and any(w in strategy for w in ['논리', '설명', '근거']): strat_bonus += 12
            if 'F' in s_mbti and any(w in strategy for w in ['공감', '위로', '마음']): strat_bonus += 12

        final_risk = min(max(55 + (step_num * 2) + yt_risk + ctx_risk - match_bonus - strat_bonus, 0), 100)
        
        # 결과 멘트 생성
        advice = f"[{admin_info['id']}전도사님-MBTI:{admin_info['mbti']}] 성향을 고려한 분석: "
        advice += f"{s_mbti} 수강생에게는 " + ("논리적 납득이 필수적입니다." if 'T' in s_mbti else "정서적 지지가 최우선입니다.")
        
        return final_risk, StrategyEngine.STAGE_MAP.get(step_num, "분석중"), advice, missing

# 3. 사이드바 (전도사 입력란 완전 복구)
with st.sidebar:
    st.header("⚙️ 시스템 설정 v6.0")
    mbti_list = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    ennea_list = ["모름"] + [f"{i}번" for i in range(1, 10)]
    
    admins = []
    for label in ["A", "B", "C"]:
        with st.expander(f"👤 전도사 {label} 프로필"):
            f = st.file_uploader(f"{label}반 데이터 (Excel)", type=["xlsx"], key=f"f_{label}")
            col1, col2 = st.columns(2)
            with col1:
                m = st.selectbox(f"MBTI", mbti_list, key=f"m_{label}")
                g = st.radio(f"성별", ["남", "여", "모름"], index=2, key=f"g_{label}")
            with col2:
                e = st.selectbox(f"애니어그램", ennea_list, key=f"e_{label}")
            admins.append({'id': label, 'file': f, 'mbti': m, 'ennea': e, 'gender': g})

# 4. 메인 화면
st.title("🏛️ 전략 시뮬레이션 시스템 v6.0")
col_inp, col_chart = st.columns([1, 1.2])

with col_inp:
    st.subheader("🎯 시나리오 & 대응 전략")
    situation = st.text_area("🌐 발생 상황", placeholder="예: 외부 정보를 접하고 의심이 생김", height=80)
    strategy_input = st.text_area("🛡️ 대응 전략", placeholder="예: 전도사와 1:1 면담을 통한 소통", height=80)
    run_btn = st.button("구조화 분석 가동 🚀", use_container_width=True)

if run_btn:
    final_res = []
    status_box = st.empty()
    prog_bar = st.progress(0)
    
    active_admins = [a for a in admins if a['file']]
    
    for a_idx, admin in enumerate(active_admins):
        temp_path = f"temp_{admin['id']}.xlsx"
        with open(temp_path, "wb") as f: f.write(admin['file'].getbuffer())
        
        xl = pd.ExcelFile(temp_path)
        for s_idx, sheet in enumerate(xl.sheet_names
