import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import os
from openpyxl import load_workbook

# 1. 페이지 설정
st.set_page_config(page_title="AI Strategy Master v6.8", page_icon="🏛️", layout="wide")

# 2. 고도화된 전략 엔진
class StrategyEngineV68:
    PROCESS_STEPS = ["", "마음사기", "수강 목적성 심기", "영 인지", "성경 인정", "선악구분", "시대구분", "말씀 인정", "종교 세계 인식", "약속의 목자 인정", "약속한 성전 인정"]

    @staticmethod
    def get_context_and_mbti(file_path, sheet_name):
        """시트 전체 스캔을 통해 문맥과 MBTI를 동시에 추출"""
        try:
            wb = load_workbook(file_path, data_only=True)
            ws = wb[sheet_name]
            all_text = ""
            for row in ws.iter_rows(values_only=True):
                for cell in row:
                    if cell: all_text += f" {str(cell).strip()}"
            
            mbtis = ["ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
            found_mbti = next((m for m in mbtis if m in all_text.upper()), "미기입")
            return all_text, found_mbti
        except: return "", "미기입"

    @staticmethod
    def run_simulation(text, mbti, admin, sit, strat):
        # 단계 및 이해도 분석 (내부 활용)
        curr_idx = 0
        for i, step in enumerate(StrategyEngineV68.PROCESS_STEPS):
            if step and step in text: curr_idx = i
        
        # 이해도 판단 (상/중/하)
        level = "중"
        if any(kw in text for kw in ['확실', '통달', '믿음', '완전']): level = "상"
        elif any(kw in text for kw in ['불안', '의심', '정체', '초입']): level = "하"

        # 위기 지수 계산
        base_risk = 55
        media_risk = 30 if any(k in sit for k in ['http', 'youtube', '영상', '자막']) else 0
        
        # [핵심] 단계별/이해도별 취약점 연산
        if curr_idx < 6 and level == "하": media_risk *= 1.3 # 초반 단계 이해도 낮을 시 위험도 급증
        
        final_risk = min(max(base_risk + media_threat - (15 if level == "상" else 0), 0), 100)
        
        # [핵심] 전도사 성향과 수강생 정보를 융합한 제안 생성
        advice = f"**[{admin['id']}전도사님 맞춤 전략]**\n"
        if level == "하":
            advice += f"현재 수강생은 '{StrategyEngineV68.PROCESS_STEPS[curr_idx]}' 단계 정착이 불안정합니다. "
            advice += f"전도사님의 {admin['mbti']} 성향을 살려 " + ("교리적 의구심을 팩트로 해소" if 'T' in admin['mbti'] else "정서적 유대감을 강화하여 심리적 방어벽을 구축") + "해야 합니다."
        else:
            advice += f"'{StrategyEngineV68.PROCESS_STEPS[curr_idx]}' 과정을 잘 이해하고 있으니, "
            advice += f"{admin['ennea']}형의 에너지를 활용해 다음 단계로의 확신을 이끌어내십시오."

        return int(final_risk), advice

# 3. 레이아웃 (사이드바 입력란 누적 검토)
with st.sidebar:
    st.header("⚙️ 하이퍼 설정 v6.8")
    common_file = st.file_uploader("📂 공통 출석부 업로드", type=["xlsx"], key="main_v68")
    st.markdown("---")
    
    m_opts = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    e_opts = ["모름"] + [f"{i}번" for i in range(1, 10)]
    
    admins = []
    for t in ["A", "B", "C"]:
        with st.expander(f"👤 {t}전도사 프로필"):
            f = st.file_uploader(f"{t}반 파일", type=["xlsx"], key=f"f68_{t}")
            c1, c2 = st.columns(2)
            with c1:
                m_in = st.selectbox("MBTI", m_opts, key=f"m68_{t}")
                g_in = st.radio("성별", ["남", "여", "모름"], index=2, key=f"g68_{t}")
            with c2:
                e_in = st.selectbox("애니어그램", e_opts, key=f"e68_{t}")
            admins.append({'id': t, 'file': f, 'mbti': m_in, 'ennea': e_in})

# 4. 메인 분석부
st.title("🏛️ 전략 시뮬레이션 시스템 v6.8")
col_l, col_r = st.columns([1, 1.2])

with col_l:
    st.subheader("🎯 상황 데이터 입력")
    sit_in = st.text_area("🌐 발생 상황 및 영상 텍스트", height=100)
    strat_in = st.text_area("🛡️ 대응 전략", height=100)
    
    if st.button("무결점 정밀 분석 실행 🚀", use_container_width=True):
        active_admins = [a for a in admins if a['file']]
        if not active_admins:
            st.error("분석할 파일을 하나 이상 업로드해주세요.")
        else:
            sim_results = []
            msg_box = st.empty()
            p_bar = st.progress(0)
            
            for i, adm in enumerate(active_admins):
                tmp_path = f"v68_temp_{adm['id']}.xlsx"
                with open(tmp_path, "wb") as f: f.write(adm['file'].getbuffer())
                
                xl = pd.ExcelFile(tmp_path)
                for s_idx, s_name in enumerate(xl.sheet_names):
                    pure_n = re.sub(r'[^가-힣]', '', s_name)
                    if pure_n in ['단계', '양식', '기본', '출석'] or len(pure_n) < 2: continue
                    
                    msg_box.info(f"⏳ {adm['id']}전도사 - {pure_n} 심리 분석 중...")
                    p_bar.progress((i/len(active_admins)) + (s_idx/(len(xl.sheet_names)*len(active_admins))))
                    
                    full_text, s_mbti = StrategyEngineV68.get_context_and_mbti(tmp_path, s_name)
                    risk, advice = StrategyEngineV68.run_simulation(full_text, s_mbti, adm, sit_in, strat_in)
                    sim_results.append({'name': pure_n, 'admin': adm['id'], 'risk': risk, 'advice': advice})
                
                if os.path.exists(tmp_path): os.remove(tmp_path)
            
            p_bar.progress(1.0)
            msg_box.success("✅ 분석이 완료되었습니다!")
            st.session_state['v68_res'] = sim_results

# 5. 결과 시각화
if 'v68_res' in st.session_state and st.session_state['v68_res']:
    df = pd.DataFrame(st.session_state['v68_res']).drop_duplicates(subset=['name'])
    with col_r:
        st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=100-df['risk'].mean(), title={'text': "🛡️ 전체 안전 지수"})), use_container_width=True)

    st.markdown("---")
    grid = st.columns(3)
    for idx, r in enumerate(df.to_dict('records')):
        with grid[idx % 3]:
            card_color = "#ef4444" if r['risk'] > 70 else "#3b82f6"
            st.markdown(f"""
                <div style="border-top:5px solid {card_color}; padding:20px; background:white; border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.1); margin-bottom:20px; min-height:280px;">
                    <h3 style="margin:0;">{r['name']} <small style="font-size:0.6em; color:#64748b;">({r['admin']}반)</small></h3>
                    <hr style="margin:15px 0;">
                    <div style="font-size:0.9em; line-height:1.6; color:#334155;">{r['advice']}</div>
                    <div style="text-align:right; font-weight:bold; color:{card_color}; font-size:1.1em; margin-top:20px;">위기 지수: {r['risk']}점</div>
                </div>
            """, unsafe_allow_html=True)
