import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# 1. 페이지 설정
st.set_page_config(page_title="Total Strategic Risk Advisor", page_icon="🛡️", layout="wide")

# 2. 분석 엔진: 단계별 의미 및 성향 매칭 로직
class IntegratedEngine:
    STAGE_MAP = {
        1: "마음사기", 2: "수강 목적성 심기", 3: "영 인지", 4: "성경 인정",
        5: "선악구분", 6: "시대구분", 7: "말씀 인정", 8: "종교 세계 인식",
        9: "약속의 목자 인정", 10: "약속한 성전 인정"
    }

    @staticmethod
    def analyze_student(row, admin_info, situation):
        name = str(row.get('이름', '알 수 없음'))
        mbti = str(row.get('MBTI', '')).upper().strip()
        raw_step = str(row.get('단계', ''))
        feedback = str(row.get('피드백', ''))
        
        # 데이터 누락 체크
        if not mbti or mbti in ['NAN', ''] or not raw_step or raw_step in ['NAN', '']:
            return None, "⚠️ 정보 입력 필요", f"{name}님: MBTI 혹은 단계(예: 4상) 데이터가 없습니다."

        # 단계 파싱 (예: "4상" -> 4단계, 상)
        try:
            step_num = int(re.findall(r'\d+', raw_step)[0])
            step_level = "상" if "상" in raw_step else "중" if "중" in raw_step else "하"
        except:
            return None, "⚠️ 단계 형식 오류", "단계 열에 '4상', '1중' 형태로 입력해주세요."

        # 위기 지수 계산
        base_score = 55
        # 1. 단계별 영향 (고단계일수록 외부 충격에 민감, 하 수준일수록 불안정)
        base_score += (step_num * 2)
        if step_level == "하": base_score += 15
        elif step_level == "상": base_score -= 10

        # 2. 텍스트 마이닝
        neg_keywords = ['의심', '비판', '유튜브', '반대', '가족', '졸음', '힘듦']
        for word in neg_keywords:
            if word in feedback: base_score += 12

        # 3. 전도사 매칭 (성향 궁합)
        match_benefit = 0
        a_mbti = admin_info.get('mbti', '모름')
        if a_mbti != "모름" and len(mbti) == 4:
            if mbti[2] == a_mbti[2]: match_benefit += 15 # T-T / F-F 공감
            if mbti[0] != a_mbti[0]: match_benefit += 5  # E-I 보안
        
        final_risk = base_score - match_benefit
        
        # 대응 제언
        stage_name = IntegratedEngine.STAGE_MAP.get(step_num, "미정의 단계")
        if step_level == "하":
            advice = f"현재 {stage_name} 단계의 수용도가 낮습니다. 전도사님의 {admin_info['mbti']} 성향을 살린 밀착 케어가 필요합니다."
        else:
            advice = f"{stage_name} 인지가 안정적입니다. 현 전략을 유지하되 {mbti} 특성에 맞춘 피드백을 강화하세요."

        return min(max(final_risk, 0), 100), f"{stage_name} ({step_level})", advice

# 3. 사이드바: 모든 입력란 복구
with st.sidebar:
    st.header("📂 데이터 및 관리자 설정")
    
    # 공통 출석부
    st.subheader("1. 공통 데이터")
    common_file = st.file_uploader("전체 출석부 업로드", type=["xlsx", "csv"], key="common")
    
    st.markdown("---")
    
    # 전도사별 섹션 복구 (A, B, C)
    admins = []
    mbti_list = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", 
                 "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    
    for label in ["A", "B", "C"]:
        with st.expander(f"👤 전도사 {label} 관리 섹션", expanded=False):
            # 파일 업로드 칸 복구
            admin_file = st.file_uploader(f"{label}반 수강생 파일", type=["xlsx", "csv"], key=f"file_{label}")
            
            # 개인정보 입력란 복구 (성별 포함)
            a_mbti = st.selectbox(f"{label} MBTI", mbti_list, key=f"mbti_{label}")
            a_ennea = st.selectbox(f"{label} 애니어그램", ["모름"] + [str(i) for i in range(1, 10)], key=f"en_{label}")
            a_gender = st.radio(f"{label} 성별", ["모름", "남", "여"], key=f"gen_{label}")
            a_blood = st.selectbox(f"{label} 혈액형", ["모름", "A", "B", "O", "AB"], key=f"bl_{label}")
            
            admins.append({
                'label': label, 'file': admin_file, 'mbti': a_mbti, 
                'ennea': a_ennea, 'gender': a_gender, 'blood': a_blood
            })

# 4. 메인 화면 구성
st.title("🏛️ 전도사-수강생 관계 역동 시뮬레이터")

col_inp, col_chart = st.columns([1, 1.2])

with col_inp:
    st.subheader("🎯 전략 시나리오")
    situation = st.text_area("🌐 발생 상황", placeholder="예: 7단계 진행 중 비판 유튜브 노출", height=100)
    strategy = st.text_area("🛡️ 대응 계획", placeholder="예: 전도사 중심의 1:1 감성 소통 및 말씀 재확인", height=100)
    run_btn = st.button("정밀 시뮬레이션 시작 🚀", use_container_width=True)

# 5. 실행 로직
if run_btn:
    final_students = []
    
    for admin in admins:
        if admin['file'] is not None:
            try:
                # 파일 읽기
                ext = admin['file'].name.split('.')[-1]
                df = pd.read_excel(admin['file']) if ext == 'xlsx' else pd.read_csv(admin['file'])
                
                # 수강생별 분석
                for _, row in df.iterrows():
                    risk, stage_info, advice = IntegratedEngine.analyze_student(row, admin, situation)
                    
                    # 영향력 점수 (E형/4단 이상)
                    mbti_val = str(row.get('MBTI', '')).upper()
                    raw_step = str(row.get('단계', '0'))
                    step_num = int(re.findall(r'\d+', raw_step)[0]) if re.findall(r'\d+', raw_step) else 0
                    inf_power = "⭐ 고영향력" if 'E' in mbti_val and step_num >= 4 else ""
                    
                    final_students.append({
                        'name': row.get('이름', '미상'),
                        'mbti': mbti_val,
                        'admin': admin['label'],
                        'risk': risk,
                        'stage': stage_info,
                        'advice': advice,
                        'inf': inf_power,
                        'feedback': str(row.get('피드백', ''))
                    })
            except Exception as e:
                st.error(f"전도사 {admin['label']} 파일 처리 중 오류: {e}")

    if final_students:
        # 상단 차트 표시
        with col_chart:
            valid_risks = [s['risk'] for s in final_students if s['risk'] is not None]
            if valid_risks:
                avg_safety = 100 - (sum(valid_risks) / len(valid_risks))
                fig = go.Figure(go.Indicator(
                    mode="gauge+number", value=avg_safety,
                    title={'text': "🛡️ 전체 기수 예상 안전도"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#22c55e"}}
                ))
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)

        # 결과 카드 섹션
        st.markdown("---")
        st.subheader("👤 수강생별 정밀 진단 결과")
        cols = st.columns(3)
        
        for i, res in enumerate(final_students):
            with cols[i % 3]:
                if res['risk'] is None:
                    st.warning(f"### {res['name']}\n{res['stage']}\n{res['advice']}")
                else:
                    risk_val = res['risk']
                    card_color = "#ef4444" if risk_val > 70 else "#f59e0b" if risk_val > 40 else "#3b82f6"
                    st.markdown(f"""
                        <div style="background:white; border-top:6px solid {card_color}; padding:15px; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:15px; min-height:300px;">
                            <h3 style="margin:0;">{res['name']} <small style="font-size:0.6em; color:gray;">(담당: {res['admin']})</small></h3>
                            <p style="color:orange; font-size:0.8em; font-weight:bold; margin:5px 0;">{res['inf']}</p>
                            <p style="font-size:0.85em;"><b>성향:</b> {res['mbti']} | <b>단계:</b> {res['stage']}</p>
                            <hr>
                            <p style="font-size:0.85em; color:#555;"><b>📋 피드백 요약:</b> {res['feedback'][:40]}...</p>
                            <div style="background:#f8fafc; padding:10px; border-radius:8px; margin-top:10px; font-size:0.85em; border-left:3px solid {card_color};">
                                <b>💡 AI 대응 조언:</b><br>{res['advice']}
                            </div>
                            <div style="text-align:right; font-weight:bold; color:{card_color}; margin-top:15px; font-size:1.1em;">예상 위기 지수: {risk_val}점</div>
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("사이드바에서 전도사별 파일을 업로드하고 '시뮬레이션 가동' 버튼을 눌러주세요.")
