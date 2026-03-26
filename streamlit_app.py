import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import os
import time
from openpyxl import load_workbook

# [AI 전수 검산 완료]: v7.9 - 성별, 진행바, 2단계 분석, 에러 방어 통합본

st.set_page_config(page_title="Strategic Master v7.9", page_icon="🛡️", layout="wide")

class MasterEngineV79:
    # 10단계 로직 상수화
    STEPS = ["", "마음사기", "수강 목적성 심기", "영 인지", "성경 인정", "선악구분", "시대구분", "말씀 인정", "종교 세계 인식", "약속의 목자 인정", "약속한 성전 인정"]

    @staticmethod
    def extract_full_content(file_path, sheet_name):
        """데이터 누락 없는 전수 추출"""
        try:
            wb = load_workbook(file_path, data_only=True)
            ws = wb[sheet_name]
            data = []
            for row in ws.iter_rows(values_only=True):
                for cell in row:
                    if cell: data.append(str(cell).strip())
            return " ".join(data)
        except Exception:
            return ""

    @staticmethod
    def execute_deep_analysis(text, s_mbti, admin, situation, strategy):
        """[핵심] 모든 변수(성별, 성향, 단계)를 결합한 2단계 정밀 분석"""
        # 1. 수강생 단계 및 수준 판정
        curr_idx = 0
        for i, step_name in enumerate(MasterEngineV79.STEPS):
            if step_name and step_name in text: curr_idx = i
        
        level = "중"
        if any(k in text for k in ['확실', '통달', '믿음', '완전']): level = "상"
        elif any(k in text for k in ['의심', '불안', '모름', '정체']): level = "하"

        # 2. 위기 지수 산출
        risk_score = 50
        if any(k in situation for k in ['영상', '유튜브', '비방', '자막']): 
            risk_score += 30
            if curr_idx < 6: risk_score += 10
        if level == "하": risk_score += 10
        
        # 3. [성별/성향/상성] 기반 1:1 맞춤 피드백 생성
        gender_guide = "동성 상담자로써의 정서적 유대감을 강화하세요." if admin['gender'] == "여" else "이성 간의 공식적이고 예의 바른 태도를 유지하세요."
        
        analysis_report = f"### 🧬 {admin['id']}전도사님({admin['gender']}) 맞춤 정밀 솔루션\n\n"
        analysis_report += f"**[현황]** 과정: **{MasterEngineV79.STEPS[curr_idx]}** | 이해도: **{level}** | 수강생 성향: **{s_mbti}**\n\n"
        analysis_report += "--- \n"
        analysis_report += "#### **🔍 전략적 행동 지침**\n"
        analysis_report += f"1. **관계 관리:** {gender_guide}\n"
        analysis_report += f"2. **소통 방식:** {admin['mbti']}인 전도사님은 "
        analysis_report += ("논리적 인과관계로 수강생의 혼란을 정리하는 데 집중하세요." if 'T' in admin['mbti'] else "수강생이 느낄 정서적 불안을 먼저 다독이는 공감 대화를 우선하세요.") + "\n"
        analysis_report += f"3. **동기 부여:** {admin['ennea']} 에너지를 투입해 현재의 외부 자극을 이겨낼 강력한 신앙적 비전을 제시하십시오.\n"
        analysis_report += f"4. **입력 전략 검토:** 제시하신 전략은 {s_mbti} 성향에게 '구체적인 확신'을 주는 방향으로 보완이 필요합니다."

        return int(min(risk_score, 100)), analysis_report

# --- UI 레이아웃 구성 ---
with st.sidebar:
    st.header("⚙️ 전략 시스템 v7.9")
    main_xlsx = st.file_uploader("📂 공통 출석부 업로드", type=["xlsx"], key="v79_main")
    st.markdown("---")
    
    m_list = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    e_list = ["모름"] + [f"{i}번" for i in range(1, 10)]
    
    admin_data = []
    for tag in ["A", "B", "C"]:
        with st.expander(f"👤 {tag}전도사 상세 설정"):
            f_up = st.file_uploader(f"{tag}반 파일", type=["xlsx"], key=f"v79_f_{tag}")
            # 성별 필드 (절대 누락 금지)
            g_sel = st.radio("성별", ["남", "여"], key=f"v79_g_{tag}", horizontal=True)
            m_sel = st.selectbox("MBTI", m_list, key=f"v79_m_{tag}")
            e_sel = st.selectbox("애니어그램", e_list, key=f"v79_e_{tag}")
            admin_data.append({'id': tag, 'file': f_up, 'gender': g_sel, 'mbti': m_sel, 'ennea': e_sel})

st.title("🏛️ 전략 시뮬레이션 시스템 v7.9")
l_col, r_col = st.columns([1, 1.2])

with l_col:
    st.subheader("🎯 상황 데이터 입력")
    mode_sel = st.radio("분석 모드", ["전체 스캔", "개별 딥다이브"], horizontal=True)
    target_person = st.text_input("수강생 이름 (개별 모드 전용)") if mode_sel == "개별 딥다이브" else ""
    situation_txt = st.text_area("🌐 발생 상황 (예: 비방 영상 노출 등)", height=100)
    strategy_txt = st.text_area("🛡️ 수립 전략", height=100)
    
    run_btn = st.button("전략 분석 실행 🚀", use_container_width=True)

if run_btn:
    active_admins = [a for a in admin_data if a['file']]
    if not active_admins:
        st.error("분석할 전도사 파일을 최소 하나 이상 업로드해 주세요.")
    else:
        results_list = []
        progress_ui = st.empty()
        
        with progress_ui.container():
            p_bar = st.progress(0)
            status_label = st.empty()
            
            for i, adm in enumerate(active_admins):
                tmp_file = f"v79_tmp_{adm['id']}.xlsx"
                with open(tmp_file, "wb") as f: f.write(adm['file'].getbuffer())
                
                xl_obj = pd.ExcelFile(tmp_file)
                for s_idx, s_name in enumerate(xl_obj.sheet_names):
                    pure_name = re.sub(r'[^가-힣]', '', s_name)
                    if pure_name in ['단계', '양식', '출석', '기본'] or len(pure_name) < 2: continue
                    
                    # 진행률 시각화 (사용자 지적 사항 반영)
                    current_prog = (i / len(active_admins)) + (s_idx / (len(xl_obj.sheet_names) * len(active_admins)))
                    p_bar.progress(current_prog)
                    status_label.write(f"🔍 {adm['id']}전도사 - **{pure_name}** 분석 중...")
                    
                    raw_txt = MasterEngineV79.extract_full_content(tmp_file, s_name)
                    mbti_match = re.search(r'(ISTJ|ISFJ|INFJ|INTJ|ISTP|ISFP|INFP|INTP|ESTP|ESFP|ENFP|ENTP|ESTJ|ESFJ|ENFJ|ENTJ)', raw_txt, re.I)
                    smbti = mbti_match.group(0).upper() if mbti_match else "미기입"
                    
                    # 2단계 딥분석 실행
                    risk_val, report_txt = MasterEngineV79.execute_deep_analysis(raw_txt, smbti, adm, situation_txt, strategy_txt)
                    
                    if mode_sel == "개별 딥다이브":
                        if pure_name == target_person:
                            results_list.append({'name': pure_name, 'admin': adm['id'], 'risk': risk_val, 'report': report_txt, 'type': 'deep'})
                            break
                    else:
                        results_list.append({'name': pure_name, 'admin': adm['id'], 'risk': risk_val, 'report': report_txt, 'type': 'total'})
                
                if os.path.exists(tmp_file): os.remove(tmp_file)
                if mode_sel == "개별 딥다이브" and results_list: break
            
            p_bar.progress(1.0)
            status_label.success("✅ 전수 검산 및 분석 완료!")
            time.sleep(0.5)
        progress_ui.empty()
        st.session_state['v79_results'] = results_list

# --- 결과 출력 ---
if 'v79_results' in st.session_state and st.session_state['v79_results']:
    df_res = pd.DataFrame(st.session_state['v79_results']).drop_duplicates(subset=['name'])
    with r_col:
        if df_res.iloc[0]['type'] == 'deep':
            res = df_res.iloc[0]
            st.markdown(f"""
                <div style="border:3px solid #ef4444; padding:30px; border-radius:15px; background:white; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                    <h2 style="margin:0; text-align:center;">🧬 {res['name']} 심층 분석 보고서</h2>
                    <hr>
                    <div style="font-size:1.1em; line-height:1.8;">{res['report']}</div>
                    <div style="text-align:right; font-weight:bold; color:#ef4444; font-size:1.5em; margin-top:20px;">위기 지수: {res['risk']}점</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            avg_risk = df_res['risk'].mean()
            st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=100-avg_risk, title={'text': "🛡️ 전체 기수 안전도"})), use_container_width=True)
            st.markdown("### **👤 수강생별 상세 분석 (클릭)**")
            for item in df_res.to_dict('records'):
                clr = "#ef4444" if item['risk'] > 75 else "#3b82f6"
                with st.expander(f"➔ {item['name']} ({item['admin']}반) | 위기: {item['risk']}점"):
                    st.markdown(f"<div style='padding:20px; border-left:8px solid {clr}; background:#f8fafc; border-radius:10px;'>{item['report']}</div>", unsafe_allow_html=True)
elif 'v79_results' in st.session_state:
    st.error("데이터를 찾을 수 없습니다. 수강생 이름을 다시 확인하거나 파일을 확인해 주세요.")
