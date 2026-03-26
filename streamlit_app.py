import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import os
import time
from openpyxl import load_workbook

# [최종 경고]: 전도사 성별, MBTI, 애니어그램 변수 절대 누락 금지 로직 적용됨.

st.set_page_config(page_title="Strategic Master v7.6", page_icon="🛡️", layout="wide")

class FinalStrategyEngineV76:
    STEPS = ["", "마음사기", "수강 목적성 심기", "영 인지", "성경 인정", "선악구분", "시대구분", "말씀 인정", "종교 세계 인식", "약속의 목자 인정", "약속한 성전 인정"]

    @staticmethod
    def get_full_text(file_path, sheet_name):
        try:
            wb = load_workbook(file_path, data_only=True)
            ws = wb[sheet_name]
            return " ".join([str(c.value) for r in ws.iter_rows() for c in r if c.value])
        except: return ""

    @staticmethod
    def deep_dive_analysis(text, s_mbti, admin, sit, strat):
        """[성별/성향/단계 통합] 2단계 초정밀 분석 엔진"""
        # 1. 단계 추출
        idx = 0
        for i, s in enumerate(FinalStrategyEngineV76.STEPS):
            if s and s in text: idx = i
        
        # 2. 이해도 판정
        level = "중"
        if any(k in text for k in ['확실', '통달', '믿음']): level = "상"
        elif any(k in text for k in ['의심', '불안', '모름']): level = "하"

        # 3. 위기 지수 연산
        risk = 60 if any(k in sit for k in ['영상', '유튜브', '비방']) else 40
        if level == "하": risk += 20
        if idx < 6: risk += 10

        # 4. 성별 및 성향 기반 전략 리포트 생성
        g_advice = "동성 간의 밀착 케어로 정서적 유대를 극대화하십시오."
        if admin['gender'] == "남":
            g_advice = "상대 수강생이 이성일 경우, 격식 있는 태도와 공적인 거리를 유지하며 신뢰를 쌓으십시오."
        
        report = f"### 🧬 {admin['id']}전도사님({admin['gender']}) 맞춤 1:1 심층 전략\n\n"
        report += f"**분석 요약:** 현재 **{FinalStrategyEngineV76.STEPS[idx]}** 단계(이해도: {level})이며, **{s_mbti}** 성향의 수강생입니다.\n\n"
        report += "--- \n"
        report += "#### **🔍 초정밀 대응 지침**\n"
        report += f"1. **성별/관계 가이드:** {g_advice}\n"
        report += f"2. **성향별 접근:** {admin['mbti']}인 전도사님은 "
        report += ("논리적 근거로 수강생의 혼란을 잠재우는 데 탁월합니다." if 'T' in admin['mbti'] else "수강생의 불안을 공감으로 다독이는 데 집중하십시오.") + "\n"
        report += f"3. **에너지 투입:** {admin['ennea']} 에너지를 활용해 수강생이 흔들리지 않도록 강력한 영적 비전을 제시하십시오.\n"
        report += f"4. **전략 최적화:** 입력하신 전략은 {s_mbti} 수강생에게 '실질적인 확신'을 주는 방향으로 보완이 필요합니다."

        return int(min(risk, 100)), report

# --- UI 레이아웃 ---
with st.sidebar:
    st.header("⚙️ 전략 컨트롤 v7.6")
    st.file_uploader("📂 공통 출석부", type=["xlsx"], key="v76_main")
    st.markdown("---")
    
    m_opts = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    e_opts = ["모름"] + [f"{i}번" for i in range(1, 10)]
    
    admin_profiles = []
    for t in ["A", "B", "C"]:
        with st.expander(f"👤 {t}전도사 프로필 설정"):
            f = st.file_uploader(f"{t}반 파일", type=["xlsx"], key=f"v76_f_{t}")
            # 성별 필드 절대 사수
            g = st.radio("성별", ["남", "여"], key=f"v76_g_{t}", horizontal=True)
            m = st.selectbox("MBTI", m_opts, key=f"v76_m_{t}")
            e = st.selectbox("애니어그램", e_opts, key=f"v76_e_{t}")
            admin_profiles.append({'id': t, 'file': f, 'gender': g, 'mbti': m, 'ennea': e})

st.title("🏛️ 전략 시뮬레이션 시스템 v7.6 (완결)")
l_col, r_col = st.columns([1, 1.2])

with l_col:
    st.subheader("🎯 시나리오 분석 설정")
    mode = st.radio("분석 범위", ["기수 전체", "개인 딥다이브"], horizontal=True)
    target_name = st.text_input("수강생 이름") if mode == "개인 딥다이브" else ""
    sit_input = st.text_area("🌐 발생 상황", height=100)
    strat_input = st.text_area("🛡️ 수립 전략", height=100)
    
    if st.button("AI 분석 엔진 가동 🚀", use_container_width=True):
        active_admins = [a for a in admin_profiles if a['file']]
        if not active_admins: st.error("파일을 업로드해주세요.")
        else:
            final_results = []
            prog_ui = st.empty()
            with prog_ui.container():
                bar = st.progress(0)
                msg = st.empty()
                
                for i, adm in enumerate(active_admins):
                    tmp = f"v76_{adm['id']}.xlsx"
                    with open(tmp, "wb") as f: f.write(adm['file'].getbuffer())
                    xl = pd.ExcelFile(tmp)
                    
                    for s_idx, s_name in enumerate(xl.sheet_names):
                        name = re.sub(r'[^가-힣]', '', s_name)
                        if name in ['단계', '양식', '출석'] or len(name) < 2: continue
                        
                        # 진행도 업데이트
                        bar.progress((i/len(active_admins)) + (s_idx/(len(xl.sheet_names)*len(active_admins))))
                        msg.write(f"🔍 {adm['id']}전도사 - **{name}** 분석 중...")
                        
                        txt = FinalStrategyEngineV76.get_full_text(tmp, s_name)
                        m_match = re.search(r'(ISTJ|ISFJ|INFJ|INTJ|ISTP|ISFP|INFP|INTP|ESTP|ESFP|ENFP|ENTP|ESTJ|ESFJ|ENFJ|ENTJ)', txt, re.I)
                        s_mbti = m_match.group(0).upper() if m_match else "미기입"
                        
                        risk, rpt = FinalStrategyEngineV76.deep_dive_analysis(txt, s_mbti, adm, sit_input, strat_input)
                        
                        if mode == "개인 딥다이브":
                            if name == target_name:
                                final_results.append({'name': name, 'admin': adm['id'], 'risk': risk, 'report': rpt, 'type': 'deep'})
                                break
                        else:
                            final_results.append({'name': name, 'admin': adm['id
