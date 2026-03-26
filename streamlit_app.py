import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import os
from openpyxl import load_workbook

# 1. 페이지 설정
st.set_page_config(page_title="AI Strategy Master v6.9", page_icon="🏛️", layout="wide")

# 2. 마스터 분석 엔진
class FinalMasterEngineV69:
    # 사용자 정의 10단계 과정
    STEPS = ["", "마음사기", "수강 목적성 심기", "영 인지", "성경 인정", "선악구분", "시대구분", "말씀 인정", "종교 세계 인식", "약속의 목자 인정", "약속한 성전 인정"]

    @staticmethod
    def get_sheet_data(file_path, sheet_name):
        """시트 전체 텍스트 추출 및 MBTI 식별"""
        try:
            wb = load_workbook(file_path, data_only=True)
            ws = wb[sheet_name]
            combined_text = ""
            for row in ws.iter_rows(values_only=True):
                for cell in row:
                    if cell: combined_text += f" {str(cell).strip()}"
            
            mbti_list = ["ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
            s_mbti = next((m for m in mbti_list if m in combined_text.upper()), "미기입")
            return combined_text, s_mbti
        except: return "", "미기입"

    @staticmethod
    def predict_strategy(text, s_mbti, admin, sit, strat):
        """단계-이해도-전도사성향-외부위협 통합 연산"""
        # 단계 추출
        curr_step_idx = 0
        for i, step_name in enumerate(FinalMasterEngineV69.STEPS):
            if step_name and step_name in text: curr_step_idx = i
        
        # 이해도(질적 지표) 분석
        level_grade = "중"
        if any(kw in text for kw in ['확실', '통달', '믿음', '완전', '수료']): level_grade = "상"
        elif any(kw in text for kw in ['불안', '의심', '정체', '초입', '모름']): level_grade = "하"

        # 위기 점수(Risk) 계산 로직 - 변수명 통일 (media_threat 오류 해결)
        risk_val = 55 
        
        # 외부 위협(영상/링크) 분석
        if any(k in sit for k in ['http', 'youtube', '영상', '자막', '비방']):
            threat_weight = 30
            # 초반 단계이거나 이해도가 낮으면 위협 가중치 증가
            if curr_step_idx < 6 or level_grade == "하": threat_weight *= 1.4
            risk_val += threat_weight
        
        # 이해도에 따른 가감점
        if level_grade == "상": risk_val -= 15
        elif level_grade == "하": risk_val += 10
        
        # 전도사 상성 반영 조언 생성
        advice_msg = f"**[{admin['id']}전도사님 전용 매칭 전략]**\n"
        if level_grade == "하":
            advice_msg += f"현재 수강생은 '{FinalMasterEngineV69.STEPS[curr_step_idx]}' 단계의 개념이 흔들리고 있습니다. "
            if 'T' in admin['mbti']:
                advice_msg += "전도사님의 논리적 분석력을 발휘해 의문을 팩트로 잠재우십시오."
            else:
                advice_msg += "전도사님의 따뜻한 공감 능력으로 심리적 안정을 주는 것이 급선무입니다."
        else:
            advice_msg += f"'{FinalMasterEngineV69.STEPS[curr_step_idx]}' 단계를 훌륭히 소화 중입니다. "
            advice_msg += f"{admin['ennea']}형 특유의 리더십으로 확신을 굳히는 상담을 권장합니다."

        return int(min(max(risk_val, 0), 100)), advice_msg

# 3. 사이드바 (누적 요구사항: 공통 출석부 + 전도사 프로필)
with st.sidebar:
    st.header("⚙️ 하이퍼 마스터 v6.9")
    main_xlsx = st.file_uploader("📂 공통 출석부 업로드", type=["xlsx"], key="final_main")
    st.markdown("---")
    
    m_opts = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    e_opts = ["모름"] + [f"{i}번" for i in range(1, 10)]
    
    admin_profiles = []
    for tag in ["A", "B", "C"]:
        with st.expander(f"👤 {tag}전도사 프로필 설정"):
            f_in = st.file_uploader(f"{tag}반 개별 파일", type=["xlsx"], key=f"v69_f_{tag}")
            c1, c2 = st.columns(2)
            with c1:
                m_in = st.selectbox("MBTI", m_opts, key=f"v69_m_{tag}")
                g_in = st.radio("성별", ["남", "여", "모름"], index=2, key=f"v69_g_{tag}")
            with c2:
                e_in = st.selectbox("애니어그램", e_opts, key=f"v69_e_{tag}")
            admin_profiles.append({'id': tag, 'file': f_in, 'mbti': m_in, 'ennea': e_in})

# 4. 메인 대시보드
st.title("🏛️ 전략 시뮬레이션 시스템 v6.9")
col_inp, col_out = st.columns([1, 1.2])

with col_inp:
    st.subheader("🎯 시나리오 데이터 입력")
    scenario_sit = st.text_area("🌐 발생 상황 (유튜브 링크 등)", placeholder="영상 텍스트나 발생 상황을 입력하세요.", height=100)
    scenario_strat = st.text_area("🛡️ 대응 관리 전략", placeholder="현재 구상 중인 전략을 입력하세요.", height=100)
    
    if st.button("최종 정밀 시뮬레이션 가동 🚀", use_container_width=True):
        active_admins = [a for a in admin_profiles if a['file']]
        if not active_admins:
            st.error("분석할 엑셀 파일을 업로드해 주세요.")
        else:
            final_results = []
            status_msg = st.empty()
            progress_bar = st.progress(0)
            
            for i, adm in enumerate(active_admins):
                temp_file = f"v69_tmp_{adm['id']}.xlsx"
                with open(temp_file, "wb") as f: f.write(adm['file'].getbuffer())
                
                excel = pd.ExcelFile(temp_file)
                for s_idx, s_name in enumerate(excel.sheet_names):
                    # 수강생 이름 정제 및 필터링
                    name_clean = re.sub(r'[^가-힣]', '', s_name)
                    if name_clean in ['단계', '양식', '기본', '출석', '전체'] or len(name_clean) < 2:
                        continue
                    
                    status_msg.info(f"⏳ {adm['id']}전도사 - {name_clean} 데이터 심층 대조 중...")
                    progress_bar.progress((i/len(active_admins)) + (s_idx/(len(excel.sheet_names)*len(active_admins))))
                    
                    # 데이터 추출 및 연산
                    s_context, s_mbti = FinalMasterEngineV69.get_sheet_data(temp_file, s_name)
                    risk_score, strategy_advice = FinalMasterEngineV69.predict_strategy(s_context, s_mbti, adm, scenario_sit, scenario_strat)
                    
                    final_results.append({'name': name_clean, 'admin': adm['id'], 'risk': risk_score, 'advice': strategy_advice})
                
                if os.path.exists(temp_file): os.remove(temp_file)
            
            progress_bar.progress(1.0)
            status_msg.success("✅ 모든 수강생 데이터 분석 완료!")
            st.session_state['v69_data'] = final_results

# 5. 결과 시각화 (하이퍼 카드 레이아웃)
if 'v69_data' in st.session_state and st.session_state['v69_data']:
    res_df = pd.DataFrame(st.session_state['v69_data']).drop_duplicates(subset=['name'])
    with col_out:
        avg_risk = res_df['risk'].mean()
        st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=100-avg_risk, title={'text': "🛡️ 기수 통합 안전 지수"})), use_container_width=True)

    st.markdown("---")
    grid_cols = st.columns(3)
    for idx, row in enumerate(res_df.to_dict('records')):
        with grid_cols[idx % 3]:
            # 위기 지수에 따른 색상 코드
            status_color = "#ef4444" if row['risk'] > 75 else "#f59e0b" if row['risk'] > 45 else "#3b82f6"
            st.markdown(f"""
                <div style="border-top:6px solid {status_color}; padding:20px; background:white; border-radius:12px; box-shadow:0 4px 15px rgba(0,0,0,0.15); margin-bottom:20px; min-height:320px;">
                    <h3 style="margin:0; color:#1e293b;">{row['name']} <small style="font-size:0.6em; color:#64748b;">({row['admin']}반)</small></h3>
                    <hr style="margin:15px 0; border:0.5px solid #eee;">
                    <div style="font-size:0.92em; line-height:1.7; color:#334155; min-height:120px;">
                        {row['advice']}
                    </div>
                    <div style="text-align:right; font-weight:bold; color:{status_color}; font-size:1.2em; margin-top:20px;">
                        위기 지수: {row['risk']}점
                    </div>
                </div>
            """, unsafe_allow_html=True)
