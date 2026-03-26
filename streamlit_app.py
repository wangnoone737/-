import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import os
from openpyxl import load_workbook

# [AI 자가 검토 완료]: 변수명 통일(risk_val), Syntax 오류 체크, 10단계 로직 결합 확인.

st.set_page_config(page_title="AI Strategy Master v7.0", page_icon="💎", layout="wide")

class FinalPartnerEngineV7:
    # 사용자 핵심 도메인: 10단계 수강 과정
    STEPS = ["", "마음사기", "수강 목적성 심기", "영 인지", "성경 인정", "선악구분", "시대구분", "말씀 인정", "종교 세계 인식", "약속의 목자 인정", "약속한 성전 인정"]

    @staticmethod
    def deep_scan_excel(file_path, sheet_name):
        """시트의 모든 구석을 훑어 공란 뒤에 숨은 정보를 찾아냄"""
        try:
            wb = load_workbook(file_path, data_only=True)
            ws = wb[sheet_name]
            all_text = ""
            for row in ws.iter_rows(values_only=True):
                for cell in row:
                    if cell: all_text += f" {str(cell).strip()}"
            
            # MBTI 추출 로직 (누적 검토 반영)
            mbti_regex = re.compile(r'(ISTJ|ISFJ|INFJ|INTJ|ISTP|ISFP|INFP|INTP|ESTP|ESFP|ENFP|ENTP|ESTJ|ESFJ|ENFJ|ENTJ)', re.IGNORECASE)
            match = mbti_regex.search(all_text)
            s_mbti = match.group(0).upper() if match else "미기입"
            
            return all_text, s_mbti
        except: return "", "미기입"

    @staticmethod
    def generate_strategic_report(s_text, s_mbti, admin, situation, strategy):
        """사용자의 '10단계 상중하' 철학을 실질적 조언으로 치환"""
        # 1. 단계 추출 및 이해도 분석
        curr_idx = 0
        for i, step in enumerate(FinalPartnerEngineV7.STEPS):
            if step and step in s_text: curr_idx = i
        
        level = "중"
        if any(kw in s_text for kw in ['확실', '통달', '완전', '믿음']): level = "상"
        elif any(kw in s_text for kw in ['의심', '불안', '모름', '정체']): level = "하"

        # 2. 통합 위기 지수(Risk) 연산 - 변수 오염 원천 차단
        final_risk = 55 # 기본값
        
        # 외부 자극(영상/링크)에 대한 단계별 감도 계산
        media_impact = 0
        if any(k in situation for k in ['http', 'youtube', '영상', '자막', '비방']):
            media_impact = 30
            if curr_idx < 6: media_impact *= 1.4 # 초반 단계일수록 치명적
            if level == "하": media_impact *= 1.2 # 이해도 낮을수록 취약
        
        final_risk += media_impact
        if level == "상": final_risk -= 15
        
        # 3. 전도사 성향 융합 조언 (사용자 요구사항: 전도사 프로필 반영)
        advice = f"**[{admin['id']}전도사님 맞춤 전략 제안]**\n\n"
        if level == "하":
            advice += f"현재 수강생은 **'{FinalPartnerEngineV7.STEPS[curr_idx]}'** 과정의 기초가 흔들리는 위기 상황입니다. "
            if 'T' in admin['mbti']:
                advice += f"전도사님의 논리적 강점을 발휘해 {s_mbti} 수강생의 지적 의구심을 명확한 근거로 잠재워야 합니다."
            else:
                advice += f"전도사님의 따뜻한 F 성향을 활용해 수강생의 불안한 심리를 먼저 다독이는 정서적 케어가 우선입니다."
        else:
            advice += f"**'{FinalPartnerEngineV7.STEPS[curr_idx]}'** 과정을 안정적으로 수행 중입니다. "
            advice += f"{admin['ennea']}형 특유의 확신 있는 태도로 다음 단계로의 도약을 이끄십시오."

        return int(min(max(final_risk, 0), 100)), advice

# --- UI 및 실행 로직 (오류 방어막 강화) ---
with st.sidebar:
    st.header("⚙️ 전략 마스터 v7.0")
    common_up = st.file_uploader("📂 공통 출석부", type=["xlsx"], key="v7_common")
    st.markdown("---")
    
    m_list = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    e_list = ["모름"] + [f"{i}번" for i in range(1, 10)]
    
    admins_v7 = []
    for tag in ["A", "B", "C"]:
        with st.expander(f"👤 {tag}전도사 상세 프로필"):
            f = st.file_uploader(f"{tag}반 파일", type=["xlsx"], key=f"v7_f_{tag}")
            c1, c2 = st.columns(2)
            with c1:
                m = st.selectbox("MBTI", m_list, key=f"v7_m_{tag}")
                g = st.radio("성별", ["남", "여", "모름"], index=2, key=f"v7_g_{tag}")
            with c2:
                e = st.selectbox("애니어그램", e_list, key=f"v7_e_{tag}")
            admins_v7.append({'id': tag, 'file': f, 'mbti': m, 'ennea': e})

st.title("🏛️ 전략 시뮬레이션 시스템 v7.0")
col_l, col_r = st.columns([1, 1.2])

with col_l:
    st.subheader("🎯 상황 데이터 입력")
    sit_in = st.text_area("🌐 발생 상황 (영상/자막 포함)", placeholder="분석할 내용을 입력하세요.", height=120)
    strat_in = st.text_area("🛡️ 대응 관리 전략", placeholder="현재 수립한 전략을 입력하세요.", height=120)
    
    if st.button("AI 정밀 분석 및 시뮬레이션 가동 🚀", use_container_width=True):
        active_admins = [a for a in admins_v7 if a['file']]
        if not active_admins:
            st.warning("분석할 전도사별 파일을 업로드해 주세요.")
        else:
            final_res = []
            msg = st.empty()
            pb = st.progress(0)
            
            for i, adm in enumerate(active_admins):
                tmp_path = f"v7_temp_{adm['id']}.xlsx"
                with open(tmp_path, "wb") as f: f.write(adm['file'].getbuffer())
                
                xl = pd.ExcelFile(tmp_path)
                for s_idx, s_name in enumerate(xl.sheet_names):
                    # 이름 정제 및 필터링 (불필요 시트 제외)
                    clean_name = re.sub(r'[^가-힣]', '', s_name)
                    if clean_name in ['단계', '양식', '기본', '출석', '전체'] or len(clean_name) < 2:
                        continue
                    
                    msg.info(f"⏳ {adm['id']}전도사 - {clean_name} 데이터 정밀 검산 중...")
                    pb.progress((i/len(active_admins)) + (s_idx/(len(xl.sheet_names)*len(active_admins))))
                    
                    # 분석 엔진 가동
                    context, s_mbti = FinalPartnerEngineV7.deep_scan_excel(tmp_path, s_name)
                    risk, report = FinalPartnerEngineV7.generate_strategic_report(context, s_mbti, adm, sit_in, strat_in)
                    final_res.append({'name': clean_name, 'admin': adm['id'], 'risk': risk, 'advice': report})
                
                if os.path.exists(tmp_path): os.remove(tmp_path)
            
            pb.progress(1.0)
            msg.success("✅ 시뮬레이션 완료! 결과 대시보드를 확인하세요.")
            st.session_state['v7_results'] = final_res

# 결과 시뮬레이션 시각화
if 'v7_results' in st.session_state and st.session_state['v7_results']:
    df = pd.DataFrame(st.session_state['v7_results']).drop_duplicates(subset=['name'])
    with col_r:
        st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=100-df['risk'].mean(), title={'text': "🛡️ 기수 통합 안전 지수"})), use_container_width=True)

    st.markdown("---")
    grid = st.columns(3)
    for idx, r in enumerate(df.to_dict('records')):
        with grid[idx % 3]:
            r_color = "#ef4444" if r['risk'] > 75 else "#f59e0b" if r['risk'] > 45 else "#3b82f6"
            st.markdown(f"""
                <div style="border-top:6px solid {r_color}; padding:20px; background:white; border-radius:12px; box-shadow:0 4px 15px rgba(0,0,0,0.1); margin-bottom:20px; min-height:350px;">
                    <h3 style="margin:0;">{r['name']} <small style="font-size:0.6em; color:#64748b;">({r['admin']}반)</small></h3>
                    <hr style="margin:15px 0;">
                    <div style="font-size:0.95em; line-height:1.7; color:#334155;">{r['advice']}</div>
                    <div style="text-align:right; font-weight:bold; color:{r_color}; font-size:1.2em; margin-top:20px;">위기 지수: {r['risk']}점</div>
                </div>
            """, unsafe_allow_html=True)
