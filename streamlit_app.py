import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="AI Strategic Advisor Pro", page_icon="🧠", layout="wide")

# 2. 분석 엔진 클래스
class StrategicEngine:
    @staticmethod
    def text_mining_sentiment(text):
        """피드백 텍스트 마이닝: 키워드 기반 감성 분석"""
        negative_words = ['피곤', '졸음', '의심', '가족', '바쁨', '힘듦', '갈등', '부정', '반대']
        positive_words = ['은혜', '열정', '감사', '확신', '기쁨', '성장', '집중']
        
        score = 0
        for word in negative_words:
            if word in str(text): score += 15
        for word in positive_words:
            if word in str(text): score -= 10
        return score

    @staticmethod
    def calculate_match(student, admin):
        """수강생-전도사 매칭 궁합 분석"""
        match_score = 0
        s_mbti = str(student.get('MBTI', '')).upper()
        a_mbti = str(admin.get('mbti', '')).upper()
        
        # 성격 보완성 체크 (E-I 보완 또는 T-F 보완 등)
        if s_mbti and a_mbti:
            if s_mbti[0] != a_mbti[0]: match_score += 10 # 외향-내향 보완
            if s_mbti[2] == a_mbti[2]: match_score += 15 # 사고-사고 혹은 감정-감정 공감
            
        # 애니어그램 기반 궁합 (단순 예시 로직)
        if student.get('애니어그램') == admin.get('ennea'): match_score += 20
            
        return match_score

# 3. 사이드바: 전도사 역량 입력 (2번 요청사항)
with st.sidebar:
    st.header("👤 전도사(관리자) 역량 설정")
    admin_data = {}
    cols_a = st.columns(2)
    with cols_a[0]:
        admin_data['mbti'] = st.selectbox("전도사 MBTI", ["ISTJ", "ENFP", "ENTJ", "ISFJ", "INFJ", "ESTP", "기타"])
        admin_data['ennea'] = st.number_input("전도사 애니어그램", 1, 9, 1)
    with cols_a[1]:
        admin_data['gender'] = st.radio("성별", ["남", "여"])
        admin_data['blood'] = st.selectbox("혈액형", ["A", "B", "O", "AB"])
    
    st.markdown("---")
    st.header("📂 데이터 주입")
    file_att = st.file_uploader("수강생 데이터(Excel)", type=["xlsx"])

# 4. 메인 화면 및 전략 입력
st.title("🏛️ AI 전략 시뮬레이션 : 관계 역동 모델")

c1, c2 = st.columns([1, 1.5])
with c1:
    st.subheader("🎯 상황 및 대응 전략")
    situation = st.text_area("🌐 발생 상황", height=100)
    plan = st.text_area("🛡️ 대응 계획", height=100)
    run_btn = st.button("전략 시뮬레이션 가동 🚀", use_container_width=True)

# 5. 분석 실행 로직
if run_btn and file_att:
    df = pd.read_excel(file_att)
    
    # [1] 피드백 텍스트 마이닝 적용
    df['sentiment_risk'] = df['피드백'].apply(StrategicEngine.text_mining_sentiment)
    
    # [2] 전도사 매칭 점수 산출
    df['match_score'] = df.apply(lambda x: StrategicEngine.calculate_match(x, admin_data), axis=1)
    
    # [3] 위기 전이 지수 산출 (영향력 모델)
    # E형이면서 고단계인 사람을 인플루언서로 가정
    df['influencer'] = df.apply(lambda x: 1.5 if 'E' in str(x['MBTI']) and x['단계'] >= 4 else 1.0, axis=1)
    
    # 최종 위기 점수 계산
    def finalize_score(row):
        score = 50 + row['sentiment_risk'] - (row['match_score'] * 0.5)
        if "비판" in situation and row['단계'] >= 4: score += 20
        return min(max(score, 0), 100)

    df['total_risk'] = df.apply(finalize_score, axis=1)
    
    # 전체 리포트 출력
    with c2:
        avg_risk = df['total_risk'].mean()
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = 100 - avg_risk,
            title = {'text': "🛡️ 전략 실행 후 예상 안전도"},
            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#22c55e"}}
        ))
        st.plotly_chart(fig, use_container_width=True)

    # 6. 결과 카드 출력 (상세 제언)
    st.markdown("---")
    st.subheader("👤 수강생별 정밀 시뮬레이션 결과")
    
    cols = st.columns(3)
    for i, (_, row) in enumerate(df.iterrows()):
        risk = row['total_risk']
        match = row['match_score']
        
        with cols[i % 3]:
            # 위험도에 따른 색상
            color = "#ef4444" if risk > 70 else "#3b82f6"
            inf_msg = "⭐ 기수 내 영향력 높음 (흔들릴 시 전염 주의)" if row['influencer'] > 1 else ""
            
            st.markdown(f"""
                <div style="background: white; border-top: 6px solid {color}; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;">
                    <h3 style="margin:0;">{row['이름']} <small style="color:gray;">({row['MBTI']})</small></h3>
                    <p style="color:orange; font-weight:bold; font-size:0.8em;">{inf_msg}</p>
                    <hr>
                    <p><b>🔍 텍스트 분석 결과:</b> 피드백 내 부정 키워드로 인해 위기 가중치 반영됨.</p>
                    <p><b>🤝 전도사 매칭도:</b> {match}점 (성향 궁합에 따른 시너지 분석)</p>
                    <div style="background:#fef2f2; padding:10px; border-radius:8px; margin-top:10px;">
                        <b>💡 AI 전략 제언:</b><br>
                        {row['이름']} 수강생은 현재 {admin_data['mbti']} 전도사님과 { '보완적' if match > 15 else '다소 평이한' } 관계입니다. 
                        전략 실행 시 <b>{'1:1 감성 접근' if 'F' in str(row['MBTI']) else '논리적 자료 제시'}</b>를 병행하십시오.
                    </div>
                    <div style="text-align:right; margin-top:10px; font-weight:bold; color:{color};">최종 위기 지수: {risk}점</div>
                </div>
            """, unsafe_allow_html=True)

elif run_btn:
    st.error("파일을 업로드해주세요.")
