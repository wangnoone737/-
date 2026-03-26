import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# 1. 페이지 설정
st.set_page_config(page_title="Strategic Relationship Simulator", page_icon="🛡️", layout="wide")

# 2. 분석 엔진
class IntegratedEngine:
    STAGE_MAP = {
        1: "마음사기", 2: "수강 목적성 심기", 3: "영 인지", 4: "성경 인정",
        5: "선악구분", 6: "시대구분", 7: "말씀 인정", 8: "종교 세계 인식",
        9: "약속의 목자 인정", 10: "약속한 성전 인정"
    }

    @staticmethod
    def analyze_student(row, admin_info, situation):
        # 다양한 컬럼명 대응 (이름, 성명 등)
        name = str(row.get('이름', row.get('성명', '알 수 없음'))).strip()
        mbti = str(row.get('MBTI', '')).upper().strip()
        raw_step = str(row.get('단계', '')).strip()
        feedback = str(row.get('피드백', ''))
        
        if not mbti or mbti in ['NAN', ''] or not raw_step or raw_step in ['NAN', '']:
            return None, "⚠️ 정보 입력 필요", f"{name}님: 분석에 필요한 핵심 데이터가 부족합니다."

        try:
            step_num = int(re.findall(r'\d+', raw_step)[0])
            step_level = "상" if "상" in raw_step else "중" if "중" in raw_step else "하"
        except:
            return None, "⚠️ 단계 형식 오류", "단계 열에 '4상', '1중' 형태로 입력해주세요."

        base_score = 55 + (step_num * 2)
        if step_level == "하": base_score += 15
        elif step_level == "상": base_score -= 10

        neg_keywords = ['의심', '비판', '유튜브', '반대', '가족', '졸음', '힘듦']
        for word in neg_keywords:
            if word in feedback: base_score += 12

        match_benefit = 0
        a_mbti = admin_info.get('mbti', '모름')
        if a_mbti != "모름" and len(mbti) == 4:
            if mbti[2] == a_mbti[2]: match_benefit += 15
            if mbti[0] != a_mbti[0]: match_benefit += 5
        
        final_risk = base_score - match_benefit
        stage_name = IntegratedEngine.STAGE_MAP.get(step_num, "미정의 단계")
        
        advice = f"현재 {stage_name}({step_level}) 단계입니다. "
        advice += "관계를 재정립하세요." if step_level == "하" else "안정적 관리가 필요합니다."

        return min(max(final_risk, 0), 100), f"{stage_name} ({step_level})", advice

# 3. 사이드바 구성
with st.sidebar:
    st.header("📂 데이터 설정")
    st.subheader("1. 공통 데이터")
    common_file = st.file_uploader("전체 출석부", type=["xlsx", "csv"], key="common")
    
    st.markdown("---")
    admins = []
    mbti_list = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", 
                 "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    
    for label in ["A", "B", "C"]:
        with st.expander(f"👤 전도사 {label} 설정"):
            file = st.file_uploader(f"{label}반 파일", type=["xlsx", "csv"], key=f"f_{label}")
            mbti = st.selectbox(f"{label} MBTI", mbti_list, key=f"m_{label}")
            admins.append({'label': label, 'file': file, 'mbti': mbti})

# 4. 메인 화면
st.title("🏛️ 전도사-수강생 관계 시뮬레이터")
col_inp, col_chart = st.columns([1, 1.2])

with col_inp:
    situation = st.text_area("🌐 상황", placeholder="예: 비판 유튜브 노출", height=100)
    run_btn = st.button("시뮬레이션 가동 🚀", use_container_width=True)

# 5. 실행 로직 (KeyError 및 SyntaxError 완전 해결)
if run_btn:
    raw_list = []
    for admin in admins:
        if admin['file'] is not None:
            try:
                ext = admin['file'].name.split('.')[-1]
                df = pd.read_excel(admin['file']) if ext == 'xlsx' else pd.read_csv(admin['file'])
                
                # '이름' 혹은 '성명' 컬럼 존재 여부 확인
                name_col = next((c for c in df.columns if c in ['이름', '성명']), None)
                
                for _, row in df.iterrows():
                    d = row.to_dict()
                    d['_target_name'] = d.get(name_col, '알수없음') # 중복 제거용 고유키
                    d['담당전도사'] = admin['label']
                    d['admin_info'] = admin
                    raw_list.append(d)
            except Exception as e:
                st.error(f"파일 처리 오류: {e}")

    if raw_list:
        # 91명 중복 문제 해결: 고유 이름 기준
        df_final = pd.DataFrame(raw_list).drop_duplicates(subset=['_target_name'], keep='first')
        
        processed = []
        for _, row in df_final.iterrows():
            risk, stage, advice = IntegratedEngine.analyze_student(row, row['admin_info'], situation)
            processed.append({'name': row['_target_name'], 'admin': row['담당전도사'], 'risk': risk, 'stage': stage, 'advice': advice})

        with col_chart:
            valid_risks = [p['risk'] for p in processed if p['risk'] is not None]
            if valid_risks:
                avg = 100 - (sum(valid_risks) / len(valid_risks))
                fig = go.Figure(go.Indicator(
                    mode="gauge+number", value=avg,
                    title={'text': f"🛡️ 전체 {len(processed)}명 안전도"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#22c55e"}}
                ))
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        cols = st.columns(3)
        for i, res in enumerate(processed):
            with cols[i % 3]:
                r_val = res['risk']
                color = "#ef4444" if r_val and r_val > 70 else "#3b82f6"
                st.markdown(f"""
                    <div style="border-top:5px solid {color}; padding:15px; background:white; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:15px;">
                        <h4>{res['name']} <small>(담당: {res['admin']})</small></h4>
                        <p style="font-size:0.8em;"><b>지표:</b> {res['stage']}</p>
                        <p style="font-size:0.8em; color:#666;">{res['advice']}</p>
                        <div style="text-align:right; font-weight:bold; color:{color};">위기: {r_val if r_val else '-'}점</div>
                    </div>
                """, unsafe_allow_html=True)
