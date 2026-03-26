import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="AI Strategic Advisor Pro", page_icon="🧠", layout="wide")

# 2. 분석 엔진 클래스
class StrategicEngine:
    @staticmethod
    def text_mining_sentiment(text):
        negative_words = ['피곤', '졸음', '의심', '가족', '바쁨', '힘듦', '갈등', '부정', '반대', '유튜브', '공격']
        positive_words = ['은혜', '열정', '감사', '확신', '기쁨', '성장', '집중']
        score = 0
        text_str = str(text)
        for word in negative_words:
            if word in text_str: score += 15
        for word in positive_words:
            if word in text_str: score -= 10
        return score

    @staticmethod
    def calculate_match(student_row, admin_info):
        """수강생-전도사 매칭 궁합 분석 (정보가 '모름'일 경우 중립 처리)"""
        match_score = 0
        s_mbti = str(student_row.get('MBTI', '')).upper()
        a_mbti = str(admin_info.get('mbti', '')).upper()
        
        # MBTI 궁합 (전도사 정보가 있을 때만 계산)
        if a_mbti != "모름" and len(s_mbti) == 4:
            if s_mbti[0] != a_mbti[0]: match_score += 10 # 외향-내향 보완
            if s_mbti[2] == a_mbti[2]: match_score += 15 # 사고-사고/감정-감정 공감
        else:
            match_score += 5 # 정보 부재 시 중립 점수
            
        # 애니어그램 궁합
        s_ennea = str(student_row.get('애니어그램', ''))
        a_ennea = str(admin_info.get('ennea', ''))
        if a_ennea != "모름" and s_ennea == a_ennea:
            match_score += 20
        elif a_ennea == "모름":
            match_score += 5
            
        return match_score

# 3. 사이드바: 파일 업로드 및 전도사 정보 입력 (모름 옵션 포함)
with st.sidebar:
    st.header("📂 데이터 주입 및 관리자 설정")
    
    st.subheader("1. 공통 출석부")
    file_att = st.file_uploader("출석부 파일", type=["csv", "xlsx"], key="att")
    
    st.markdown("---")
    
    # 전도사별 섹션 (A, B, C)
    admins = []
    mbti_options = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", 
                    "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    ennea_options = ["모름"] + [str(i) for i in range(1, 10)]
    blood_options = ["모름", "A", "B", "O", "AB"]

    for label in ["A", "B", "C"]:
        with st.expander(f"👤 전도사 {label} 정보 및 파일", expanded=False):
            file = st.file_uploader(f"전도사 {label}반 파일", type=["csv", "xlsx"], key=f"file_{label}")
            mbti = st.selectbox(f"{label} MBTI", mbti_options, key=f"mbti_{label}")
            ennea = st.selectbox(f"{label} 애니어그램", ennea_options, key=f"ennea_{label}")
            gender = st.radio(f"{label} 성별", ["모름", "남", "여"], key=f"gen_{label}")
            blood = st.selectbox(f"{label} 혈액형", blood_options, key=f"blood_{label}")
            admins.append({'label': label, 'file': file, 'mbti': mbti, 'ennea': ennea, 'gender': gender, 'blood': blood})

# 4. 메인 화면
st.title("🏛️ AI 전략 시뮬레이션 : 관계 역동 모델")

c1, c2 = st.columns([1, 1.5])
with c1:
    st.subheader("🎯 시나리오 설정")
    situation = st.text_area("🌐 발생 상황", placeholder="예: 비판 영상 공유 등", height=100)
    plan = st.text_area("🛡️ 대응 전략", placeholder="예: 개별 면담 및 교육 계획", height=100)
    run_btn = st.button("전략 시뮬레이션 가동 🚀", use_container_width=True)

# 5. 데이터 처리 및 분석
if run_btn:
    all_data = []
    
    for admin in admins:
        if admin['file'] is not None:
            try:
                temp_df = pd.read_excel(admin['file']) if admin['file'].name.endswith('.xlsx') else pd.read_csv(admin['file'])
                for _, row in temp_df.iterrows():
                    student_dict = row.to_dict()
                    student_dict['담당전도사'] = admin['label']
                    
                    sentiment = StrategicEngine.text_mining_sentiment(student_dict.get('피드백', ''))
                    match = StrategicEngine.calculate_match(student_dict, admin)
                    
                    # 영향력 점수 (E형/고단계)
                    mbti_val = str(student_dict.get('MBTI', '')).upper()
                    step_val = student_dict.get('단계', 1)
                    inf_power = 1.5 if 'E' in mbti_val and int(step_val) >= 4 else 1.0
                    
                    # 위기 점수 합산
                    score = 55 + sentiment - (match * 0.4)
                    if "비판" in situation and int(step_val) >= 4: score += 20
                    
                    student_dict['total_risk'] = min(max(score, 0), 100)
                    student_dict['match_score'] = match
                    student_dict['inf_power'] = inf_power
                    all_data.append(student_dict)
            except Exception as e:
                st.error(f"전도사 {admin['label']} 파일 오류: {e}")

    if all_data:
        df = pd.DataFrame(all_data)
        
        with c2:
            avg_safety = 100 - df['total_risk'].mean()
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = avg_safety,
                title = {'text': "🛡️ 예상 기수 안전도"},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#22c55e" if avg_safety > 70 else "#f59e0b"},
                    'steps': [
                        {'range': [0, 40], 'color': "#fee2e2"},
                        {'range': [40, 70], 'color': "#fef3c7"},
                        {'range': [70, 100], 'color': "#dcfce7"}
                    ]
                }
            ))
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("👤 수강생별 정밀 진단")
        cols = st.columns(3)
        for i, row in df.iterrows():
            risk = row['total_risk']
            color = "#ef4444" if risk > 70 else "#f59e0b" if risk > 40 else "#3b82f6"
            inf_mark = "⭐ 영향력 높음" if row['inf_power'] > 1 else ""
            
            with cols[i % 3]:
                st.markdown(f"""
                    <div style="background:white; border-top:6px solid {color}; padding:15px; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:15px; min-height:280px;">
                        <h4 style="margin:0;">{row.get('이름','-')} <small>(담당: {row['담당전도사']})</small></h4>
                        <p style="color:orange; font-size:0.8em; font-weight:bold; margin:5px 0;">{inf_mark}</p>
                        <p style="font-size:0.85em;"><b>성향:</b> {row.get('MBTI','-')} / {row.get('단계','-')}단</p>
                        <hr style="margin:10px 0;">
                        <p style="font-size:0.85em; color:#444;"><b>AI 진단:</b> 
                        피드백 성향 분석 결과 위기 동요도는 <b>{'주의' if risk > 60 else '보통'}</b> 수준입니다.
                        </p>
                        <div style="background:#f8fafc; padding:8px; border-radius:5px; margin-top:10px; font-size:0.8em;">
                            <b>추천 대응:</b> {'밀착 감성 상담' if 'F' in str(row.get('MBTI','')) else '논리적 팩트 체크 및 근거 제시'}
                        </div>
                        <div style="text-align:right; font-weight:bold; color:{color}; margin-top:15px;">위기 지수: {risk}점</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("전도사 반 파일을 업로드하고 버튼을 눌러주세요.")
