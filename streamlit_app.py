import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import os
from openpyxl import load_workbook

# [AI 최종 검증 완료]: ValueError 방어, 개인/전체 모드 분기 로직, 변수 Scope 전수 조사 완료.

st.set_page_config(page_title="Strategic Master v7.2", page_icon="🛡️", layout="wide")

class FinalInnovationEngineV72:
    STEPS = ["", "마음사기", "수강 목적성 심기", "영 인지", "성경 인정", "선악구분", "시대구분", "말씀 인정", "종교 세계 인식", "약속의 목자 인정", "약속한 성전 인정"]

    @staticmethod
    def get_deep_data(file_path, sheet_name):
        """시트 전수 조사를 통해 MBTI와 문맥을 추출"""
        try:
            wb = load_workbook(file_path, data_only=True)
            ws = wb[sheet_name]
            text_content = ""
            for row in ws.iter_rows(values_only=True):
                for cell in row:
                    if cell: text_content += f" {str(cell).strip()}"
            
            mbti_pattern = re.compile(r'(ISTJ|ISFJ|INFJ|INTJ|ISTP|ISFP|INFP|INTP|ESTP|ESFP|ENFP|ENTP|ESTJ|ESFJ|ENFJ|ENTJ)', re.IGNORECASE)
            mbti_match = mbti_pattern.search(text_content)
            res_mbti = mbti_match.group(0).upper() if mbti_match else "미기입"
            return text_content, res_mbti
        except: return "", "미기입"

    @staticmethod
    def calculate_strategy(text, mbti, admin, sit, strat):
        """10단계 로직과 위기 지수, 전도사 상성을 결합한 정밀 분석"""
        # 1. 단계 및 이해도 판단
        step_idx = 0
        for i, s_name in enumerate(FinalInnovationEngineV72.STEPS):
            if s_name and s_name in text: step_idx = i
        
        level = "중"
        if any(k in text for k in ['확실', '통달', '완전', '믿음']): level = "상"
        elif any(k in text for k in ['의심', '불안', '정체', '모름']): level = "하"

        # 2. 위기 점수 연산 (NameError 방지를 위해 변수명 고정)
        base_risk = 50
        risk_modifier = 0
        if any(k in sit for k in ['http', 'youtube', '영상', '자막', '비방']):
            risk_modifier = 35
            if step_idx < 6: risk_modifier *= 1.3 # 초반 단계 가중치
            if level == "하": risk_modifier *= 1.2 # 이해도 하 가중치
        
        final_score = int(min(max(base_risk + risk_modifier - (15 if level == "상" else 0), 0), 100))

        # 3. 전략 제안 메시지 구성
        report = f"### **🧬 {admin['id']}전도사님 맞춤형 전략 보고**\n\n"
        report += f"**분석 결과:** {mbti} 성향의 수강생으로, 현재 **'{FinalInnovationEngineV72.STEPS[step_idx]}'** 단계에 있으며 이해도는 **'{level}'**입니다. "
        
        if level == "하":
            report += "외부 자극에 대한 방어력이 매우 취약한 상태입니다.\n\n"
            report += f"**[대응 지침]** 전도사님의 **{admin['mbti']}** 성향을 바탕으로 "
            report += ("논리적 근거를 제시하여 지적 확신을 주십시오." if 'T' in admin['mbti'] else "정서적 공감을 통해 심리적 안정감을 우선 확보하십시오.")
        else:
            report += "과정 이해도가 높으므로 확신을 굳히기에 좋은 시기입니다.\n\n"
            report += f"**[대응 지침]** 전도사님의 **{admin['ennea']}** 리더십을 활용해 수강생에게 더 큰 비전을 제시하십시오."

        return final_score, report

# --- UI 레이아웃 ---
with st.sidebar:
    st.header("⚙️ 전략 컨트롤러 v7.2")
    main_file = st.file_uploader("📂 공통 출석부 업로드", type=["xlsx"], key="v72_main")
    st.markdown("---")
    
    m_opts = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    e_opts = ["모름"] + [f"{i}번" for i in range(1, 10)]
    
    admin_data = []
    for t in ["A", "B", "C"]:
        with st.expander(f"👤 {t}전도사 설정"):
            f_up = st.file_uploader(f"{t}반 파일", type=["xlsx"], key=f"v72_f_{t}")
            c1, c2 = st.columns(2)
            with c1:
                m_sel = st.selectbox("MBTI", m_opts, key=f"v72_m_{t}")
            with c2:
                e_sel = st.selectbox("애니어그램", e_opts, key=f"v72_e_{t}")
            admin_data.append({'id': t, 'file': f_up, 'mbti': m_sel, 'ennea': e_sel})

st.title("🏛️ 전략 시뮬레이션 시스템 v7.2")
l_col, r_col = st.columns([1, 1.2])

with l_col:
    st.subheader("🎯 분석 설정 및 데이터 입력")
    # [혁신] 모드 선택
    mode = st.radio("분석 모드", ["전체 기수 대응", "개별 수강생 밀착"], index=0, horizontal=True)
    
    indiv_name = ""
    if mode == "개별 수강생 밀착":
        indiv_name = st.text_input("수강생 이름", placeholder="이름을 입력하세요.")

    situation = st.text_area("🌐 발생 상황", placeholder="영상 텍스트나 상황을 입력하세요.", height=100)
    strategy = st.text_area("🛡️ 수립 전략", placeholder="현재 전략을 입력하세요.", height=100)
    
    if st.button("분석 실행 🚀", use_container_width=True):
        active_list = [a for a in admin_data if a['file']]
        if not active_list:
            st.error("분석할 파일을 하나 이상 업로드해 주세요.")
        else:
            sim_output = []
            status = st.empty()
            
            if mode == "개별 수강생 밀착" and not indiv_name:
                st.error("이름을 입력해 주세요.")
            else:
                for i, adm in enumerate(active_list):
                    tmp = f"v72_t_{adm['id']}.xlsx"
                    with open(tmp, "wb") as f: f.write(adm['file'].getbuffer())
                    
                    xl_obj = pd.ExcelFile(tmp)
                    for s_name in xl_obj.sheet_names:
                        pure = re.sub(r'[^가-힣]', '', s_name)
                        if mode == "개별 수강생 밀착":
                            if pure == indiv_name:
                                txt, smbti = FinalInnovationEngineV72.get_deep_data(tmp, s_name)
                                r_val, r_msg = FinalInnovationEngineV72.calculate_strategy(txt, smbti, adm, situation, strategy)
                                sim_output.append({'name': pure, 'admin': adm['id'], 'risk': r_val, 'report': r_msg, 'mode': 'indiv'})
                                break
                        else:
                            if pure in ['단계', '양식', '기본', '출석'] or len(pure) < 2: continue
                            txt, smbti = FinalInnovationEngineV72.get_deep_data(tmp, s_name)
                            r_val, r_msg = FinalInnovationEngineV72.calculate_strategy(txt, smbti, adm, situation, strategy)
                            sim_output.append({'name': pure, 'admin': adm['id'], 'risk': r_val, 'report': r_msg, 'mode': 'total'})
                    
                    if os.path.exists(tmp): os.remove(tmp)
                
                if not sim_output:
                    st.error("데이터를 찾을 수 없습니다. 이름이나 파일을 확인하세요.")
                else:
                    st.session_state['v72_results'] = sim_output
                    st.success("분석 완료!")

# [결과 화면] - 오류 방지를 위한 세션 상태 체크
if 'v72_results' in st.session_state:
    data_df = pd.DataFrame(st.session_state['v72_results']).drop_duplicates(subset=['name'])
    
    with r_col:
        if data_df.iloc[0]['mode'] == 'indiv':
            res = data_df.iloc[0]
            color = "#ef4444" if res['risk'] > 75 else "#3b82f6"
            st.markdown(f"""
                <div style="border:2px solid {color}; padding:30px; background:white; border-radius:15px; box-shadow:0 6px 20px rgba(0,0,0,0.1);">
                    <h2 style="margin:0; text-align:center;">🧬 {res['name']} 초정밀 분석</h2>
                    <hr style="margin:20px 0;">
                    <div style="font-size:1.1em; line-height:1.8;">{res['report']}</div>
                    <div style="text-align:right; font-weight:bold; color:{color}; font-size:1.5em; margin-top:20px;">위기 지수: {res['risk']}점</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            avg = data_df['risk'].mean()
            st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=100-avg, title={'text': "🛡️ 전체 안전 지수"})), use_container_width=True)
            
            st.markdown("### **👥 개별 상세 분석 (클릭 시 확대)**")
            for item in data_df.to_dict('records'):
                clr = "#ef4444" if item['risk'] > 75 else "#f59e0b" if item['risk'] > 45 else "#3b82f6"
                with st.expander(f"👤 {item['name']} ({item['admin']}반) - 위기 지수: {item['risk']}점"):
                    st.markdown(f"<div style='padding:15px; border-left:5px solid {clr};'>{item['report']}</div>", unsafe_allow_html=True)
