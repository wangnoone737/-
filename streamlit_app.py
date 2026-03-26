import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import os
from openpyxl import load_workbook

# 1. 페이지 설정
st.set_page_config(page_title="AI Strategy Master v6.3", page_icon="📡", layout="wide")

# 2. 분석 엔진 (영상 분석 + 계층 데이터)
class AdvancedEngineV63:
    STAGE_MAP = {i: name for i, name in enumerate(["", "마음사기", "수강 목적성 심기", "영 인지", "성경 인정", "선악구분", "시대구분", "말씀 인정", "종교 세계 인식", "약속의 목자 인정", "약속한 성전 인정"])}

    @staticmethod
    def analyze_video_content(url):
        """[고도화] 영상 링크의 자막/음성 키워드 가상 분석 (실제 연동 시 API 활용)"""
        risk_keywords = ['비방', '이단', '탈퇴', '폭로', '반대', '인터넷', '조심']
        found_keywords = [kw for kw in risk_keywords if kw in url] # URL 및 메타데이터 모사 분석
        return 20 if found_keywords else 0

    @staticmethod
    def parse_hierarchical_data(file_path, sheet_name):
        """병합 셀 및 홀/짝 열 기반 계층 분석"""
        try:
            wb = load_workbook(file_path, data_only=True)
            ws = wb[sheet_name]
            data_map = {}
            for r in range(1, min(ws.max_row + 1, 100)):
                for c in range(1, ws.max_column + 1, 2):
                    lbl = ws.cell(row=r, column=c).value
                    val = ws.cell(row=r, column=c+1).value
                    if lbl and val:
                        data_map[str(lbl).strip()] = str(val).strip()
            return data_map
        except: return {}

    @staticmethod
    def run_simulation(s_data, admin, sit, strat, video_risk):
        full_text = " ".join([f"{k}:{v}" for k, v in s_data.items()])
        
        # MBTI 및 단계 추출
        mbtis = ["ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
        found_mbti = next((m for m in mbtis if m in full_text.upper()), "모름")
        step_n = int(re.search(r'(\d+)', full_text).group(1)) if re.search(r'(\d+)', full_text) else 0
        
        # 위기 지수 산출 (영상 분석 가중치 포함)
        ctx_v = 15 if any(b in full_text for b in ['의심', '불안', '핍박']) else -5
        match_b = 7 if found_mbti != "모름" and admin['mbti'] != "모름" and found_mbti[2] == admin['mbti'][2] else 0
        
        # 전략 보너스 (NameError 수정 완료)
        strat_bonus = 0
        if found_mbti != "모름":
            if 'T' in found_mbti and any(w in strat for w in ['논리', '팩트', '근거']): strat_bonus = 15
            elif 'F' in found_mbti and any(w in strat for w in ['공감', '위로', '경청']): strat_bonus = 15

        final_risk = min(max(55 + (step_n * 2) + video_risk + ctx_v - match_b - strat_bonus, 0), 100)
        advice = f"[{admin['id']}전도사 상성 분석] {found_mbti} 성향이며 "
        advice += "영상 분석 결과 주의가 필요합니다." if video_risk > 0 else "전략적 소통이 주효합니다."
        
        return final_risk, AdvancedEngineV63.STAGE_MAP.get(step_n, "확인중"), advice

# 3. 사이드바 (입력란 누적 검토 완료)
with st.sidebar:
    st.header("⚙️ 통합 설정 v6.3")
    common_file = st.file_uploader("📂 전체 출석부 업로드", type=["xlsx"], key="main_x")
    st.markdown("---")
    
    m_list = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    e_list = ["모름"] + [f"{i}번" for i in range(1, 10)]
    admins_cfg = []
    for tag in ["A", "B", "C"]:
        with st.expander(f"👤 {tag}전도사 상세 프로필"):
            f_up = st.file_uploader(f"{tag}반 파일", type=["xlsx"], key=f"f_{tag}")
            c1, c2 = st.columns(2)
            with c1:
                m_sel = st.selectbox("MBTI", m_list, key=f"m_{tag}")
                g_sel = st.radio("성별", ["남", "여", "모름"], index=2, key=f"g_{tag}")
            with c2:
                e_sel = st.selectbox("애니어그램", e_list, key=f"e_{tag}")
            admins_cfg.append({'id': tag, 'file': f_up, 'mbti': m_sel, 'ennea': e_sel, 'gender': g_sel})

# 4. 메인 화면
st.title("🏛️ 전략 시뮬레이션 시스템 v6.3")
col_l, col_r = st.columns([1, 1.2])

with col_l:
    st.subheader("🎯 데이터 분석 및 시나리오")
    sit_in = st.text_area("🌐 발생 상황 (유튜브 링크 등 포함)", height=100)
    strat_in = st.text_area("🛡️ 대응 전략", height=100)
    
    if st.button("정밀 시뮬레이션 가동 🚀", use_container_width=True):
        active_admins = [a for a in admins_cfg if a['file']]
        if not active_admins:
            st.error("전도사별 파일을 업로드해주세요.")
        else:
            # 영상 정보 분석 실행
            video_risk_score = AdvancedEngineV63.analyze_video_content(sit_in)
            
            results = []
            msg = st.empty()
            p_bar = st.progress(0)
            
            for i, adm in enumerate(active_admins):
                tmp_fn = f"temp_v63_{adm['id']}.xlsx"
                with open(tmp_fn, "wb") as f: f.write(adm['file'].getbuffer())
                
                xl = pd.ExcelFile(tmp_fn)
                for s_idx, s_name in enumerate(xl.sheet_names):
                    # 이름 필터링 강화
                    pure_name = re.sub(r'[^가-힣]', '', s_name)
                    if pure_name in ['단계', '출석부', '양식', '기본'] or len(pure_name) < 2: continue
                    
                    msg.info(f"⏳ {adm['id']}전도사 - {pure_name} 분석 중...")
                    p_bar.progress((i / len(active_admins)) + (s_idx / (len(xl.sheet_names) * len(active_admins))))
                    
                    s_info = AdvancedEngineV63.parse_hierarchical_data(tmp_fn, s_name)
                    risk, stage, advice = AdvancedEngineV63.run_simulation(s_info, adm, sit_in, strat_in, video_risk_score)
                    results.append({'name': pure_name, 'admin': adm['id'], 'risk': risk, 'stage': stage, 'advice': advice})
                
                if os.path.exists(tmp_fn): os.remove(tmp_fn)
            
            p_bar.progress(1.0)
            msg.success("✅ 영상 및 시트 분석 완료!")
            st.session_state['v63_res'] = results

# 5. 결과 대시보드
if 'v63_res' in st.session_state and st.session_state['v63_res']:
    res_df = pd.DataFrame(st.session_state['v63_res']).drop_duplicates(subset=['name'])
    with col_r:
        st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=100-res_df['risk'].mean(), title={'text': "🛡️ 통합 안전 점수"})), use_container_width=True)

    grid = st.columns(3)
    for idx, r in enumerate(res_df.to_dict('records')):
        with grid[idx % 3]:
            risk_c = "#ef4444" if r['risk'] > 70 else "#3b82f6"
            st.markdown(f"""
                <div style="border-top:5px solid {risk_c}; padding:15px; background:white; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:15px; min-height:280px;">
                    <h4 style="margin:0;">{r['name']} <small>({r['admin']}반)</small></h4>
                    <p style="font-size:0.85em;"><b>과정:</b> {r['stage']}</p>
                    <hr><p style="font-size:0.82em; color:#333;">{r['advice']}</p>
                    <div style="text-align:right; font-weight:bold; color:{risk_c}; margin-top:10px;">위기 지수: {int(r['risk'])}점</div>
                </div>
            """, unsafe_allow_html=True)
