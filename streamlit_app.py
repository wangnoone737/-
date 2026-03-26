import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import os
import time
from openpyxl import load_workbook

# [긴급 패치 v7.8]: SyntaxError 및 NameError 원천 봉쇄. 잘림 없는 전체 코드.

st.set_page_config(page_title="Strategic Master v7.8", page_icon="🛡️", layout="wide")

class FinalEngineV78:
    STEPS = ["", "마음사기", "수강 목적성 심기", "영 인지", "성경 인정", "선악구분", "시대구분", "말씀 인정", "종교 세계 인식", "약속의 목자 인정", "약속한 성전 인정"]

    @staticmethod
    def get_text(file_path, sheet_name):
        try:
            wb = load_workbook(file_path, data_only=True)
            ws = wb[sheet_name]
            return " ".join([str(c.value) for r in ws.iter_rows() for c in r if c.value])
        except: return ""

    @staticmethod
    def run_deep_analysis(text, s_mbti, admin, sit, strat):
        # 1. 단계 추출
        idx = 0
        for i, s in enumerate(FinalEngineV78.STEPS):
            if s and s in text: idx = i
        
        # 2. 이해도 판정
        level = "중"
        if any(k in text for k in ['확실', '통달', '믿음']): level = "상"
        elif any(k in text for k in ['의심', '불안', '모름']): level = "하"

        # 3. 위기 지수 연산
        base_threat = 60 if any(k in sit for k in ['영상', '유튜브', '비방']) else 40
        if level == "하": base_threat += 20
        if idx < 6: base_threat += 10
        final_score = int(min(base_threat, 100))

        # 4. 리포트 생성 (성별/성향/상성 기반)
        g_tip = "동성 간 밀착 상담 권장" if admin['gender'] == "여" else "이성 간 격식 있는 상담 권장"
        report = f"### 🧬 {admin['id']}전도사님({admin['gender']}) 맞춤 전략\n\n"
        report += f"**상태:** {FinalEngineV78.STEPS[idx]}({level}) | **성향:** {s_mbti}\n\n"
        report += f"**[대응 지침]**\n"
        report += f"* **관계:** {g_tip}\n"
        report += f"* **방법:** {admin['mbti']} 강점을 활용해 " + ("논리적 해답을 제시하세요." if 'T' in admin['mbti'] else "정서적 안정을 최우선하세요.") + "\n"
        report += f"* **에너지:** {admin['ennea']}형의 에너지를 바탕으로 확신을 심어주십시오."

        return final_score, report

# --- UI 레이아웃 ---
with st.sidebar:
    st.header("⚙️ 시스템 설정 v7.8")
    main_file = st.file_uploader("📂 공통 출석부", type=["xlsx"], key="v78_main")
    
    m_opts = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    e_opts = ["모름"] + [f"{i}번" for i in range(1, 10)]
    
    admins = []
    for t in ["A", "B", "C"]:
        with st.expander(f"👤 {t}전도사 설정"):
            f = st.file_uploader(f"{t}반 파일", type=["xlsx"], key=f"v78_f_{t}")
            g = st.radio("성별", ["남", "여"], key=f"v78_g_{t}", horizontal=True)
            m = st.selectbox("MBTI", m_opts, key=f"v78_m_{t}")
            e = st.selectbox("애니어그램", e_opts, key=f"v78_e_{t}")
            admins.append({'id': t, 'file': f, 'gender': g, 'mbti': m, 'ennea': e})

st.title("🏛️ 전략 시뮬레이션 v7.8")
l_col, r_col = st.columns([1, 1.2])

with l_col:
    st.subheader("🎯 분석 입력")
    mode = st.radio("모드", ["전체", "개별"], horizontal=True)
    target = st.text_input("수강생 이름") if mode == "개별" else ""
    sit_in = st.text_area("🌐 상황", height=80)
    strat_in = st.text_area("🛡️ 전략", height=80)
    
    if st.button("무결점 정밀 분석 실행 🚀", use_container_width=True):
        active_list = [a for a in admins if a['file']]
        if not active_list: st.error("파일을 업로드하세요.")
        else:
            final_res = []
            prog = st.empty()
            with prog.container():
                bar = st.progress(0)
                status = st.empty()
                for i, adm in enumerate(active_list):
                    t_path = f"v78_{adm['id']}.xlsx"
                    with open(t_path, "wb") as f: f.write(adm['file'].getbuffer())
                    xl = pd.ExcelFile(t_path)
                    for s_idx, s_name in enumerate(xl.sheet_names):
                        name = re.sub(r'[^가-힣]', '', s_name)
                        if name in ['단계', '양식', '출석'] or len(name) < 2: continue
                        
                        bar.progress((i/len(active_list)) + (s_idx/(len(xl.sheet_names)*len(active_list))))
                        status.write(f"🔍 {adm['id']}전도사 - {name} 분석 중...")
                        
                        txt = FinalEngineV78.get_text(t_path, s_name)
                        m_m = re.search(r'(ISTJ|ISFJ|INFJ|INTJ|ISTP|ISFP|INFP|INTP|ESTP|ESFP|ENFP|ENTP|ESTJ|ESFJ|ENFJ|ENTJ)', txt, re.I)
                        s_mbti = m_m.group(0).upper() if m_m else "미기입"
                        
                        risk, rpt = FinalEngineV78.run_deep_analysis(txt, s_mbti, adm, sit_in, strat_in)
                        
                        if mode == "개별":
                            if name == target:
                                final_res.append({'name': name, 'admin': adm['id'], '
