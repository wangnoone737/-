import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import os
from openpyxl import load_workbook

# 1. 페이지 설정
st.set_page_config(page_title="AI Strategy Master v6.1", page_icon="⚖️", layout="wide")

# 2. 분석 엔진
class FinalEngine:
    STAGE_MAP = {i: name for i, name in enumerate(["", "마음사기", "수강 목적성 심기", "영 인지", "성경 인정", "선악구분", "시대구분", "말씀 인정", "종교 세계 인식", "약속의 목자 인정", "약속한 성전 인정"])}

    @staticmethod
    def parse_sheet_structure(file_path, sheet_name):
        """병합 셀 및 열 위계 분석 (v6.1 최적화)"""
        try:
            wb = load_workbook(file_path, data_only=True)
            ws = wb[sheet_name]
            extracted = {}
            # 최대 80행까지 스캔하여 속도 향상
            for row in range(1, min(ws.max_row + 1, 80)):
                for col in range(1, ws.max_column + 1, 2):
                    item = ws.cell(row=row, column=col).value
                    content = ws.cell(row=row, column=col+1).value
                    if item and content:
                        extracted[str(item).strip()] = str(content).strip()
            return extracted
        except:
            return {}

    @staticmethod
    def analyze_matching(student_data, admin_info, situation, strategy):
        context = " ".join([f"{k}:{v}" for k, v in student_data.items()])
        
        # MBTI 및 단계 추출
        s_mbti = ""
        for m in ["ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]:
            if m in context.upper(): s_mbti = m; break
        
        step_m = re.search(r'(\d+)', context)
        step_num = int(step_m.group(1)) if step_m else 0
        
        # 데이터 결손 체크
        missing = []
        if not s_mbti: missing.append("MBTI")
        if step_num == 0: missing.append("수강 단계")
        if not any(kw in context for kw in ['고민', '상황', '환경']): missing.append("배경 정보")

        # 지수 계산
        yt_risk = 15 if any(kw in situation for kw in ["youtube.com", "youtu.be"]) else 0
        ctx_risk = 10 if any(kw in context for kw in ['의심', '불안', '인터넷', '핍박']) else -5
        
        # 관리자-수강생 상성 (T/F 일치 여부)
        match_bonus = 0
        if s_mbti and admin_info['mbti'] != "모름":
            if s_mbti[2] == admin_info['mbti'][2]: match_bonus = 7
        
        bonus = 0
        if s_mbti:
            if 'T' in s_mbti and any(w in strategy for w in ['논리', '설명', '근거']): bonus = 12
            if 'F' in s_mbti and any(w in strategy for w in ['공감', '위로', '경청']): bonus = 12

        risk = min(max(55 + (step_num * 2) + yt_risk + ctx_risk - match_bonus - bonus, 0), 100)
        advice = f"[{admin_info['id']}전도사(MBTI:{admin_info['mbti']})] 매칭 분석 결과: "
        advice += f"{s_mbti} 성향에 맞춘 전략적 접근이 필요합니다."
        
        return risk, FinalEngine.STAGE_MAP.get(step_num, "정보 확인중"), advice, missing

# 3. 사이드바 설정 (전도사 정보 입력 복구)
with st.sidebar:
    st.header("⚙️ 분석 설정 v6.1")
    mbti_opts = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    ennea_opts = ["모름"] + [f"{i}번" for i in range(1, 10)]
    
    admins = []
    for label in ["A", "B", "C"]:
        with st.expander(f"👤 전도사 {label} 프로필"):
            f = st.file_uploader(f"{label}반 데이터", type=["xlsx"], key=f"f_{label}")
            c1, c2 = st.columns(2)
            with c1:
                m = st.selectbox(f"MBTI", mbti_opts, key=f"m_{label}")
                g = st.radio(f"성별", ["남", "여", "모름"], index=2, key=f"g_{label}")
            with c2:
                e = st.selectbox(f"애니어그램", ennea_opts, key=f"e_{label}")
            admins.append({'id': label, 'file': f, 'mbti': m, 'ennea': e, 'gender': g})

# 4. 메인 화면
st.title("🏛️ 전략 시뮬레이션 시스템 v6.1")
col_inp, col_chart = st.columns([1, 1.2])

with col_inp:
    st.subheader("🎯 시나리오 입력")
    sit = st.text_area("🌐 발생 상황", height=80)
    strat = st.text_area("🛡️ 대응 전략", height=80)
    run_btn = st.button("AI 정밀 분석 가동 🚀", use_container_width=True)

if run_btn:
    results = []
    status = st.empty()
    prog = st.progress(0)
    
    active = [a for a in admins if a['file']]
    
    for a_idx, admin in enumerate(active):
        path = f"temp_{admin['id']}.xlsx"
        with open(path, "wb") as tmp: tmp.write(admin['file'].getbuffer())
        
        xl = pd.ExcelFile(path)
        # 구문 오류 해결 지점: 괄호 및 루프 구조 확인
        for s_idx, sheet in enumerate(xl.sheet_names):
            status.info(f"⏳ {admin['id']}전도사 - {sheet} 시트 분석 중...")
            prog.progress((a_idx / len(active)) + (s_idx / (len(xl.sheet_names) * len(active))))
            
            # 구조 분석 및 이름 추출
            data = FinalEngine.parse_sheet_structure(path, sheet)
            name = re.sub(r'[^가-힣]', '', sheet)
            
            if name and len(name) >= 2 and name != '단계':
                risk, stage, advice, missing = FinalEngine.analyze_matching(data, admin, sit, strat)
                results.append({'name': name, 'admin': admin['id'], 'risk': risk, 'stage': stage, 'advice': advice, 'missing': missing})
        
        if os.path.exists(path): os.remove(path)

    prog.progress(1.0)
    status.success("✅ 분석 완료!")

    if results:
        df_res = pd.DataFrame(results).drop_duplicates(subset=['name'])
        with col_chart:
            avg_v = 100 - df_res['risk'].mean()
            st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=avg_v, title={'text': "🛡️ 전체 안전도"})), use_container_width=True)

        st.markdown("---")
        cols = st.columns(3)
        for i, r in enumerate(df_res.to_dict('records')):
            with cols[i % 3]:
                c_code = "#ef4444" if r['risk'] > 70 else "#3b82f6"
                st.markdown(f"""
                    <div style="border-top:5px solid {c_code}; padding:15px; background:white; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:15px; min-height:280px;">
                        <h4 style="margin:0;">{r['name']} <small>({r['admin']}반)</small></h4>
                        <p style="font-size:0.85em;"><b>단계:</b> {r['stage']}</p>
                        <hr><p style="font-size:0.82em;">{r['advice']}</p>
                        <div style="background:#f8fafc; padding:8px; border-radius:5px; margin-top:10px;">
                            <p style="font-size:0.72em; color:#475569; margin:0;">💡 <b>가이드:</b> {', '.join(r['missing']) if r['missing'] else '정보 충분'}</p>
                        </div>
                        <div style="text-align:right; font-weight:bold; color:{c_code}; margin-top:10px;">위기: {int(r['risk'])}점</div>
                    </div>
                """, unsafe_allow_html=True)
