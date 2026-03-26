import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import os
from openpyxl import load_workbook

# 1. 페이지 설정
st.set_page_config(page_title="AI Strategy Master v6.2", page_icon="🛡️", layout="wide")

# 2. 분석 엔진 (병합 구조 분석 + 상성 로직)
class MasterEngineV62:
    STAGE_MAP = {i: name for i, name in enumerate(["", "마음사기", "수강 목적성 심기", "영 인지", "성경 인정", "선악구분", "시대구분", "말씀 인정", "종교 세계 인식", "약속의 목자 인정", "약속한 성전 인정"])}

    @staticmethod
    def parse_hierarchical_data(file_path, sheet_name):
        """병합 셀 및 홀/짝 열 기반의 계층 구조 분석 (사용자 논리 적용)"""
        try:
            wb = load_workbook(file_path, data_only=True)
            ws = wb[sheet_name]
            data_map = {}
            # 속도와 분석 깊이의 균형 (최대 100행)
            for r in range(1, min(ws.max_row + 1, 100)):
                for c in range(1, ws.max_column + 1, 2):
                    label = ws.cell(row=r, column=c).value
                    value = ws.cell(row=r, column=c+1).value
                    if label and value:
                        data_map[str(label).strip()] = str(value).strip()
            return data_map
        except:
            return {}

    @staticmethod
    def run_simulation(s_data, admin, sit, strat):
        # 전체 맥락 합치기
        full_text = " ".join([f"{k}:{v}" for k, v in s_data.items()])
        
        # MBTI 추출
        mbtis = ["ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
        found_mbti = next((m for m in mbtis if m in full_text.upper()), "모름")
        
        # 단계 추출
        step_match = re.search(r'(\d+)', full_text)
        step_n = int(step_match.group(1)) if step_match else 0
        
        # 데이터 가이드 (부족한 정보 체크)
        missing = []
        if found_mbti == "모름": missing.append("MBTI")
        if step_n == 0: missing.append("단계")
        if not any(k in full_text for k in ['고민', '상황', '가족']): missing.append("상세배경")

        # 지수 계산 (유튜브 가중치 15점, 성향 보너스 12점 등 누적 로직)
        yt_v = 15 if any(u in sit for u in ["youtube", "youtu.be"]) else 0
        ctx_v = 10 if any(b in full_text for b in ['의심', '불안', '핍박']) else -5
        
        # 전도사 상성 보너스 (MBTI T/F 일치 시)
        match_b = 0
        if found_mbti != "모름" and admin['mbti'] != "모름":
            if found_mbti[2] == admin['mbti'][2]: match_b = 7
            
        strat_b = 0
        if found_mbti != "모름":
            if 'T' in found_mbti and any(w in strat for w in ['논리', '팩트', '근거']): strat_b = 12
            if 'F' in found_mbti and any(w in strat for w in ['공감', '위로', '경청']): strat_b = 12

        final_risk = min(max(55 + (step_n * 2) + yt_v + ctx_v - match_b - strat_bonus, 0), 100)
        
        feedback = f"[{admin['id']}전도사 매칭] {found_mbti} 성향 분석 결과: "
        feedback += "정밀한 교리적 설명이 효과적입니다." if 'T' in found_mbti else "따뜻한 공감과 유대가 위기를 낮춥니다."
        
        return final_risk, MasterEngineV62.STAGE_MAP.get(step_n, "확인중"), feedback, missing

# 3. 사이드바 (모든 입력란 통합 복구)
with st.sidebar:
    st.header("⚙️ 통합 설정 v6.2")
    
    # [복구] 공통 출석부 입력란
    st.subheader("1. 공통 데이터")
    common_file = st.file_uploader("전체 출석부 파일", type=["xlsx"], key="main_excel")
    st.markdown("---")
    
    # 전도사별 설정 (MBTI, 애니어그램 포함)
    m_list = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    e_list = ["모름"] + [f"{i}번" for i in range(1, 10)]
    
    admins_cfg = []
    for tag in ["A", "B", "C"]:
        with st.expander(f"👤 {tag}전도사 상세 프로필"):
            f_up = st.file_uploader(f"{tag}반 개별 파일", type=["xlsx"], key=f"file_{tag}")
            c1, c2 = st.columns(2)
            with c1:
                m_sel = st.selectbox("MBTI", m_list, key=f"mbti_{tag}")
                g_sel = st.radio("성별", ["남", "여", "모름"], index=2, key=f"gender_{tag}")
            with c2:
                e_sel = st.selectbox("애니어그램", e_list, key=f"ennea_{tag}")
            admins_cfg.append({'id': tag, 'file': f_up, 'mbti': m_sel, 'ennea': e_sel, 'gender': g_sel})

# 4. 메인 화면
st.title("🏛️ 전략 시뮬레이션 시스템 v6.2")
col_l, col_r = st.columns([1, 1.2])

with col_l:
    st.subheader("🎯 시나리오 입력")
    sit_in = st.text_area("🌐 발생 상황", placeholder="예: 주변 사람의 비방을 들음", height=80)
    strat_in = st.text_area("🛡️ 대응 전략", placeholder="예: 확실한 근거로 오해 불식", height=80)
    if st.button("AI 정밀 분석 가동 🚀", use_container_width=True):
        active_admins = [a for a in admins_cfg if a['file']]
        if not active_admins:
            st.error("분석할 전도사별 파일을 업로드해주세요.")
        else:
            results = []
            msg_box = st.empty()
            p_bar = st.progress(0)
            
            for i, adm in enumerate(active_admins):
                tmp_fn = f"temp_v62_{adm['id']}.xlsx"
                with open(tmp_fn, "wb") as f: f.write(adm['file'].getbuffer())
                
                xl = pd.ExcelFile(tmp_fn)
                for s_idx, s_name in enumerate(xl.sheet_names):
                    msg_box.info(f"⏳ {adm['id']}전도사 - {s_name} 분석 중...")
                    p_bar.progress((i / len(active_admins)) + (s_idx / (len(xl.sheet_names) * len(active_admins))))
                    
                    # 구조 분석 및 데이터 매칭
                    s_info = MasterEngineV62.parse_hierarchical_data(tmp_fn, s_name)
                    # 이름 정제 (단계 단어 제외)
                    pure_name = re.sub(r'[^가-힣]', '', s_name)
                    if pure_name and len(pure_name) >= 2 and pure_name != '단계':
                        risk, stage, advice, miss = MasterEngineV62.run_simulation(s_info, adm, sit_in, strat_in)
                        results.append({'name': pure_name, 'admin': adm['id'], 'risk': risk, 'stage': stage, 'advice': advice, 'missing': miss})
                
                if os.path.exists(tmp_fn): os.remove(tmp_fn)
            
            p_bar.progress(1.0)
            msg_box.success("✅ 모든 분석이 완료되었습니다!")
            
            # 결과 저장 (세션 상태 활용)
            st.session_state['sim_results'] = results

# 5. 결과 대시보드 표시
if 'sim_results' in st.session_state and st.session_state['sim_results']:
    res_df = pd.DataFrame(st.session_state['sim_results']).drop_duplicates(subset=['name'])
    
    with col_r:
        avg_s = 100 - res_df['risk'].mean()
        st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=avg_s, title={'text': "🛡️ 기수 안전 점수"}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "darkgreen"}})), use_container_width=True)

    st.markdown("---")
    grid = st.columns(3)
    for idx, r in enumerate(res_df.to_dict('records')):
        with grid[idx % 3]:
            risk_c = "#ef4444" if r['risk'] > 70 else "#f59e0b" if r['risk'] > 40 else "#3b82f6"
            st.markdown(f"""
                <div style="border-top:5px solid {risk_c}; padding:15px; background:white; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:15px; min-height:300px;">
                    <h4 style="margin:0;">{r['name']} <small>({r['admin']}반)</small></h4>
                    <p style="font-size:0.85em; color:#666;"><b>진행:</b> {r['stage']}</p>
                    <hr>
                    <p style="font-size:0.82em; line-height:1.5; color:#333;">{r['advice']}</p>
                    <div style="background:#f8fafc; padding:8px; border-radius:5px; margin-top:10px;">
                        <p style="font-size:0.75em; color:#475569; margin:0;"><b>💡 추가 정보:</b></p>
                        <p style="font-size:0.75em; color:#1e293b; margin:0;">{', '.join(r['missing']) if r['missing'] else '분석 데이터 충분'}</p>
                    </div>
                    <div style="text-align:right; font-weight:bold; color:{risk_c}; margin-top:10px;">위기 지수: {int(r['risk'])}점</div>
                </div>
            """, unsafe_allow_html=True)
