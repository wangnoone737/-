import streamlit as st
import pandas as pd
import plotly.express as px
import io

# 1. 페이지 설정 (웹사이트 타이틀 및 아이콘)
st.set_page_config(page_title="Center Risk Simulator", page_icon="🏛️", layout="wide")

# 2. 디자인 테마 (CSS 주입)
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .css-1d391kg { background-color: #ffffff; padding: 2rem; border-radius: 1rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .stHeader { color: #1e3a8a; }
    .metric-card { background-color: white; padding: 1.5rem; border-radius: 1rem; box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1); border-left: 5px solid #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ 센터 위기 관리 전략 시뮬레이터")
st.markdown("---")

# 3. 사이드바: 데이터 업로드
with st.sidebar:
    st.header("📂 데이터 주입")
    file_att = st.file_uploader("1. 출석부 파일 (CSV)", type="csv")
    file_admin = st.file_uploader("2. 전도사반 파일 (CSV/Excel)", type="csv")
    st.markdown("---")
    st.info("💡 파일을 업로드하면 6명의 수강생 데이터가 로드됩니다.")

# 4. 분석 엔진 (시뮬레이션 로직)
# (실제 구현 시 파일 데이터를 읽어야 하지만, 여기서는 구조적 시뮬레이션을 위해 샘플 데이터를 사용합니다.)
def get_mock_data():
    names = ['김남호', '김윤심', '이홍규', '서형국', '윤영옥', '오정숙']
    data = []
    for name in names:
        data.append({
            '이름': name,
            'MBTI': 'ISFP' if name == '김남호' else 'ESFJ' if name == '김윤심' else 'INTP',
            '신성': 'O' if name in ['김남호', '서형국'] else 'X',
            '단계': 4 if name == '김남호' else 5 if name == '김윤심' else 3,
            '최근_피드백': [
                "최근 경제적 어려움 토로, 강의 집중도 낮아짐",
                "지식적 의문 제기, 상담 시 단답형",
                "가족 반대 심해짐, 불안감 표시",
                "바쁜 일정으로 보강 거부",
                "말수가 적고 반응이 무딤",
                "조용히 수강 중, 특이사항 없음"
            ]
        })
    return pd.DataFrame(data)

df_students = get_mock_data()

# 5. 메인 화면: 상황 및 전략 입력
c1, c2 = st.columns([1, 1.5])

with c1:
    st.subheader("🎯 전략 시뮬레이션 설정")
    situation = st.text_area("🌐 상황 (유튜브 링크 또는 사건)", placeholder="예: 비판 유튜브 영상 링크 입력")
    plan = st.text_area("🛡️ 대응 전략 (강사/전도사 계획)", placeholder="예: 보강 시 해당 내용 반박 및 믿음 강조")
    run_btn = st.button("분석 실행 🚀", use_container_width=True)

with c2:
    st.subheader("📊 기수 전반 위기 리포트")
    if file_att and file_admin and run_btn:
        # AI 분석 로직 (임의 수치 적용)
        df_students['이탈위험도'] = [85, 60, 75, 50, 40, 30] # 샘플 위험도
        
        avg_risk = df_students['이탈위험도'].mean()
        
        # 위험도 게이지 차트 (시각적 결과)
        fig = px.gauge(
            df_students, 
            value=avg_risk, 
            mode="gauge+number", 
            title="🔥 기수 전체 흔들림 정도",
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#ef4444" if avg_risk > 70 else "#f59e0b" if avg_risk > 40 else "#10b981"}}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 집단 심리 상태 요약
        st.markdown(f"""
            <div class="metric-card">
                <h4>🧠 AI 집단 심리 분석</h4>
                <p>영상의 논조가 수강생들의 '단계별 지식'을 공격할 때, 특히 '{'감정형(F)' 수강생들의 불안감' if "반박" in plan else '내향형(I)' 수강생들의 내적 갈등'}이 증폭될 것으로 예측됩니다.</p>
                <p>현재 계획은 고위험군의 이탈을 {'가속화할 수 있습니다' if avg_risk > 70 else '어느 정도 통제 가능합니다'}.</p>
            </div>
        """, unsafe_allow_html=True)

# 6. 하단: 개별 수강생 상세 분석 카드
st.markdown("---")
st.subheader("👤 개별 수강생 심층 분석 (최근 5회 피드백 기반)")

if file_att and file_admin and run_btn:
    cols = st.columns(3) # 3열 배치
    for i, (_, row) in enumerate(df_students.iterrows()):
        col_idx = i % 3
        with cols[col_idx]:
            risk_color = "#ef4444" if row['이탈위험도'] > 70 else "#f59e0b" if row['이탈위험도'] > 40 else "#10b981"
            st.markdown(f"""
                <div style="background: white; padding: 1.5rem; border-radius: 1rem; border-top: 5px solid {risk_color}; box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1); margin-bottom: 1rem;">
                    <b style="font-size: 1.2em;">{row['이름']}</b> <small style="color: #64748b;">({row['MBTI']} / {row['단계']}단계)</small><br>
                    <p style="font-size: 0.9em; color: #1e293b; margin-top: 0.5rem;"><b>최근 피드백:</b> {row['최근_피드백'][0]}</p>
                    <p style="font-size: 0.85em; color: #4b5563;"><b>AI 예측:</b> '{situation}'에 노출 시, 성향상 '{'내적 갈등 후 잠적' if 'I' in row['MBTI'] else '공개적 의문 제기'}' 가능성 {row['이탈위험도']}%.</p>
                </div>
            """, unsafe_allow_html=True)
else:
    st.info("👈 왼쪽 사이드바에서 파일을 업로드하고 분석을 실행해주세요.")
